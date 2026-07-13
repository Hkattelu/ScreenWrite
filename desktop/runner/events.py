"""
JSONL event protocol between the pipeline runner (child process) and the
desktop server.

One JSON object per line, appended to events.jsonl and flushed per event so
the server can tail the file live. Progress derives from the pipeline's
existing log messages via PipelineLogHandler - no changes to the core beyond
the structured vo_pacing snapshot in workflow_result.

Event types (all carry "seq" - monotonic from 1 - and "ts" - unix seconds):
    run_started   {run_id, pid, config}          config MUST be pre-redacted
    step          {step, label}                  step transitions (see STEP_PATTERNS)
    beat_progress {done, total}
    log           {level, logger, message}
    result        {success, workflow_result}     terminal
    fatal         {error, traceback}             terminal
"""

import json
import logging
import re
import time
from pathlib import Path


class EventWriter:
    """Appends events to a JSONL file, one flushed line per event."""

    def __init__(self, events_path: Path):
        self._file = open(events_path, 'a', encoding='utf-8')
        self._seq = 0

    def emit(self, event_type: str, **fields) -> None:
        self._seq += 1
        record = {'seq': self._seq, 'ts': time.time(), 'type': event_type}
        record.update(fields)
        self._file.write(json.dumps(record, default=str) + '\n')
        self._file.flush()

    def close(self) -> None:
        try:
            self._file.close()
        except OSError:
            pass


# Step transitions matched against screenwrite.orchestrator INFO messages.
# A drift-guard unit test pins these to the orchestrator source.
STEP_PATTERNS = [
    (re.compile(r'^Step 1: Parsing'), 'parse'),
    (re.compile(r'^Step 1\.5: Conforming'), 'vo_conform'),
    (re.compile(r'^Step 2: (Fetching|Skipping)'), 'fetch'),
    (re.compile(r'^Step 3: Generating'), 'timeline'),
    (re.compile(r'^Step 4: (Building|Skipping)'), 'resolve'),
]

# Per-beat fetch progress from AssetOrchestrator.fetch_game_assets_batch.
PROGRESS_RE = re.compile(r'^Game b-roll progress: (\d+)/(\d+) beats')


class PipelineLogHandler(logging.Handler):
    """
    Converts pipeline log records into structured progress events.

    Attached ONCE to the root logger (screenwrite.* records propagate there,
    so a second attachment would double-emit): screenwrite.* records pass at
    INFO+ (steps, beat progress, creator-facing messages); everything else
    (yt-dlp, huggingface, urllib3...) only at WARNING+ - noise that signals
    real problems.
    """

    def __init__(self, writer: EventWriter):
        super().__init__(level=logging.INFO)
        self.writer = writer

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 - a bad log call must not kill the run
            return

        try:
            if record.name.startswith('screenwrite'):
                for pattern, step in STEP_PATTERNS:
                    if pattern.match(message):
                        self.writer.emit('step', step=step, label=message)
                        return
                progress = PROGRESS_RE.match(message)
                if progress:
                    self.writer.emit(
                        'beat_progress',
                        done=int(progress.group(1)),
                        total=int(progress.group(2)),
                    )
                    return
            elif record.levelno < logging.WARNING:
                return
            self.writer.emit(
                'log',
                level=record.levelname,
                logger=record.name,
                message=message,
            )
        except Exception:  # noqa: BLE001
            pass


def install_handlers(writer: EventWriter, run_log_path: Path) -> list:
    """
    Wire event capture + a full DEBUG file log for the runner process.

    Returns the attached handlers so the caller can detach/close them
    (releases the run.log file handle - Windows can't delete open files).
    """
    root = logging.getLogger()
    pipeline_handler = PipelineLogHandler(writer)
    root.addHandler(pipeline_handler)

    file_handler = logging.FileHandler(run_log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root.addHandler(file_handler)
    if root.level > logging.INFO or root.level == logging.NOTSET:
        root.setLevel(logging.INFO)
    return [pipeline_handler, file_handler]


def remove_handlers(handlers: list) -> None:
    """Detach and close handlers installed by install_handlers."""
    root = logging.getLogger()
    for handler in handlers:
        root.removeHandler(handler)
        try:
            handler.close()
        except Exception:  # noqa: BLE001
            pass
