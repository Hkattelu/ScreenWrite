"""
Tests for the desktop server: RunManager state machine and the Flask API.

The runner child process is stubbed - a fake Popen plus hand-written
events.jsonl files stand in for real pipeline runs.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from desktop.server.app_factory import create_app
from desktop.server.runs import RunManager, RunBusyError
from desktop.server.settings import SettingsStore


class FakeProc:
    def __init__(self, pid=4242):
        self.pid = pid
        self._returncode = None

    def poll(self):
        return self._returncode

    def terminate(self):
        self._returncode = -15

    def finish(self, code=0):
        self._returncode = code


class RunManagerHarness:
    """RunManager with spawn stubbed and app-home redirected to a tmp dir."""

    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.settings = SettingsStore(repo_root=self.tmp / 'repo',
                                      app_home=self.tmp / 'home')
        (self.tmp / 'repo').mkdir(parents=True, exist_ok=True)
        (self.tmp / 'repo' / '.env.example').write_text('GEMINI_API_KEY=your_api_key_here\n')
        self.manager = RunManager(self.settings)
        self.proc = FakeProc()
        self._patches = [
            patch.object(RunManager, '_spawn', lambda mgr, cfg: self.proc),
            patch('desktop.server.runs.runs_dir', lambda: self._runs_dir()),
            patch('desktop.server.runs.new_run_dir', self._new_run_dir),
            patch('desktop.server.runs.default_media_dir',
                  lambda: self.tmp / 'media'),
        ]
        for p in self._patches:
            p.start()

    def _runs_dir(self):
        path = self.tmp / 'runs'
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _new_run_dir(self, run_id):
        path = self._runs_dir() / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def stop(self):
        for p in self._patches:
            p.stop()

    def run_dir(self):
        return self.manager._current.run_dir

    def write_events(self, events):
        path = self.run_dir() / 'events.jsonl'
        with open(path, 'a', encoding='utf-8') as handle:
            for i, event in enumerate(events, self._next_seq()):
                event = {'seq': i, 'ts': 0.0, **event}
                handle.write(json.dumps(event) + '\n')

    def _next_seq(self):
        current = self.manager._current
        return (current.events[-1]['seq'] + 1) if current.events else 1


START_PAYLOAD = {'script_text': 'word ' * 20, 'game': 'Dark Souls'}


class TestRunManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.harness = RunManagerHarness(self.tmp.name)
        self.addCleanup(self.harness.stop)
        self.manager = self.harness.manager

    def test_start_writes_inputs_and_config(self):
        run_id = self.manager.start(START_PAYLOAD)
        run_dir = self.harness.run_dir()
        self.assertTrue((run_dir / 'script.md').exists())
        config = json.loads((run_dir / 'run_config.json').read_text())
        self.assertEqual(config['run_id'], run_id)
        self.assertEqual(config['orchestrator']['game'], 'Dark Souls')
        self.assertNotIn('pexels_api_key', config['orchestrator'])

    def test_busy_while_running(self):
        self.manager.start(START_PAYLOAD)
        with self.assertRaises(RunBusyError):
            self.manager.start(START_PAYLOAD)

    def test_snapshot_tracks_steps_and_beats(self):
        self.manager.start(START_PAYLOAD)
        self.harness.write_events([
            {'type': 'step', 'step': 'parse', 'label': 'Step 1'},
            {'type': 'beat_progress', 'done': 2, 'total': 6},
            {'type': 'log', 'level': 'INFO', 'logger': 'x', 'message': 'hi'},
        ])
        snap = self.manager.snapshot()
        self.assertEqual(snap['state'], 'running')
        self.assertEqual(snap['step'], 'parse')
        self.assertEqual((snap['beat_done'], snap['beat_total']), (2, 6))
        self.assertEqual(len(snap['events']), 3)

    def test_after_seq_cursor(self):
        self.manager.start(START_PAYLOAD)
        self.harness.write_events([
            {'type': 'log', 'level': 'INFO', 'logger': 'x', 'message': 'one'},
            {'type': 'log', 'level': 'INFO', 'logger': 'x', 'message': 'two'},
        ])
        first = self.manager.snapshot(after_seq=0)
        second = self.manager.snapshot(after_seq=first['last_seq'])
        self.assertEqual(len(first['events']), 2)
        self.assertEqual(second['events'], [])

    def test_success_and_failure_states(self):
        self.manager.start(START_PAYLOAD)
        self.harness.write_events([
            {'type': 'result', 'success': True,
             'workflow_result': {'success': True, 'output_path': 'x.fcpxml'}},
        ])
        self.harness.proc.finish(0)
        self.assertEqual(self.manager.snapshot()['state'], 'succeeded')

    def test_failed_state(self):
        self.manager.start(START_PAYLOAD)
        self.harness.write_events([
            {'type': 'result', 'success': False,
             'workflow_result': {'success': False}},
        ])
        self.harness.proc.finish(3)
        self.assertEqual(self.manager.snapshot()['state'], 'failed')

    def test_cancelled_state(self):
        self.manager.start(START_PAYLOAD)
        self.manager.cancel()
        self.harness.proc.finish(-15)
        self.assertEqual(self.manager.snapshot()['state'], 'cancelled')

    def test_crashed_state_attaches_log_tail(self):
        self.manager.start(START_PAYLOAD)
        (self.harness.run_dir() / 'run.log').write_text('boom line\n')
        self.harness.proc.finish(1)
        snap = self.manager.snapshot()
        self.assertEqual(snap['state'], 'crashed')
        self.assertIn('boom line', snap['fatal']['log_tail'])

    def test_validation_errors(self):
        from desktop.server.runs import RunValidationError
        with self.assertRaises(RunValidationError):
            self.manager.start({'script_text': '   '})
        with self.assertRaises(RunValidationError):
            self.manager.start({'script_text': 'ok words here',
                                'vo_path': 'Z:/nope.wav'})

    def test_result_from_memory_and_disk(self):
        run_id = self.manager.start(START_PAYLOAD)
        self.harness.write_events([
            {'type': 'result', 'success': True,
             'workflow_result': {'success': True, 'output_path': 'out.fcpxml'}},
        ])
        self.harness.proc.finish(0)
        self.manager.snapshot()
        result = self.manager.result(run_id)
        self.assertEqual(result['fcpxml_path'], 'out.fcpxml')

        # Disk fallback for an unknown (restarted) manager
        (self.harness._runs_dir() / 'old-run').mkdir()
        (self.harness._runs_dir() / 'old-run' / 'result.json').write_text(
            json.dumps({'success': True, 'output_path': 'old.fcpxml'}))
        old = self.manager.result('old-run')
        self.assertEqual(old['fcpxml_path'], 'old.fcpxml')


class TestApi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.harness = RunManagerHarness(self.tmp.name)
        self.addCleanup(self.harness.stop)
        app = create_app(self.harness.manager, self.harness.settings)
        app.testing = True
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['ok'])

    def test_run_lifecycle_and_409(self):
        response = self.client.post('/api/run', json=START_PAYLOAD)
        self.assertEqual(response.status_code, 200)
        run_id = response.get_json()['run_id']

        busy = self.client.post('/api/run', json=START_PAYLOAD)
        self.assertEqual(busy.status_code, 409)

        snap = self.client.get('/api/run/current').get_json()
        self.assertEqual(snap['run_id'], run_id)
        self.assertEqual(snap['state'], 'running')

        cancel = self.client.post(f'/api/run/{run_id}/cancel')
        self.assertTrue(cancel.get_json()['cancelled'])

    def test_run_validation_422(self):
        response = self.client.post('/api/run', json={'script_text': ''})
        self.assertEqual(response.status_code, 422)

    def test_script_load(self):
        script = Path(self.tmp.name) / 's.md'
        script.write_text('hello narration', encoding='utf-8')
        response = self.client.post('/api/script/load', json={'path': str(script)})
        self.assertEqual(response.get_json()['text'], 'hello narration')
        missing = self.client.post('/api/script/load', json={'path': 'Z:/none.md'})
        self.assertEqual(missing.status_code, 422)

    def test_settings_roundtrip_masked(self):
        import os
        # SettingsStore.put mutates os.environ; don't leak into other tests.
        self.addCleanup(lambda: os.environ.pop('GEMINI_API_KEY', None))
        put = self.client.put('/api/settings', json={
            'keys': {'gemini': 'AIzaSyFAKEKEY1234'},
            'defaults': {'last_game': 'Hades', 'max_workers': 2},
        })
        payload = put.get_json()
        self.assertEqual(payload['gemini_key'], '...1234')
        self.assertEqual(payload['defaults']['last_game'], 'Hades')
        self.assertEqual(payload['defaults']['max_workers'], 2)
        # Raw key never appears anywhere in the response
        self.assertNotIn('AIzaSyFAKEKEY1234', put.get_data(as_text=True))

    def test_cache_clear_blocked_during_run(self):
        self.client.post('/api/run', json=START_PAYLOAD)
        response = self.client.post('/api/cache/clear')
        self.assertEqual(response.status_code, 409)

    def test_spa_fallback(self):
        with patch('desktop.server.app_factory.DIST_DIR', Path(self.tmp.name)):
            (Path(self.tmp.name) / 'index.html').write_text('<html>app</html>')
            app = create_app(self.harness.manager, self.harness.settings)
            app.testing = True
            client = app.test_client()
            self.assertIn(b'app', client.get('/').data)
            self.assertIn(b'app', client.get('/some/deep/route').data)


if __name__ == '__main__':
    unittest.main()
