"""
Tests for the persistent per-game footage library and its integration with
the chaptered gameplay fetcher (no network).
"""

import tempfile
import threading
import unittest
from pathlib import Path

from screenwrite.utils.game_library import GameLibrary, CHAPTER_INDEX_TTL_HOURS
from screenwrite.fetchers.chaptered_gameplay_fetcher import ChapteredGameplayFetcher


class LibraryTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.library = GameLibrary('Dark Souls', root=Path(self.tmp.name))


class TestChapterIndexCache(LibraryTestBase):
    INDEX = [{'video_id': 'v1', 'title': 'Longplay', 'url': 'u', 'thumbnail_url': '',
              'duration': 3600, 'chapters': [{'title': 'Boss', 'start_time': 1.0,
                                              'end_time': 2.0}]}]

    def test_round_trip(self):
        self.assertIsNone(self.library.load_chapter_index())
        self.library.save_chapter_index(self.INDEX)
        loaded = self.library.load_chapter_index()
        self.assertEqual(loaded, self.INDEX)

    def test_ttl_expiry(self):
        self.library.save_chapter_index(self.INDEX)
        # An index older than the TTL is treated as absent
        self.assertIsNone(self.library.load_chapter_index(ttl_hours=0))
        self.assertIsNotNone(self.library.load_chapter_index(ttl_hours=CHAPTER_INDEX_TTL_HOURS))

    def test_slug_isolation_per_game(self):
        other = GameLibrary('Elden Ring', root=Path(self.tmp.name))
        self.library.save_chapter_index(self.INDEX)
        self.assertIsNone(other.load_chapter_index())


class TestClipStore(LibraryTestBase):
    def test_store_and_find(self):
        source = Path(self.tmp.name) / 'downloaded.mp4'
        source.write_bytes(b'video-bytes')
        self.assertIsNone(self.library.find_clip('v1', 100.0, 9.0))

        stored = self.library.store_clip(str(source), 'v1', 100.0, 9.0)
        self.assertNotEqual(stored, str(source))
        self.assertTrue(Path(stored).exists())
        self.assertEqual(self.library.find_clip('v1', 100.0, 9.0), stored)
        # Different window is a different clip
        self.assertIsNone(self.library.find_clip('v1', 100.0, 12.0))

    def test_find_ignores_missing_file(self):
        source = Path(self.tmp.name) / 'downloaded.mp4'
        source.write_bytes(b'x')
        stored = self.library.store_clip(str(source), 'v1', 5.0, 9.0)
        Path(stored).unlink()
        self.assertIsNone(self.library.find_clip('v1', 5.0, 9.0))

    def test_clip_key_matches_fetcher_format(self):
        self.assertEqual(GameLibrary.clip_key('abc', 4670.9, 9.4), 'abc@4670+9')


class TestSourceStats(LibraryTestBase):
    def test_ratio_math(self):
        self.assertEqual(self.library.success_ratio('v1'), 0.5)  # unseen
        self.library.record_result('v1', ok=True)
        self.library.record_result('v1', ok=True)
        self.library.record_result('v1', ok=False)
        self.assertAlmostEqual(self.library.success_ratio('v1'), 2 / 3)
        self.library.record_result('v2', ok=False)
        self.assertEqual(self.library.success_ratio('v2'), 0.0)

    def test_concurrent_writes_do_not_corrupt(self):
        def hammer(video_id):
            for _ in range(20):
                self.library.record_result(video_id, ok=True)

        threads = [threading.Thread(target=hammer, args=(f'v{i}',)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        for i in range(4):
            self.assertEqual(self.library.success_ratio(f'v{i}'), 1.0)


class TestFetcherIntegration(unittest.TestCase):
    def _fetcher(self, library, chapters):
        fetcher = ChapteredGameplayFetcher.__new__(ChapteredGameplayFetcher)
        fetcher.game = 'Dark Souls'
        fetcher.library = library
        fetcher._chapter_index = [{
            'video_id': vid, 'title': f'video {vid}', 'url': f'https://yt/{vid}',
            'thumbnail_url': '', 'duration': 3600, 'chapters': chs,
        } for vid, chs in chapters.items()]
        fetcher._index_lock = threading.Lock()
        fetcher._download_cache = {}
        fetcher._download_lock = threading.Lock()
        return fetcher

    def test_equal_score_prefers_successful_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = GameLibrary('Dark Souls', root=Path(tmp))
            library.record_result('good', ok=True)
            library.record_result('bad', ok=False)
            chapter = [{'title': 'Bell Gargoyles', 'start_time': 10.0, 'end_time': 200.0}]
            fetcher = self._fetcher(library, {'bad': chapter, 'good': list(chapter)})

            matches = fetcher.match_chapters('Bell Gargoyles')
            self.assertEqual([m['video_id'] for m in matches][:2], ['good', 'bad'])

    def test_download_segment_served_from_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = GameLibrary('Dark Souls', root=Path(tmp))
            clip = Path(tmp) / 'clip.mp4'
            clip.write_bytes(b'video')
            stored = library.store_clip(str(clip), 'v1', 100.0, 9.0)

            fetcher = self._fetcher(library, {})

            class ExplodingYouTube:
                def download_section(self, *a, **k):
                    raise AssertionError('network must not be hit on library hit')

            fetcher.youtube_client = ExplodingYouTube()
            path = fetcher.download_segment(
                'v1@100', {'video_id': 'v1'}, start_time=100.0, duration=9.0)
            self.assertEqual(path, stored)

    def test_download_failure_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = GameLibrary('Dark Souls', root=Path(tmp))
            fetcher = self._fetcher(library, {})

            class FailingYouTube:
                def download_section(self, *a, **k):
                    return None

            fetcher.youtube_client = FailingYouTube()
            path = fetcher.download_segment(
                'v1@100', {'video_id': 'v1'}, start_time=100.0, duration=9.0)
            self.assertIsNone(path)
            self.assertEqual(library.success_ratio('v1'), 0.0)

    def test_chapter_index_persisted_through_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = GameLibrary('Dark Souls', root=Path(tmp))
            index = [{'video_id': 'v1', 'title': 't', 'url': 'u', 'thumbnail_url': '',
                      'duration': 100, 'chapters': []}]
            fetcher = self._fetcher(library, {})
            fetcher._chapter_index = None
            fetcher._build_chapter_index = lambda: index

            self.assertEqual(fetcher.get_chapter_index(), index)
            # Second fetcher (new run) loads from the library without building
            fetcher2 = self._fetcher(library, {})
            fetcher2._chapter_index = None
            fetcher2._build_chapter_index = lambda: self.fail('must load from library')
            self.assertEqual(fetcher2.get_chapter_index(), index)


if __name__ == '__main__':
    unittest.main()
