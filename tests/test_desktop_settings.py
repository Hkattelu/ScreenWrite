"""Tests for the desktop SettingsStore and API-key validation helpers."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from desktop.server.settings import (
    SettingsStore,
    test_gemini_key,
    test_pexels_key,
)


class TestSettingsStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        self.home = Path(self.tmp.name) / 'home'
        self.repo.mkdir()
        (self.repo / '.env.example').write_text(
            'PEXELS_API_KEY=your_api_key_here\nGEMINI_API_KEY=your_api_key_here\n')
        self.store = SettingsStore(repo_root=self.repo, app_home=self.home)

    def test_env_created_from_example_and_key_written(self):
        with patch.dict(os.environ, {}, clear=False):
            self.store.put({'keys': {'gemini': 'AIzaTestKey9999'}})
            env_text = (self.repo / '.env').read_text()
            # Key becomes visible to this process immediately (asserted inside
            # the patch context - patch.dict restores os.environ on exit)
            self.assertEqual(os.environ.get('GEMINI_API_KEY'), 'AIzaTestKey9999')
        self.assertIn('GEMINI_API_KEY=AIzaTestKey9999', env_text)
        # Untouched keys keep their example placeholder
        self.assertIn('PEXELS_API_KEY=your_api_key_here', env_text)

    def test_get_masks_keys_and_hides_placeholders(self):
        with patch.dict(os.environ,
                        {'GEMINI_API_KEY': 'AIzaLongKeyabcd',
                         'PEXELS_API_KEY': 'your_api_key_here'}):
            payload = self.store.get()
        self.assertEqual(payload['gemini_key'], '...abcd')
        self.assertIsNone(payload['pexels_key'])

    def test_defaults_roundtrip_atomic(self):
        self.store.put({'defaults': {'last_game': 'Hollow Knight',
                                     'max_workers': 8,
                                     'unknown_field': 'dropped'}})
        payload = self.store.get()
        self.assertEqual(payload['defaults']['last_game'], 'Hollow Knight')
        self.assertEqual(payload['defaults']['max_workers'], 8)
        self.assertNotIn('unknown_field', payload['defaults'])
        self.assertFalse((self.home / 'desktop_settings.json.tmp').exists())

    def test_media_dir_defaults_when_unset(self):
        payload = self.store.get()
        self.assertTrue(payload['defaults']['media_dir'])


class TestKeyValidation(unittest.TestCase):
    def _response(self, status, body=None):
        response = MagicMock()
        response.status_code = status
        response.json.return_value = body or {}
        return response

    def test_gemini_valid(self):
        with patch('desktop.server.settings.requests.get',
                   return_value=self._response(200)):
            self.assertTrue(test_gemini_key('AIzaX')['ok'])

    def test_gemini_invalid_carries_api_message(self):
        body = {'error': {'message': 'API key not valid.'}}
        with patch('desktop.server.settings.requests.get',
                   return_value=self._response(400, body)):
            result = test_gemini_key('AIzaBad')
        self.assertFalse(result['ok'])
        self.assertIn('API key not valid', result['message'])

    def test_pexels_forbidden(self):
        with patch('desktop.server.settings.requests.get',
                   return_value=self._response(403)):
            result = test_pexels_key('nope')
        self.assertFalse(result['ok'])
        self.assertEqual(result['status'], 403)

    def test_no_key(self):
        self.assertFalse(test_gemini_key('')['ok'])
        self.assertFalse(test_pexels_key(None)['ok'])


if __name__ == '__main__':
    unittest.main()
