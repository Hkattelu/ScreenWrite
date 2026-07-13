"""
Tests for the desktop runner's JSONL event protocol and entry point.

No pywebview, no network - the pipeline is monkeypatched where needed.
"""

import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from desktop.runner.events import (
    EventWriter,
    PipelineLogHandler,
    STEP_PATTERNS,
    PROGRESS_RE,
)
from desktop.runner import __main__ as runner_main


def read_events(path: Path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def make_record(logger_name, level, message):
    return logging.LogRecord(logger_name, level, __file__, 1, message, None, None)


class TestEventWriter(unittest.TestCase):
    def test_monotonic_seq_and_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            writer = EventWriter(path)
            writer.emit('run_started', run_id='r1')
            writer.emit('log', message='hello')
            writer.close()

            events = read_events(path)
        self.assertEqual([e['seq'] for e in events], [1, 2])
        self.assertEqual(events[0]['type'], 'run_started')
        self.assertEqual(events[0]['run_id'], 'r1')
        self.assertIn('ts', events[0])

    def test_append_across_writers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            first = EventWriter(path)
            first.emit('log', message='a')
            first.close()
            second = EventWriter(path)
            second.emit('log', message='b')
            second.close()
            self.assertEqual(len(read_events(path)), 2)


class TestPipelineLogHandler(unittest.TestCase):
    def _events_for(self, records):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            writer = EventWriter(path)
            handler = PipelineLogHandler(writer)
            for record in records:
                handler.emit(record)
            writer.close()
            return read_events(path)

    def test_step_transitions(self):
        events = self._events_for([
            make_record('screenwrite.orchestrator', logging.INFO,
                        'Step 1: Parsing script into beats'),
            make_record('screenwrite.orchestrator', logging.INFO,
                        'Step 1.5: Conforming beats to VO audio'),
            make_record('screenwrite.orchestrator', logging.INFO,
                        'Step 2: Fetching B-roll assets'),
            make_record('screenwrite.orchestrator', logging.INFO,
                        'Step 3: Generating FCPXML timeline'),
            make_record('screenwrite.orchestrator', logging.INFO,
                        'Step 4: Building project in DaVinci Resolve'),
        ])
        self.assertEqual([e['type'] for e in events], ['step'] * 5)
        self.assertEqual([e['step'] for e in events],
                         ['parse', 'vo_conform', 'fetch', 'timeline', 'resolve'])

    def test_beat_progress(self):
        events = self._events_for([
            make_record('screenwrite.fetchers.asset_orchestrator', logging.INFO,
                        'Game b-roll progress: 3/12 beats'),
        ])
        self.assertEqual(events[0]['type'], 'beat_progress')
        self.assertEqual((events[0]['done'], events[0]['total']), (3, 12))

    def test_screenwrite_info_passes_other_info_dropped(self):
        events = self._events_for([
            make_record('screenwrite.vo', logging.INFO, 'Conformed 4/6 beats'),
            make_record('urllib3.connectionpool', logging.INFO, 'noise'),
            make_record('yt_dlp', logging.WARNING, 'throttled'),
        ])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['message'], 'Conformed 4/6 beats')
        self.assertEqual(events[1]['logger'], 'yt_dlp')

    def test_drift_guard_orchestrator_step_messages(self):
        """The regexes must keep matching the literal core log messages."""
        source = Path('screenwrite/orchestrator.py').read_text(encoding='utf-8')
        for literal in ('Step 1: Parsing', 'Step 1.5: Conforming',
                        'Step 2: Fetching', 'Step 2: Skipping',
                        'Step 3: Generating', 'Step 4: Building',
                        'Step 4: Skipping'):
            self.assertIn(literal, source,
                          f'orchestrator log message changed: {literal!r}')
            matched = any(p.match(literal) for p, _ in STEP_PATTERNS)
            self.assertTrue(matched, f'no STEP_PATTERN matches {literal!r}')

    def test_drift_guard_beat_progress_message(self):
        source = Path('screenwrite/fetchers/asset_orchestrator.py').read_text(encoding='utf-8')
        self.assertIn('Game b-roll progress: {done}/{len(beats)} beats', source)
        self.assertTrue(PROGRESS_RE.match('Game b-roll progress: 1/6 beats'))


class TestRunnerMain(unittest.TestCase):
    def _config(self, tmp):
        run_dir = Path(tmp)
        script = run_dir / 'script.md'
        script.write_text('Some narration text long enough to form one beat '
                          'of at least thirteen words right here now.',
                          encoding='utf-8')
        config = {
            'run_id': 'r1',
            'repo_root': str(Path.cwd()),
            'script_path': str(script),
            'output_path': str(run_dir / 'out.fcpxml'),
            'skip_fetch': True,
            'orchestrator': {'youtube_enabled': False, 'pexels_enabled': False,
                             'use_llm_queries': False},
        }
        config_path = run_dir / 'run_config.json'
        config_path.write_text(json.dumps(config), encoding='utf-8')
        return config_path

    def _run(self, tmp, orchestrate_result=None, orchestrate_error=None):
        from screenwrite.orchestrator import VideoOrchestrator
        config_path = self._config(tmp)
        if orchestrate_error is not None:
            patcher = patch.object(VideoOrchestrator, 'orchestrate',
                                   side_effect=orchestrate_error)
        else:
            patcher = patch.object(VideoOrchestrator, 'orchestrate',
                                   return_value=orchestrate_result)
        with patcher:
            code = runner_main.run_pipeline(str(config_path))
        return code, Path(tmp)

    def test_success_exit_zero_and_result_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, run_dir = self._run(
                tmp, orchestrate_result={'success': True, 'beats_count': 1,
                                         'warnings': [], 'errors': []})
            self.assertEqual(code, 0)
            result = json.loads((run_dir / 'result.json').read_text(encoding='utf-8'))
            self.assertTrue(result['success'])
            events = read_events(run_dir / 'events.jsonl')
            self.assertEqual(events[0]['type'], 'run_started')
            self.assertNotIn('pexels_api_key', json.dumps(events[0]['config']))
            self.assertEqual(events[-1]['type'], 'result')
            self.assertTrue(events[-1]['success'])

    def test_pipeline_failure_exit_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, run_dir = self._run(
                tmp, orchestrate_result={'success': False, 'warnings': [],
                                         'errors': ['boom']})
            self.assertEqual(code, 3)
            events = read_events(run_dir / 'events.jsonl')
            self.assertEqual(events[-1]['type'], 'result')
            self.assertFalse(events[-1]['success'])

    def test_crash_exit_one_and_fatal_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, run_dir = self._run(tmp, orchestrate_error=RuntimeError('kaboom'))
            self.assertEqual(code, 1)
            events = read_events(run_dir / 'events.jsonl')
            self.assertEqual(events[-1]['type'], 'fatal')
            self.assertIn('kaboom', events[-1]['error'])
            self.assertIn('RuntimeError', events[-1]['traceback'])


if __name__ == '__main__':
    unittest.main()
