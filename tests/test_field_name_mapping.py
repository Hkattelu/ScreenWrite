"""
Unit tests for field name mapping in asset fetching.

These tests verify specific examples of field name mapping between
frontend (youtube_phrase) and backend (youtube_search_phrase) conventions.
"""

import unittest
import os
import sys

# Import the field mapping function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../webapp/backend')))
from routes.fetch import _map_beat_field_names


class TestFieldNameMapping(unittest.TestCase):
    """
    Unit tests for field name mapping.
    
    Validates: Requirements 6.1, 6.2, 6.3
    """
    
    def test_youtube_phrase_to_youtube_search_phrase(self):
        """Test that youtube_phrase (frontend) maps correctly."""
        beat = {
            'id': 'beat_001',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': 'python tutorial',
            'stock_keyword': 'coding'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, 'python tutorial')
        self.assertEqual(stock_query, 'coding')
    
    def test_youtube_search_phrase_backend_field(self):
        """Test that youtube_search_phrase (backend) is accepted."""
        beat = {
            'id': 'beat_002',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_search_phrase': 'javascript guide',
            'stock_keyword': 'programming'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, 'javascript guide')
        self.assertEqual(stock_query, 'programming')
    
    def test_backward_compatibility_both_fields(self):
        """Test backward compatibility when both field names are present."""
        beat = {
            'id': 'beat_003',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': 'frontend value',
            'youtube_search_phrase': 'backend value',
            'stock_keyword': 'test'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # Should prefer youtube_phrase (frontend field)
        self.assertEqual(youtube_query, 'frontend value')
        self.assertEqual(stock_query, 'test')
    
    def test_default_empty_string_for_missing_youtube_field(self):
        """Test that missing youtube field defaults to empty string."""
        beat = {
            'id': 'beat_004',
            'text': 'Test beat',
            'duration': 5.0,
            'stock_keyword': 'nature'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, '')
        self.assertEqual(stock_query, 'nature')
    
    def test_default_empty_string_for_missing_stock_field(self):
        """Test that missing stock_keyword defaults to empty string."""
        beat = {
            'id': 'beat_005',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': 'tutorial'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, 'tutorial')
        self.assertEqual(stock_query, '')
    
    def test_both_fields_missing(self):
        """Test that both missing fields default to empty strings."""
        beat = {
            'id': 'beat_006',
            'text': 'Test beat',
            'duration': 5.0
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, '')
        self.assertEqual(stock_query, '')
    
    def test_empty_string_values_preserved(self):
        """Test that explicit empty strings are preserved."""
        beat = {
            'id': 'beat_007',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': '',
            'stock_keyword': ''
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, '')
        self.assertEqual(stock_query, '')
    
    def test_whitespace_only_values(self):
        """Test handling of whitespace-only values."""
        beat = {
            'id': 'beat_008',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': '   ',
            'stock_keyword': '\t\n'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # Should preserve whitespace (trimming is done elsewhere if needed)
        self.assertEqual(youtube_query, '   ')
        self.assertEqual(stock_query, '\t\n')
    
    def test_special_characters_in_queries(self):
        """Test that special characters are preserved."""
        beat = {
            'id': 'beat_009',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': 'C++ tutorial & guide',
            'stock_keyword': 'code #programming'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, 'C++ tutorial & guide')
        self.assertEqual(stock_query, 'code #programming')
    
    def test_unicode_characters_in_queries(self):
        """Test that unicode characters are preserved."""
        beat = {
            'id': 'beat_010',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': 'Python 教程',
            'stock_keyword': 'プログラミング'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, 'Python 教程')
        self.assertEqual(stock_query, 'プログラミング')
    
    def test_very_long_query_strings(self):
        """Test handling of very long query strings."""
        long_query = 'a' * 500
        beat = {
            'id': 'beat_011',
            'text': 'Test beat',
            'duration': 5.0,
            'youtube_phrase': long_query,
            'stock_keyword': 'short'
        }
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        self.assertEqual(youtube_query, long_query)
        self.assertEqual(stock_query, 'short')


if __name__ == '__main__':
    unittest.main()
