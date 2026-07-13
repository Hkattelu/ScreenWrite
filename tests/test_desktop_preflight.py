"""Tests for desktop pre-flight checks (deps, keys, Resolve subprocess probe)."""

import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from desktop.server import preflight


class FakeSettings:
    def __init__(self, keys=None):
        self.keys = keys or {}

    def read_key(self, name):
        return self.keys.get(name)


class TestCheckAll(unittest.TestCase):
    def setUp(self):
        preflight.invalidate_resolve_cache()

    def test_reports_dependency_and_key_state(self):
        settings = FakeSettings({'GEMINI_API_KEY': 'AIzaX'})
        with patch('shutil.which', lambda name: 'C:/bin/ffmpeg.exe'), \
             patch('subprocess.run', return_value=MagicMock(returncode=0, stdout='v20')), \
             patch('importlib.util.find_spec', lambda name: object()):
            report = preflight.check_all(settings, include_resolve=False)
        self.assertTrue(report['ffmpeg']['ok'])
        self.assertTrue(report['node']['ok'])
        self.assertTrue(report['ytdlp']['ok'])
        self.assertTrue(report['whisper']['ok'])
        self.assertTrue(report['gemini_key']['ok'])
        self.assertFalse(report['pexels_key']['ok'])
        self.assertNotIn('resolve', report)

    def test_missing_ffmpeg(self):
        with patch('shutil.which', lambda name: None), \
             patch('subprocess.run', side_effect=FileNotFoundError):
            report = preflight.check_all(FakeSettings(), include_resolve=False)
        self.assertFalse(report['ffmpeg']['ok'])
        self.assertFalse(report['node']['ok'])


class TestResolveProbe(unittest.TestCase):
    def setUp(self):
        preflight.invalidate_resolve_cache()

    def _completed(self, stdout):
        return MagicMock(stdout=stdout, returncode=0)

    def test_probe_ok(self):
        payload = json.dumps({'ok': True, 'project_name': 'MyEssay'})
        with patch('desktop.server.preflight.subprocess.run',
                   return_value=self._completed(payload + '\n')):
            result = preflight.probe_resolve()
        self.assertTrue(result['ok'])
        self.assertEqual(result['project_name'], 'MyEssay')

    def test_probe_not_running(self):
        payload = json.dumps({'ok': False, 'error': 'Is Resolve running?'})
        with patch('desktop.server.preflight.subprocess.run',
                   return_value=self._completed(payload)):
            result = preflight.probe_resolve()
        self.assertFalse(result['ok'])
        self.assertIn('Resolve', result['error'])

    def test_probe_timeout(self):
        with patch('desktop.server.preflight.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(cmd='x', timeout=10)):
            result = preflight.probe_resolve()
        self.assertFalse(result['ok'])
        self.assertIn('timed out', result['error'])

    def test_probe_result_cached(self):
        payload = json.dumps({'ok': True})
        with patch('desktop.server.preflight.subprocess.run',
                   return_value=self._completed(payload)) as run_mock:
            preflight.probe_resolve()
            preflight.probe_resolve()
        self.assertEqual(run_mock.call_count, 1)


if __name__ == '__main__':
    unittest.main()
