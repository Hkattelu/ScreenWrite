"""
RunManager: spawns the pipeline runner child process, tails its JSONL event
file, and derives run state. One run at a time - the pipeline saturates
bandwidth/whisper/Resolve anyway.

State machine:
    running -> succeeded   (result event with success=true, exit observed)
            -> failed      (result event with success=false)
            -> cancelled   (cancel requested, process gone)
            -> crashed     (process gone without a terminal event)
"""

import json
import logging
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .paths import (
    REPO_ROOT, VENV_PYTHON, default_media_dir, new_run_dir, new_run_id, runs_dir,
)

logger = logging.getLogger(__name__)

_CREATE_NO_WINDOW = 0x08000000

# In-memory event cap; disk events.jsonl always has everything.
MAX_EVENTS_IN_MEMORY = 2000


class RunBusyError(Exception):
    """A run is already active."""


class RunValidationError(Exception):
    """The run request is invalid (message is user-facing)."""


@dataclass
class RunState:
    run_id: str
    run_dir: Path
    proc: Optional[subprocess.Popen] = None
    state: str = 'running'
    step: Optional[str] = None
    beat_done: int = 0
    beat_total: int = 0
    started_at: float = field(default_factory=time.time)
    cancel_requested: bool = False
    events: List[dict] = field(default_factory=list)
    result: Optional[dict] = None
    fatal: Optional[dict] = None
    _events_offset: int = 0


class RunManager:
    """Owns the lifecycle of the single active run."""

    def __init__(self, settings):
        self.settings = settings
        self._lock = threading.Lock()
        self._current: Optional[RunState] = None

    # ------------------------------------------------------------------
    # Start
    # ------------------------------------------------------------------

    def start(self, payload: dict) -> str:
        """Validate the request, write run inputs, spawn the runner."""
        with self._lock:
            if self._current and self._is_running_locked():
                raise RunBusyError('A run is already in progress')

            script_text = (payload.get('script_text') or '').strip()
            if not script_text:
                raise RunValidationError('Script is empty')
            vo_path = (payload.get('vo_path') or '').strip() or None
            if vo_path and not Path(vo_path).is_file():
                raise RunValidationError(f'VO audio file not found: {vo_path}')

            defaults = self.settings.get()['defaults']
            run_id = new_run_id()
            run_dir = new_run_dir(run_id)

            script_path = run_dir / 'script.md'
            script_path.write_text(script_text, encoding='utf-8')

            output_path = (payload.get('output_path') or '').strip() \
                or str(run_dir / 'timeline.fcpxml')

            game = (payload.get('game') or '').strip() or None
            # Same keys the CLI passes to VideoOrchestrator (cli.py config dict).
            orchestrator_config = {
                'output_dir': defaults.get('media_dir') or str(default_media_dir()),
                'youtube_enabled': True,
                'pexels_enabled': bool(self.settings.read_key('PEXELS_API_KEY')),
                'resolve_enabled': bool(payload.get('resolve', False)),
                'skip_failed_beats': bool(defaults.get('skip_failed_beats', True)),
                'max_workers': int(defaults.get('max_workers') or 4),
                'enable_asset_cache': True,
                'prefer_stock_for_generic': bool(defaults.get('prefer_stock_for_generic', True)),
                'use_llm_queries': bool(defaults.get('use_llm_queries', True)),
                'game': game,
                'wiki_subdomain': (payload.get('wiki_subdomain') or '').strip() or None,
                'vo_path': vo_path,
                'whisper_model': (payload.get('whisper_model')
                                  or defaults.get('whisper_model') or None),
                'resolve_force_fcpxml': False,
                'verbose': False,
            }
            run_config = {
                'run_id': run_id,
                'repo_root': str(REPO_ROOT),
                'script_path': str(script_path),
                'output_path': output_path,
                'skip_fetch': bool(payload.get('dry_run', False)),
                'orchestrator': orchestrator_config,
            }
            config_path = run_dir / 'run_config.json'
            config_path.write_text(json.dumps(run_config, indent=2), encoding='utf-8')

            proc = self._spawn(config_path)
            self._current = RunState(run_id=run_id, run_dir=run_dir, proc=proc)
            if game:
                # Remember the game for next time (quality-of-life).
                self.settings.put({'defaults': {'last_game': game}})
            logger.info(f'Started run {run_id} (pid {proc.pid})')
            return run_id

    def _spawn(self, config_path: Path) -> subprocess.Popen:
        return subprocess.Popen(
            [str(VENV_PYTHON), '-m', 'desktop.runner', '--config', str(config_path)],
            cwd=str(REPO_ROOT),
            creationflags=_CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # ------------------------------------------------------------------
    # Observe
    # ------------------------------------------------------------------

    def _is_running_locked(self) -> bool:
        run = self._current
        return bool(run and run.state == 'running')

    def is_active(self) -> bool:
        with self._lock:
            self._refresh_locked()
            return self._is_running_locked()

    def snapshot(self, after_seq: int = 0) -> dict:
        """The polling payload: state + events newer than after_seq."""
        with self._lock:
            run = self._current
            if run is None:
                return {'run_id': None, 'state': 'idle', 'events': [], 'last_seq': 0}
            self._refresh_locked()
            new_events = [e for e in run.events if e.get('seq', 0) > after_seq]
            return {
                'run_id': run.run_id,
                'state': run.state,
                'step': run.step,
                'beat_done': run.beat_done,
                'beat_total': run.beat_total,
                'started_at': run.started_at,
                'events': new_events,
                'last_seq': run.events[-1]['seq'] if run.events else 0,
                'fatal': run.fatal,
            }

    def _refresh_locked(self) -> None:
        run = self._current
        if run is None:
            return
        self._pump_events_locked(run)
        if run.state != 'running':
            return
        if run.proc is not None and run.proc.poll() is not None:
            # Process ended: pump once more, then classify.
            self._pump_events_locked(run)
            if run.cancel_requested:
                run.state = 'cancelled'
            elif run.result is not None:
                run.state = 'succeeded' if run.result.get('success') else 'failed'
            elif run.fatal is not None:
                run.state = 'failed'
            else:
                run.state = 'crashed'
                run.fatal = {'error': 'The pipeline process ended unexpectedly',
                             'log_tail': self._log_tail(run)}
            logger.info(f'Run {run.run_id} finished: {run.state}')

    def _pump_events_locked(self, run: RunState) -> None:
        events_path = run.run_dir / 'events.jsonl'
        try:
            with open(events_path, 'r', encoding='utf-8') as handle:
                handle.seek(run._events_offset)
                chunk = handle.read()
                run._events_offset = handle.tell()
        except OSError:
            return

        for line in chunk.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            self._apply_event_locked(run, event)

    def _apply_event_locked(self, run: RunState, event: dict) -> None:
        event_type = event.get('type')
        if event_type == 'step':
            run.step = event.get('step')
        elif event_type == 'beat_progress':
            run.beat_done = int(event.get('done', 0))
            run.beat_total = int(event.get('total', 0))
        elif event_type == 'result':
            run.result = event.get('workflow_result') or {}
        elif event_type == 'fatal':
            run.fatal = {'error': event.get('error'),
                         'traceback': event.get('traceback')}
        run.events.append(event)
        if len(run.events) > MAX_EVENTS_IN_MEMORY:
            del run.events[:len(run.events) - MAX_EVENTS_IN_MEMORY]

    def _log_tail(self, run: RunState, lines: int = 30) -> str:
        try:
            text = (run.run_dir / 'run.log').read_text(encoding='utf-8', errors='replace')
            return '\n'.join(text.splitlines()[-lines:])
        except OSError:
            return ''

    # ------------------------------------------------------------------
    # Cancel / results
    # ------------------------------------------------------------------

    def cancel(self, run_id: Optional[str] = None) -> bool:
        with self._lock:
            run = self._current
            if run is None or (run_id and run.run_id != run_id):
                return False
            run.cancel_requested = True
            if run.proc is not None and run.proc.poll() is None:
                run.proc.terminate()
            return True

    def result(self, run_id: str) -> Optional[dict]:
        with self._lock:
            run = self._current
            if run and run.run_id == run_id:
                self._refresh_locked()
                if run.result is not None:
                    return self._result_payload(run)
        # Fall back to disk (covers app restarts).
        result_path = runs_dir() / run_id / 'result.json'
        try:
            workflow_result = json.loads(result_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return {
            'run_id': run_id,
            'workflow_result': workflow_result,
            'fcpxml_path': workflow_result.get('output_path'),
            'run_dir': str(result_path.parent),
        }

    def _result_payload(self, run: RunState) -> dict:
        return {
            'run_id': run.run_id,
            'workflow_result': run.result,
            'fcpxml_path': (run.result or {}).get('output_path'),
            'run_dir': str(run.run_dir),
        }
