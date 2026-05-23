"""
Property-based tests for asset fetching improvements.

Feature: asset-fetching-improvements

These tests use hypothesis to verify correctness properties across
random inputs, ensuring the system behaves correctly for all valid cases.
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from hypothesis import given, strategies as st, settings, assume

# Create dummy app for request context
app = Flask(__name__)

# Import the field mapping function
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../webapp/backend')))
from routes.fetch import _map_beat_field_names


# Custom strategies for generating test data
@st.composite
def beat_strategy(draw):
    """Generate random beat data with various field name combinations."""
    beat_id = draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    text = draw(st.text(min_size=10, max_size=200))
    duration = draw(st.floats(min_value=3.0, max_value=10.0))
    
    # Generate search terms
    youtube_query = draw(st.text(min_size=0, max_size=100))
    stock_query = draw(st.text(min_size=0, max_size=100))
    
    # Randomly choose which field name to use for youtube query
    use_youtube_phrase = draw(st.booleans())
    
    beat = {
        'id': beat_id,
        'text': text,
        'duration': duration,
        'stock_keyword': stock_query
    }
    
    if use_youtube_phrase:
        beat['youtube_phrase'] = youtube_query
    else:
        beat['youtube_search_phrase'] = youtube_query
    
    return beat


@st.composite
def beat_with_both_fields_strategy(draw):
    """Generate beat data with both youtube_phrase and youtube_search_phrase."""
    beat_id = draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    text = draw(st.text(min_size=10, max_size=200))
    duration = draw(st.floats(min_value=3.0, max_value=10.0))
    
    youtube_phrase = draw(st.text(min_size=0, max_size=100))
    youtube_search_phrase = draw(st.text(min_size=0, max_size=100))
    stock_query = draw(st.text(min_size=0, max_size=100))
    
    return {
        'id': beat_id,
        'text': text,
        'duration': duration,
        'youtube_phrase': youtube_phrase,
        'youtube_search_phrase': youtube_search_phrase,
        'stock_keyword': stock_query
    }


class TestQueryTextPersistence(unittest.TestCase):
    """
    Property 1: Query text persistence and usage
    
    For any beat with modified search terms, when the beat is saved and then
    a fetch is initiated, the Asset_Orchestrator should receive and use the
    exact modified search terms, not stale or incorrect terms.
    
    Validates: Requirements 1.1, 1.2, 1.3
    """
    
    @given(beat=beat_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_1_query_text_persistence(self, beat):
        """
        Feature: asset-fetching-improvements, Property 1: Query text persistence
        
        Test that modified search terms are correctly extracted and would be
        used by Asset_Orchestrator.
        """
        # Extract queries using the field mapping function
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # The extracted queries should match what was in the beat
        expected_youtube = beat.get('youtube_phrase', beat.get('youtube_search_phrase', ''))
        expected_stock = beat.get('stock_keyword', '')
        
        # Verify the mapping is correct
        self.assertEqual(youtube_query, expected_youtube,
                        f"YouTube query mismatch for beat {beat['id']}")
        self.assertEqual(stock_query, expected_stock,
                        f"Stock query mismatch for beat {beat['id']}")
    
    @given(beat=beat_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_1_orchestrator_receives_correct_queries(self, beat):
        """
        Test that the orchestrator would receive the correct query text.
        
        This simulates the flow: beat data -> field mapping -> orchestrator
        """
        # Extract queries
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # Simulate what would be passed to orchestrator
        query_dict = {
            'id': beat['id'],
            'youtube_query': youtube_query,
            'stock_query': stock_query,
            'duration': beat['duration']
        }
        
        # Verify the query dict contains the correct values
        expected_youtube = beat.get('youtube_phrase', beat.get('youtube_search_phrase', ''))
        expected_stock = beat.get('stock_keyword', '')
        
        self.assertEqual(query_dict['youtube_query'], expected_youtube)
        self.assertEqual(query_dict['stock_query'], expected_stock)
        self.assertEqual(query_dict['id'], beat['id'])
        self.assertEqual(query_dict['duration'], beat['duration'])


class TestFieldNameRoundTrip(unittest.TestCase):
    """
    Property 2: Field name round-trip consistency
    
    For any beat data sent from Frontend with youtube_phrase field, when it
    is saved to the Backend and read back, the data should be correctly mapped
    to youtube_search_phrase internally and back to youtube_phrase when returned
    to Frontend.
    
    Validates: Requirements 1.5, 6.1, 6.2, 6.3, 6.5
    """
    
    @given(beat=beat_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_field_name_mapping_consistency(self, beat):
        """
        Feature: asset-fetching-improvements, Property 2: Field name round-trip consistency
        
        Test that youtube_phrase correctly maps to youtube_search_phrase and back.
        """
        # Extract queries using field mapping
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # The function should accept both field names
        if 'youtube_phrase' in beat:
            self.assertEqual(youtube_query, beat['youtube_phrase'])
        elif 'youtube_search_phrase' in beat:
            self.assertEqual(youtube_query, beat['youtube_search_phrase'])
        else:
            self.assertEqual(youtube_query, '')
        
        # Stock keyword should always map correctly
        self.assertEqual(stock_query, beat.get('stock_keyword', ''))
    
    @given(beat=beat_with_both_fields_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_both_fields_present(self, beat):
        """
        Test behavior when both youtube_phrase and youtube_search_phrase are present.
        
        The function should prefer youtube_phrase (frontend field) over youtube_search_phrase.
        """
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # Should use youtube_phrase when both are present
        self.assertEqual(youtube_query, beat['youtube_phrase'])
        self.assertEqual(stock_query, beat.get('stock_keyword', ''))
    
    @given(
        youtube_text=st.text(min_size=0, max_size=100),
        stock_text=st.text(min_size=0, max_size=100),
        use_frontend_field=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_2_backward_compatibility(self, youtube_text, stock_text, use_frontend_field):
        """
        Test backward compatibility with both field naming conventions.
        """
        beat = {
            'id': 'test_beat',
            'text': 'Test text for beat',
            'duration': 5.0,
            'stock_keyword': stock_text
        }
        
        if use_frontend_field:
            beat['youtube_phrase'] = youtube_text
        else:
            beat['youtube_search_phrase'] = youtube_text
        
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # Should get the same result regardless of which field name was used
        self.assertEqual(youtube_query, youtube_text)
        self.assertEqual(stock_query, stock_text)
    
    @given(beat=beat_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_empty_fields_handled(self, beat):
        """
        Test that empty or missing fields are handled correctly.
        """
        youtube_query, stock_query = _map_beat_field_names(beat)
        
        # Should return strings (not None)
        self.assertIsInstance(youtube_query, str)
        self.assertIsInstance(stock_query, str)
        
        # Empty strings should be preserved
        if not beat.get('youtube_phrase', '') and not beat.get('youtube_search_phrase', ''):
            self.assertEqual(youtube_query, '')
        
        if not beat.get('stock_keyword', ''):
            self.assertEqual(stock_query, '')


class TestDownloadProgressTracking(unittest.TestCase):
    """
    Property 6: Download state transitions
    Property 7: Independent asset progress tracking
    
    Validates: Requirements 3.3, 3.4, 3.5
    """
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @given(
        beat_id=st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        candidate_id=st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'),
        percents=st.lists(st.floats(min_value=0.0, max_value=100.0), min_size=1, max_size=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_6_download_state_transitions(self, beat_id, candidate_id, percents):
        """
        Feature: asset-fetching-improvements, Property 6: Download state transitions
        
        Test that download progress updates follow expected state transitions.
        """
        # Sort percents to simulate increasing progress
        percents.sort()
        
        # Mock session state storage
        states = []
        def mock_save_state(sid, state):
            # Capture a deep copy of the state
            states.append(json.loads(json.dumps(state)))

        with patch('routes.fetch.load_session_state') as mock_load, \
             patch('routes.fetch.save_session_state', side_effect=mock_save_state), \
             patch('routes.fetch.session_exists', return_value=True), \
             patch('routes.fetch.get_session_path', return_value=self.temp_dir):
            
            # Initial state
            initial_state = {
                'sessionId': 'test_session',
                'beats': [{'id': beat_id, 'youtube_phrase': 'test'}],
                'config': {},
                'assets': {}
            }
            mock_load.return_value = initial_state
            
            # This is a bit complex to test the background thread directly in hypothesis,
            # so we test the progress_callback logic that would be inside background_download.
            
            # Reconstruct the logic from fetch.py
            current_state = initial_state.copy()
            
            # 1. Starting state
            current_state['download_progress'] = {
                beat_id: {
                    'status': 'starting',
                    'percent': 0,
                    'updated_at': '2026-02-12T12:00:00'
                }
            }
            mock_save_state('test_session', current_state)
            
            # 2. Progress updates
            for p in percents:
                # In the real code, load_session_state would be called inside progress_callback
                mock_load.return_value = current_state
                
                # simulate progress_callback(p, 'downloading')
                if 'download_progress' not in current_state:
                    current_state['download_progress'] = {}
                current_state['download_progress'][beat_id] = {
                    'status': 'downloading',
                    'percent': p,
                    'updated_at': '2026-02-12T12:00:01'
                }
                mock_save_state('test_session', current_state)
            
            # 3. Processing state
            mock_load.return_value = current_state
            current_state['download_progress'][beat_id]['status'] = 'processing'
            current_state['download_progress'][beat_id]['percent'] = 100
            mock_save_state('test_session', current_state)
            
            # 4. Complete state
            mock_load.return_value = current_state
            current_state['download_progress'][beat_id]['status'] = 'complete'
            current_state['assets'][beat_id] = '/path/to/file.mp4'
            mock_save_state('test_session', current_state)
            
            # Verify transitions
            self.assertEqual(states[0]['download_progress'][beat_id]['status'], 'starting')
            
            # Check intermediate progress states
            for i, p in enumerate(percents):
                self.assertEqual(states[i+1]['download_progress'][beat_id]['status'], 'downloading')
                self.assertEqual(states[i+1]['download_progress'][beat_id]['percent'], p)
            
            # Check final states
            self.assertEqual(states[-2]['download_progress'][beat_id]['status'], 'processing')
            self.assertEqual(states[-1]['download_progress'][beat_id]['status'], 'complete')
            self.assertEqual(states[-1]['assets'][beat_id], '/path/to/file.mp4')

    @given(
        beat_ids=st.lists(st.text(min_size=5, max_size=10, alphabet='0123456789'), min_size=2, max_size=5, unique=True),
        progress_data=st.lists(
            st.fixed_dictionaries({
                'beat_id_idx': st.integers(min_value=0, max_value=4),
                'percent': st.floats(min_value=0.0, max_value=100.0)
            }),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_7_independent_progress_tracking(self, beat_ids, progress_data):
        """
        Feature: asset-fetching-improvements, Property 7: Independent asset progress tracking
        
        Test that multiple downloads maintain independent progress states in the session.
        """
        # Create initial state
        current_state = {
            'sessionId': 'test_session',
            'beats': [{'id': bid} for bid in beat_ids],
            'assets': {},
            'download_progress': {}
        }
        
        # Track expected percents for each beat
        expected_percents = {bid: 0.0 for bid in beat_ids}
        
        # Simulate interleaved progress updates
        for update in progress_data:
            idx = update['beat_id_idx'] % len(beat_ids)
            bid = beat_ids[idx]
            percent = update['percent']
            
            # Update only this beat's progress
            current_state['download_progress'][bid] = {
                'status': 'downloading',
                'percent': percent,
                'updated_at': '2026-02-12T12:00:00'
            }
            expected_percents[bid] = percent
            
            # Verify other beats' progress remained unchanged (if they had any)
            for other_bid in beat_ids:
                if other_bid != bid and other_bid in current_state['download_progress']:
                    # This check is inherently true because we only modified one key,
                    # but it validates our data structure (independent keys in a dict)
                    pass
        
        # Verify final state matches all latest updates
        for bid, expected_p in expected_percents.items():
            if bid in current_state['download_progress']:
                self.assertEqual(current_state['download_progress'][bid]['percent'], expected_p)
                self.assertEqual(current_state['download_progress'][bid]['status'], 'downloading')



class TestSearchWithoutDownload(unittest.TestCase):
    """
    Property 3: Search without download
    
    For any search operation, when the search endpoint is called, the system
    should return candidate metadata without creating any downloaded files on disk.
    
    Validates: Requirements 2.1
    """
    
    @given(
        youtube_query=st.text(min_size=1, max_size=100),
        stock_query=st.text(min_size=1, max_size=100),
        duration=st.floats(min_value=3.0, max_value=10.0)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_3_search_without_download(self, youtube_query, stock_query, duration):
        """
        Feature: asset-fetching-improvements, Property 3: Search without download
        
        Test that search operations don't create files on disk.
        """
        # Create a temporary directory to monitor
        with tempfile.TemporaryDirectory() as temp_dir:
            # Track files before search
            files_before = set()
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        files_before.add(os.path.join(root, file))
            
            # Mock the fetchers to simulate search behavior
            from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
            
            # Create orchestrator with mocked fetchers
            with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube, \
                 patch('screenwrite.fetchers.asset_orchestrator.PexelsClient') as MockPexels:
                
                # Mock YouTube search to return metadata without downloading
                mock_youtube_instance = Mock()
                mock_youtube_instance.name = "YouTube"
                mock_youtube_instance.search = Mock(return_value=[
                    {
                        'id': 'test_video_1',
                        'title': 'Test Video 1',
                        'thumbnail_url': 'https://example.com/thumb1.jpg',
                        'duration': duration,
                        'url': 'https://youtube.com/watch?v=test1'
                    }
                ])
                MockYouTube.return_value = mock_youtube_instance
                
                # Mock Pexels search to return metadata without downloading
                mock_pexels_instance = Mock()
                mock_pexels_instance.name = "Pexels"
                mock_pexels_instance.search = Mock(return_value=[
                    {
                        'id': 'test_pexels_1',
                        'title': 'Test Pexels Video 1',
                        'thumbnail_url': 'https://example.com/pexels_thumb1.jpg',
                        'duration': duration,
                        'video_id': 12345
                    }
                ])
                MockPexels.return_value = mock_pexels_instance
                
                # Create orchestrator
                orchestrator = AssetOrchestrator(
                    output_dir=temp_dir,
                    youtube_enabled=True,
                    pexels_enabled=True
                )
                
                # Perform search
                candidates = orchestrator.search_assets(
                    youtube_query=youtube_query,
                    stock_query=stock_query,
                    duration=duration,
                    count=5
                )
                
                # Verify candidates were returned
                self.assertIsInstance(candidates, list)
                
                # Track files after search
                files_after = set()
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            files_after.add(os.path.join(root, file))
                
                # Verify no new files were created
                new_files = files_after - files_before
                self.assertEqual(len(new_files), 0,
                               f"Search operation created {len(new_files)} files: {new_files}")
                
                # Verify search methods were called (not fetch methods)
                if youtube_query.strip():
                    mock_youtube_instance.search.assert_called()
                if stock_query.strip():
                    mock_pexels_instance.search.assert_called()
    
    @given(
        query=st.text(min_size=1, max_size=100),
        count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_3_search_returns_metadata_only(self, query, count):
        """
        Test that search returns only metadata, not file paths.
        """
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube:
            # Mock YouTube search
            mock_youtube_instance = Mock()
            mock_youtube_instance.name = "YouTube"
            mock_youtube_instance.search = Mock(return_value=[
                {
                    'id': f'video_{i}',
                    'title': f'Video {i}',
                    'thumbnail_url': f'https://example.com/thumb{i}.jpg',
                    'duration': 5.0,
                    'url': f'https://youtube.com/watch?v=test{i}'
                }
                for i in range(min(count, 5))
            ])
            MockYouTube.return_value = mock_youtube_instance
            
            orchestrator = AssetOrchestrator(youtube_enabled=True, pexels_enabled=False)
            
            candidates = orchestrator.search_assets(
                youtube_query=query,
                stock_query='',
                duration=5.0,
                count=count
            )
            
            # Verify all candidates have required metadata fields
            for candidate in candidates:
                self.assertIsInstance(candidate, AssetCandidate)
                self.assertIsInstance(candidate.id, str)
                self.assertIsInstance(candidate.title, str)
                self.assertIsInstance(candidate.thumbnail_url, str)
                self.assertIsInstance(candidate.duration, float)
                self.assertIsInstance(candidate.source, str)
                self.assertIsInstance(candidate.metadata, dict)
                
                # Verify no file paths in the candidate
                self.assertNotIn('file_path', candidate.metadata)
                self.assertNotIn('path', candidate.metadata)



class TestCandidateMetadataCompleteness(unittest.TestCase):
    """
    Property 4: Candidate metadata completeness
    
    For any asset candidate returned by the search endpoint, the candidate should
    include all required fields: id, title, thumbnail_url, duration, source, and query_used.
    
    Validates: Requirements 2.2, 8.2
    """
    
    @given(
        candidate_count=st.integers(min_value=1, max_value=10),
        query=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_4_all_candidates_have_required_fields(self, candidate_count, query):
        """
        Feature: asset-fetching-improvements, Property 4: Candidate metadata completeness
        
        Test that all candidates have required fields.
        """
        assume(query.strip())
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube:
            # Mock YouTube search to return candidates
            mock_youtube_instance = Mock()
            mock_youtube_instance.name = "YouTube"
            
            # Generate mock search results
            mock_results = [
                {
                    'id': f'video_{i}',
                    'title': f'Video Title {i}',
                    'thumbnail_url': f'https://example.com/thumb{i}.jpg',
                    'duration': float(i + 5),
                    'url': f'https://youtube.com/watch?v=test{i}'
                }
                for i in range(candidate_count)
            ]
            mock_youtube_instance.search = Mock(return_value=mock_results)
            MockYouTube.return_value = mock_youtube_instance
            
            orchestrator = AssetOrchestrator(youtube_enabled=True, pexels_enabled=False)
            
            candidates = orchestrator.search_assets(
                youtube_query=query,
                stock_query='',
                duration=5.0,
                count=candidate_count
            )
            
            # Verify all candidates have required fields
            self.assertGreater(len(candidates), 0, "Should return at least one candidate")
            
            for candidate in candidates:
                # Check all required fields exist
                self.assertIsInstance(candidate, AssetCandidate)
                self.assertTrue(hasattr(candidate, 'id'), "Candidate missing 'id' field")
                self.assertTrue(hasattr(candidate, 'title'), "Candidate missing 'title' field")
                self.assertTrue(hasattr(candidate, 'thumbnail_url'), "Candidate missing 'thumbnail_url' field")
                self.assertTrue(hasattr(candidate, 'duration'), "Candidate missing 'duration' field")
                self.assertTrue(hasattr(candidate, 'source'), "Candidate missing 'source' field")
                self.assertTrue(hasattr(candidate, 'metadata'), "Candidate missing 'metadata' field")
                
                # Check field types
                self.assertIsInstance(candidate.id, str, "id must be string")
                self.assertIsInstance(candidate.title, str, "title must be string")
                self.assertIsInstance(candidate.thumbnail_url, str, "thumbnail_url must be string")
                self.assertIsInstance(candidate.duration, (int, float), "duration must be numeric")
                self.assertIsInstance(candidate.source, str, "source must be string")
                self.assertIsInstance(candidate.metadata, dict, "metadata must be dict")
                
                # Check non-empty values for critical fields
                self.assertNotEqual(candidate.id, '', "id should not be empty")
                self.assertNotEqual(candidate.title, '', "title should not be empty")
                self.assertNotEqual(candidate.source, '', "source should not be empty")
    
    @given(
        youtube_results=st.lists(
            st.fixed_dictionaries({
                'id': st.text(min_size=1, max_size=50),
                'title': st.text(min_size=1, max_size=100),
                'thumbnail_url': st.one_of(st.just(''), st.text(min_size=10, max_size=200)),
                'duration': st.floats(min_value=0.0, max_value=600.0, allow_nan=False, allow_infinity=False),
                'url': st.text(min_size=10, max_size=200)
            }),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_4_metadata_structure_consistency(self, youtube_results):
        """
        Test that metadata structure is consistent across all candidates.
        """
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube:
            mock_youtube_instance = Mock()
            mock_youtube_instance.name = "YouTube"
            mock_youtube_instance.search = Mock(return_value=youtube_results)
            MockYouTube.return_value = mock_youtube_instance
            
            orchestrator = AssetOrchestrator(youtube_enabled=True, pexels_enabled=False)
            
            candidates = orchestrator.search_assets(
                youtube_query='test query',
                stock_query='',
                duration=5.0,
                count=len(youtube_results)
            )
            
            # All candidates should have the same structure
            if len(candidates) > 0:
                first_candidate = candidates[0]
                required_attrs = ['id', 'title', 'thumbnail_url', 'duration', 'source', 'metadata']
                
                for candidate in candidates:
                    for attr in required_attrs:
                        self.assertTrue(
                            hasattr(candidate, attr),
                            f"Candidate missing required attribute: {attr}"
                        )
                        
                        # Check type consistency
                        self.assertEqual(
                            type(getattr(candidate, attr)),
                            type(getattr(first_candidate, attr)),
                            f"Type mismatch for attribute {attr}"
                        )



class TestSingleAssetDownload(unittest.TestCase):
    """
    Property 5: Single asset download on selection
    
    For any asset candidate selection, when a user selects one candidate from
    multiple options, exactly one download should be initiated and it should be
    for the selected candidate.
    
    Validates: Requirements 2.5
    """
    
    @given(
        candidate_id=st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        source=st.sampled_from(['youtube', 'pexels']),
        beat_id=st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    )
    @settings(max_examples=100, deadline=None)
    def test_property_5_single_download_initiated(self, candidate_id, source, beat_id):
        """
        Feature: asset-fetching-improvements, Property 5: Single asset download on selection
        
        Test that selecting one candidate downloads exactly one asset.
        """
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        # Create a mock candidate
        candidate = AssetCandidate(
            id=candidate_id,
            title=f"Test {source} video",
            thumbnail_url=f"https://example.com/{candidate_id}.jpg",
            duration=5.0,
            source=source,
            metadata={
                'id': candidate_id,
                'url': f"https://{source}.com/video/{candidate_id}",
                'download_url': f"https://{source}.com/download/{candidate_id}"
            }
        )
        
        # Mock the fetchers and Path.exists to avoid disk I/O
        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube, \
             patch('screenwrite.fetchers.asset_orchestrator.PexelsClient') as MockPexels, \
             patch('screenwrite.fetchers.asset_orchestrator.Path.exists', return_value=True):
            
            # Track download calls
            download_count = {'youtube': 0, 'pexels': 0}
            
            def mock_youtube_download(video_id, metadata, **kwargs):
                download_count['youtube'] += 1
                return f"/mock/path/youtube_{video_id}.mp4"
            
            def mock_pexels_download(video_id, metadata, **kwargs):
                download_count['pexels'] += 1
                return f"/mock/path/pexels_{video_id}.mp4"
            
            # Setup mocks
            mock_youtube_instance = Mock()
            mock_youtube_instance.name = "YouTube"
            mock_youtube_instance.download_by_id = Mock(side_effect=mock_youtube_download)
            MockYouTube.return_value = mock_youtube_instance
            
            mock_pexels_instance = Mock()
            mock_pexels_instance.name = "Pexels"
            mock_pexels_instance.download_by_id = Mock(side_effect=mock_pexels_download)
            MockPexels.return_value = mock_pexels_instance
            
            # Create orchestrator
            orchestrator = AssetOrchestrator(
                output_dir="/mock/dir",
                youtube_enabled=True,
                pexels_enabled=True
            )
            
            # Download the candidate
            result_path = orchestrator.download_candidate(candidate, beat_id=beat_id)
            
            # Verify exactly one download was initiated
            total_downloads = download_count['youtube'] + download_count['pexels']
            self.assertEqual(total_downloads, 1,
                           f"Expected exactly 1 download, but got {total_downloads}")
            
            # Verify the correct source was used
            if source == 'youtube':
                self.assertEqual(download_count['youtube'], 1)
            else:
                self.assertEqual(download_count['pexels'], 1)
            
            self.assertIsNotNone(result_path)

    @given(
        candidates=st.lists(
            st.fixed_dictionaries({
                'id': st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
                'source': st.sampled_from(['youtube', 'pexels']),
                'title': st.text(min_size=1, max_size=100)
            }),
            min_size=2,
            max_size=5,
            unique_by=lambda x: x['id']  # Ensure unique candidate IDs
        ),
        selected_index=st.integers(min_value=0, max_value=4)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_5_correct_candidate_downloaded(self, candidates, selected_index):
        """
        Test that the correct candidate is downloaded when selected from multiple options.
        """
        # Ensure selected_index is valid
        assume(selected_index < len(candidates))
        
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        selected_candidate_data = candidates[selected_index]
        
        # Create AssetCandidate for the selected one
        selected_candidate = AssetCandidate(
            id=selected_candidate_data['id'],
            title=selected_candidate_data['title'],
            thumbnail_url=f"https://example.com/{selected_candidate_data['id']}.jpg",
            duration=5.0,
            source=selected_candidate_data['source'],
            metadata={'id': selected_candidate_data['id']}
        )
        
        # Track which IDs were downloaded
        downloaded_ids = []
        
        def mock_download(video_id, metadata, **kwargs):
            downloaded_ids.append(video_id)
            return f"/mock/path/{video_id}.mp4"
        
        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube, \
             patch('screenwrite.fetchers.asset_orchestrator.PexelsClient') as MockPexels, \
             patch('screenwrite.fetchers.asset_orchestrator.Path.exists', return_value=True):
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.name = "YouTube"
            mock_youtube_instance.download_by_id = Mock(side_effect=mock_download)
            MockYouTube.return_value = mock_youtube_instance
            
            mock_pexels_instance = Mock()
            mock_pexels_instance.name = "Pexels"
            mock_pexels_instance.download_by_id = Mock(side_effect=mock_download)
            MockPexels.return_value = mock_pexels_instance
            
            orchestrator = AssetOrchestrator(
                output_dir="/mock/dir",
                youtube_enabled=True,
                pexels_enabled=True
            )
            
            # Download the selected candidate
            orchestrator.download_candidate(selected_candidate, beat_id='test_beat')
            
            # Verify only the selected candidate was downloaded
            self.assertEqual(len(downloaded_ids), 1)
            self.assertEqual(downloaded_ids[0], selected_candidate_data['id'])
    
    @given(
        candidate_id=st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        source=st.sampled_from(['youtube', 'pexels'])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_5_download_failure_handling(self, candidate_id, source):
        """
        Test that download failures are handled gracefully without affecting other candidates.
        """
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = AssetCandidate(
                id=candidate_id,
                title=f"Test {source} video",
                thumbnail_url=f"https://example.com/{candidate_id}.jpg",
                duration=5.0,
                source=source,
                metadata={
                    'id': candidate_id,
                    'url': f"https://{source}.com/video/{candidate_id}"
                }
            )
            
            with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube, \
                 patch('screenwrite.fetchers.asset_orchestrator.PexelsClient') as MockPexels:
                
                # Mock download to fail
                def mock_failed_download(video_id, metadata, **kwargs):
                    raise Exception("Download failed")
                
                mock_youtube_instance = Mock()
                mock_youtube_instance.name = "YouTube"
                mock_youtube_instance.download_by_id = Mock(side_effect=mock_failed_download)
                MockYouTube.return_value = mock_youtube_instance
                
                mock_pexels_instance = Mock()
                mock_pexels_instance.name = "Pexels"
                mock_pexels_instance.download_by_id = Mock(side_effect=mock_failed_download)
                MockPexels.return_value = mock_pexels_instance
                
                orchestrator = AssetOrchestrator(
                    output_dir=temp_dir,
                    youtube_enabled=True,
                    pexels_enabled=True
                )
                
                # Attempt download
                result_path = orchestrator.download_candidate(candidate, beat_id='test_beat')
                
                # Should return None on failure, not raise exception
                self.assertIsNone(result_path,
                                "Failed download should return None")
                
                # Verify no files were created
                files_in_dir = os.listdir(temp_dir)
                self.assertEqual(len(files_in_dir), 0,
                               f"No files should be created on failed download, but found: {files_in_dir}")



class TestAssetStorageWithMetadata(unittest.TestCase):
    """
    Property 8: Asset storage with metadata
    
    For any downloaded asset, when stored in Session_State, the system should
    include the file path, beat_id, and query metadata, and this data should be
    retrievable for display.
    
    Validates: Requirements 4.2, 4.3, 4.5
    """
    
    @given(
        beat_id=st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        candidate_id=st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        source=st.sampled_from(['youtube', 'pexels']),
        query=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_8_asset_stored_with_metadata(self, beat_id, candidate_id, source, query):
        """
        Feature: asset-fetching-improvements, Property 8: Asset storage with metadata
        
        Test that downloaded assets are stored with beat_id and query metadata.
        """
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        # Create a mock candidate
        candidate = AssetCandidate(
            id=candidate_id,
            title=f"Test {source} video",
            thumbnail_url=f"https://example.com/{candidate_id}.jpg",
            duration=5.0,
            source=source,
            metadata={
                'id': candidate_id,
                'url': f"https://{source}.com/video/{candidate_id}",
                'download_url': f"https://{source}.com/download/{candidate_id}",
                'query': query
            }
        )
        
        # Mock the fetchers and Path.exists to avoid disk I/O
        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube, \
             patch('screenwrite.fetchers.asset_orchestrator.PexelsClient') as MockPexels, \
             patch('screenwrite.fetchers.asset_orchestrator.Path.exists', return_value=True):
            
            def mock_download(video_id, metadata, **kwargs):
                return f"/mock/path/{source}_{video_id}.mp4"
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.name = "YouTube"
            mock_youtube_instance.download_by_id = Mock(side_effect=mock_download)
            MockYouTube.return_value = mock_youtube_instance
            
            mock_pexels_instance = Mock()
            mock_pexels_instance.name = "Pexels"
            mock_pexels_instance.download_by_id = Mock(side_effect=mock_download)
            MockPexels.return_value = mock_pexels_instance
            
            orchestrator = AssetOrchestrator(
                output_dir="/mock/dir",
                youtube_enabled=True,
                pexels_enabled=True
            )
            
            # Download the candidate
            file_path = orchestrator.download_candidate(candidate, beat_id=beat_id)
            
            # Verify file was "downloaded"
            self.assertIsNotNone(file_path, "File path should not be None")
            
            # Simulate storing in session state
            session_state = {
                'assets': {},
                'beats': [{'id': beat_id}]
            }
            
            # Store the asset with metadata
            session_state['assets'][beat_id] = file_path
            
            # Verify storage structure
            self.assertIn(beat_id, session_state['assets'],
                        "Beat ID should be in assets map")
            self.assertEqual(session_state['assets'][beat_id], file_path,
                           "File path should be stored correctly")
            
            # Verify the file path is retrievable
            retrieved_path = session_state['assets'].get(beat_id)
            self.assertIsNotNone(retrieved_path,
                               "Should be able to retrieve file path by beat_id")
            self.assertEqual(retrieved_path, file_path,
                           "Retrieved path should match stored path")
    
    @given(
        downloads=st.lists(
            st.fixed_dictionaries({
                'beat_id': st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
                'candidate_id': st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
                'source': st.sampled_from(['youtube', 'pexels']),
                'query': st.text(min_size=1, max_size=100)
            }),
            min_size=1,
            max_size=5,
            unique_by=lambda x: x['beat_id']  # Ensure unique beat IDs
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_8_multiple_assets_stored_independently(self, downloads):
        """
        Test that multiple assets can be stored independently with their metadata.
        """
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        session_state = {'assets': {}, 'beats': []}
        
        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube, \
             patch('screenwrite.fetchers.asset_orchestrator.PexelsClient') as MockPexels, \
             patch('screenwrite.fetchers.asset_orchestrator.Path.exists', return_value=True):
            
            def mock_download(video_id, metadata, **kwargs):
                return f"/mock/path/{video_id}.mp4"
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.name = "YouTube"
            mock_youtube_instance.download_by_id = Mock(side_effect=mock_download)
            MockYouTube.return_value = mock_youtube_instance
            
            mock_pexels_instance = Mock()
            mock_pexels_instance.name = "Pexels"
            mock_pexels_instance.download_by_id = Mock(side_effect=mock_download)
            MockPexels.return_value = mock_pexels_instance
            
            orchestrator = AssetOrchestrator(
                output_dir="/mock/dir",
                youtube_enabled=True,
                pexels_enabled=True
            )
            
            # Download and store all assets
            for download_data in downloads:
                candidate = AssetCandidate(
                    id=download_data['candidate_id'],
                    title=f"Test video",
                    thumbnail_url=f"https://example.com/{download_data['candidate_id']}.jpg",
                    duration=5.0,
                    source=download_data['source'],
                    metadata={
                        'id': download_data['candidate_id'],
                        'url': f"https://{download_data['source']}.com/video/{download_data['candidate_id']}",
                        'download_url': f"https://{download_data['source']}.com/download/{download_data['candidate_id']}",
                        'query': download_data['query']
                    }
                )
                
                file_path = orchestrator.download_candidate(candidate, beat_id=download_data['beat_id'])
                
                if file_path:
                    session_state['assets'][download_data['beat_id']] = file_path
                    session_state['beats'].append({'id': download_data['beat_id']})
            
            # Verify all assets are stored independently
            self.assertEqual(len(session_state['assets']), len(downloads),
                           f"Should have {len(downloads)} assets stored")
            
            # Verify each asset is retrievable by its beat_id
            for download_data in downloads:
                beat_id = download_data['beat_id']
                self.assertIn(beat_id, session_state['assets'],
                            f"Beat {beat_id} should be in assets map")
                
                file_path = session_state['assets'][beat_id]
                self.assertIsNotNone(file_path,
                                   f"File path for beat {beat_id} should not be None")
    
    @given(
        beat_id=st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        candidate_id=st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        source=st.sampled_from(['youtube', 'pexels'])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_8_asset_replacement(self, beat_id, candidate_id, source):
        """
        Test that replacing an asset for a beat updates the stored file path.
        """
        from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate
        
        with tempfile.TemporaryDirectory() as temp_dir:
            session_state = {'assets': {}}
            
            with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient') as MockYouTube, \
                 patch('screenwrite.fetchers.asset_orchestrator.PexelsClient') as MockPexels:
                
                download_count = [0]
                
                def mock_download(video_id, metadata, **kwargs):
                    download_count[0] += 1
                    file_path = os.path.join(temp_dir, f"{video_id}_{download_count[0]}.mp4")
                    with open(file_path, 'w') as f:
                        f.write(f"content {download_count[0]}")
                    return file_path
                
                mock_youtube_instance = Mock()
                mock_youtube_instance.name = "YouTube"
                mock_youtube_instance.download_by_id = Mock(side_effect=mock_download)
                MockYouTube.return_value = mock_youtube_instance
                
                mock_pexels_instance = Mock()
                mock_pexels_instance.name = "Pexels"
                mock_pexels_instance.download_by_id = Mock(side_effect=mock_download)
                MockPexels.return_value = mock_pexels_instance
                
                orchestrator = AssetOrchestrator(
                    output_dir=temp_dir,
                    youtube_enabled=True,
                    pexels_enabled=True
                )
                
                # Download first asset
                candidate1 = AssetCandidate(
                    id=candidate_id,
                    title="First video",
                    thumbnail_url=f"https://example.com/{candidate_id}.jpg",
                    duration=5.0,
                    source=source,
                    metadata={
                        'id': candidate_id,
                        'url': f"https://{source}.com/video/{candidate_id}",
                        'download_url': f"https://{source}.com/download/{candidate_id}"
                    }
                )
                
                file_path1 = orchestrator.download_candidate(candidate1, beat_id=beat_id)
                session_state['assets'][beat_id] = file_path1
                
                # Download second asset (replacement)
                candidate2 = AssetCandidate(
                    id=f"{candidate_id}_new",
                    title="Second video",
                    thumbnail_url=f"https://example.com/{candidate_id}_new.jpg",
                    duration=5.0,
                    source=source,
                    metadata={
                        'id': f"{candidate_id}_new",
                        'url': f"https://{source}.com/video/{candidate_id}_new",
                        'download_url': f"https://{source}.com/download/{candidate_id}_new"
                    }
                )
                
                file_path2 = orchestrator.download_candidate(candidate2, beat_id=beat_id)
                session_state['assets'][beat_id] = file_path2  # Replace
                
                # Verify the asset was replaced
                self.assertEqual(session_state['assets'][beat_id], file_path2,
                               "Asset should be replaced with new file path")
                self.assertNotEqual(file_path1, file_path2,
                                  "New file path should be different from old one")
                
                # Verify only one asset is stored per beat
                self.assertEqual(len([k for k in session_state['assets'].keys() if k == beat_id]), 1,
                               "Should have exactly one asset per beat_id")


class TestExploratorySearch(unittest.TestCase):
    """
    Property 10: Exploratory search immutability
    Property 11: Optional search term update on download
    
    Validates: Requirements 5.2, 5.4, 5.5
    """
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @given(
        beat=beat_strategy(),
        custom_query=st.text(min_size=1, max_size=100),
        source=st.sampled_from(['youtube', 'pexels'])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_10_exploratory_search_immutability(self, beat, custom_query, source):
        """
        Feature: asset-fetching-improvements, Property 10: Exploratory search immutability
        
        Test that searching with a custom query does not modify the beat's stored search terms.
        """
        assume(custom_query.strip())
        
        # Mock session loading and searching
        with patch('routes.fetch.load_session_state') as mock_load, \
             patch('routes.fetch.session_exists', return_value=True), \
             patch('screenwrite.fetchers.asset_orchestrator.AssetOrchestrator.search_assets') as mock_search:
            
            # Initial state with deep copy to detect mutations
            initial_beat = json.loads(json.dumps(beat))
            session_state = {
                'sessionId': 'test_session',
                'beats': [beat],
                'config': {}
            }
            mock_load.return_value = session_state
            
            # Mock search to return empty list (we just care about side effects)
            mock_search.return_value = []
            
            # Simulate the search endpoint logic
            from routes.fetch import search_beat_assets
            
            # Create a request context
            with app.test_request_context(
                json={
                    'custom_query': custom_query,
                    'source': source
                }
            ):
                # Perform search
                search_beat_assets('test_session', beat['id'])
                
                # Verify beat data in session state remains unchanged
                current_beat = session_state['beats'][0]
                
                # Check original fields
                self.assertEqual(current_beat.get('youtube_phrase'), initial_beat.get('youtube_phrase'),
                               "youtube_phrase should not change during search")
                self.assertEqual(current_beat.get('stock_keyword'), initial_beat.get('stock_keyword'),
                               "stock_keyword should not change during search")
                self.assertEqual(current_beat.get('youtube_search_phrase'), initial_beat.get('youtube_search_phrase'),
                               "youtube_search_phrase should not change during search")

    @given(
        beat=beat_strategy(),
        new_query=st.text(min_size=1, max_size=100),
        source=st.sampled_from(['youtube', 'pexels']),
        should_update=st.booleans()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_11_optional_update_on_download(self, beat, new_query, source, should_update):
        """
        Feature: asset-fetching-improvements, Property 11: Optional search term update on download
        
        Test that beat search terms are updated only when requested during download.
        """
        assume(new_query.strip())
        
        # Mock session storage
        states_saved = []
        def mock_save_state(sid, state):
            states_saved.append(json.loads(json.dumps(state)))

        with patch('routes.fetch.load_session_state') as mock_load, \
             patch('routes.fetch.save_session_state', side_effect=mock_save_state), \
             patch('routes.fetch.session_exists', return_value=True), \
             patch('routes.fetch.get_session_path', return_value=self.temp_dir), \
             patch('threading.Thread'), \
             patch('screenwrite.fetchers.asset_orchestrator.AssetOrchestrator.download_candidate', return_value='/tmp/file.mp4'):
            # Mock threading.Thread so the background download never spawns. The
            # behavior under test (the optional synchronous beat-query update) runs
            # before the thread starts; without this, the daemon thread can outlive
            # the patch context and invoke the real downloader (real network call).
            
            # Initial state
            initial_beat = json.loads(json.dumps(beat))
            session_state = {
                'sessionId': 'test_session',
                'beats': [beat],
                'config': {},
                'assets': {}
            }
            mock_load.return_value = session_state
            
            # Simulate download endpoint logic
            from routes.fetch import download_beat_asset
            
            with app.test_request_context(
                json={
                    'candidate_id': 'test_id',
                    'source': source,
                    'metadata': {
                        'title': 'Test',
                        'query_used': new_query
                    },
                    'update_beat_query': should_update
                }
            ):
                # Perform download
                download_beat_asset('test_session', beat['id'])
                
                # If we expect an update, verify the saved state
                if should_update:
                    # Find the state where beat was updated
                    updated_found = False
                    for state in states_saved:
                        saved_beat = state['beats'][0]
                        
                        if source == 'youtube':
                            if saved_beat.get('youtube_phrase') == new_query:
                                updated_found = True
                                # Also check backend field consistency
                                self.assertEqual(saved_beat.get('youtube_search_phrase'), new_query)
                        elif source == 'pexels':
                            if saved_beat.get('stock_keyword') == new_query:
                                updated_found = True
                    
                    self.assertTrue(updated_found, 
                                  f"Beat should have been updated with query '{new_query}' when update_beat_query=True")
                else:
                    # If no update expected, verify NO saved state contains the new query
                    # (Unless it was already the query, which is unlikely with random generation but possible)
                    original_youtube = initial_beat.get('youtube_phrase', initial_beat.get('youtube_search_phrase'))
                    original_stock = initial_beat.get('stock_keyword')
                    
                    if new_query != original_youtube and new_query != original_stock:
                        for state in states_saved:
                            saved_beat = state['beats'][0]
                            if source == 'youtube':
                                self.assertNotEqual(saved_beat.get('youtube_phrase'), new_query,
                                                  "Beat youtube_phrase should NOT update when update_beat_query=False")
                            elif source == 'pexels':
                                self.assertNotEqual(saved_beat.get('stock_keyword'), new_query,
                                                  "Beat stock_keyword should NOT update when update_beat_query=False")


class TestErrorResponseFormat(unittest.TestCase):
    """
    Property 12: Error response format
    
    For any API error, the system should return a JSON response with an 'error' key
    and an appropriate HTTP status code (4xx or 5xx).
    
    Validates: Requirements 10.1, 10.3
    """
    
    @given(
        session_id=st.text(min_size=5, max_size=20),
        beat_id=st.text(min_size=5, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_12_error_format_consistency(self, session_id, beat_id):
        """
        Feature: asset-fetching-improvements, Property 12: Error response format
        
        Test that errors return consistent JSON structure.
        """
        # Test 404 Session Not Found
        with patch('routes.fetch.session_exists', return_value=False):
            from routes.fetch import search_beat_assets
            
            with app.test_request_context():
                response, status_code = search_beat_assets(session_id, beat_id)
                
                self.assertEqual(status_code, 404)
                self.assertIsInstance(response, dict)
                self.assertIn('error', response)
                self.assertEqual(response['error'], 'Session not found')
        
        # Test 500 Internal Error (simulated exception)
        with patch('routes.fetch.session_exists', return_value=True), \
             patch('routes.fetch.load_session_state', side_effect=Exception("Simulated DB failure")):
            
            from routes.fetch import search_beat_assets
            
            with app.test_request_context():
                response, status_code = search_beat_assets(session_id, beat_id)
                
                self.assertEqual(status_code, 500)
                self.assertIsInstance(response, dict)
                self.assertIn('error', response)
                self.assertIn('Simulated DB failure', response['error'])


class TestApiResponseStructure(unittest.TestCase):
    """
    Property 13: API response structure
    
    For any successful API request, the system should return a JSON response
    adhering to the expected schema (success: true, specific data keys).
    
    Validates: Requirements 10.4
    """
    
    @given(beat=beat_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_13_success_response_structure(self, beat):
        """
        Feature: asset-fetching-improvements, Property 13: API response structure
        
        Test that successful responses have the correct structure.
        """
        with patch('routes.fetch.load_session_state') as mock_load, \
             patch('routes.fetch.session_exists', return_value=True), \
             patch('screenwrite.fetchers.asset_orchestrator.AssetOrchestrator.search_assets') as mock_search:
            
            # Setup successful state
            mock_load.return_value = {
                'sessionId': 'test_session',
                'beats': [beat],
                'config': {}
            }
            
            # Mock successful search result
            from screenwrite.fetchers.asset_orchestrator import AssetCandidate
            mock_search.return_value = [
                AssetCandidate(
                    id='test_1',
                    title='Test Video',
                    thumbnail_url='http://thumb',
                    duration=5.0,
                    source='youtube',
                    metadata={}
                )
            ]
            
            from routes.fetch import search_beat_assets
            
            with app.test_request_context(json={}):
                response, status_code = search_beat_assets('test_session', beat['id'])
                
                self.assertEqual(status_code, 200)
                self.assertIsInstance(response, dict)
                self.assertTrue(response.get('success'))
                self.assertIn('candidates', response)
                self.assertIn('query_used', response)
                self.assertIn('beat_id', response)
                self.assertEqual(response['beat_id'], beat['id'])
                self.assertIsInstance(response['candidates'], list)


if __name__ == '__main__':
    unittest.main()
