"""
Tests for the game b-roll skeleton pipeline: chapter matching, candidate
generation, entity extraction parsing, beat_class routing, and FCPXML
provenance markers / manual-fill placeholders.

Everything network-facing is stubbed - these tests exercise the matching,
routing, and generation logic only.
"""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from screenwrite.core.beat import Beat
from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator
from screenwrite.fetchers.chaptered_gameplay_fetcher import (
    ChapteredGameplayFetcher,
    chapter_match_score,
    clip_window_seconds,
    normalize_title,
)
from screenwrite.fetchers.wiki_still_fetcher import guess_wiki_subdomains
from screenwrite.generators.xml_generator import XMLGenerator
from screenwrite.parsing.entity_extractor import EntityExtractor
from screenwrite.config import (
    CHAPTER_MATCH_THRESHOLD,
    CHAPTER_OFFSET_STEP_SECONDS,
    CHAPTER_WINDOW_MIN_SECONDS,
)


def make_beat(beat_id='beat_001', words=15, **kwargs):
    """Build a valid Beat (word count sets duration; 15 words = 6s)."""
    beat = Beat(
        id=beat_id,
        text='word ' * words,
        stock_keyword=kwargs.pop('stock_keyword', 'stock query'),
        youtube_search_phrase='youtube query',
    )
    for key, value in kwargs.items():
        setattr(beat, key, value)
    return beat


class TestChapterMatching(unittest.TestCase):
    """Fuzzy entity-vs-chapter-title matching."""

    def test_exact_title_matches(self):
        self.assertEqual(chapter_match_score('Bell Gargoyles', 'Bell Gargoyles'), 100.0)

    def test_decorated_chapter_title_matches(self):
        # Real chapter labels decorate names with noise like "(Boss Fight)".
        score = chapter_match_score('Bell Gargoyles', 'Bell Gargoyles (Boss Fight)')
        self.assertEqual(score, 100.0)

    def test_punctuation_and_case_normalized(self):
        score = chapter_match_score('Gwyn Lord of Cinder', 'Gwyn, Lord of Cinder (Final Boss)')
        self.assertEqual(score, 100.0)

    def test_unrelated_title_scores_low(self):
        score = chapter_match_score('Bell Gargoyles', 'Blighttown Swamp')
        self.assertLess(score, CHAPTER_MATCH_THRESHOLD)

    def test_empty_inputs_score_zero(self):
        self.assertEqual(chapter_match_score('', 'Anor Londo'), 0.0)
        self.assertEqual(chapter_match_score('Anor Londo', ''), 0.0)

    def test_normalize_title(self):
        self.assertEqual(normalize_title("Gwyn, Lord of Cinder!"), 'gwyn lord of cinder')

    def test_clip_window_has_floor_and_slack(self):
        self.assertEqual(clip_window_seconds(3.0), CHAPTER_WINDOW_MIN_SECONDS)
        self.assertGreater(clip_window_seconds(10.0), 10.0)


class TestChapteredCandidates(unittest.TestCase):
    """Candidate generation from a pre-built chapter index (no network)."""

    def _fetcher_with_index(self, chapters, video_id='vid1'):
        fetcher = ChapteredGameplayFetcher.__new__(ChapteredGameplayFetcher)
        fetcher.game = 'Dark Souls'
        fetcher._chapter_index = [{
            'video_id': video_id,
            'title': 'Dark Souls Longplay',
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail_url': '',
            'duration': 3600,
            'chapters': chapters,
        }]
        import threading
        fetcher._index_lock = threading.Lock()
        fetcher._download_cache = {}
        fetcher._download_lock = threading.Lock()
        return fetcher

    def test_multi_offset_candidates_within_one_chapter(self):
        fetcher = self._fetcher_with_index([
            {'title': 'Bell Gargoyles (Boss)', 'start_time': 1000.0, 'end_time': 1100.0},
        ])
        candidates = fetcher.search('Bell Gargoyles', count=3)
        self.assertEqual(len(candidates), 3)
        starts = [c['segment_start'] for c in candidates]
        self.assertEqual(starts, [1000.0,
                                  1000.0 + CHAPTER_OFFSET_STEP_SECONDS,
                                  1000.0 + 2 * CHAPTER_OFFSET_STEP_SECONDS])
        for candidate in candidates:
            self.assertEqual(candidate['chapter_title'], 'Bell Gargoyles (Boss)')
            self.assertIn('t=', candidate['source_url'])
            self.assertEqual(candidate['game'], 'Dark Souls')
            self.assertEqual(candidate['entity'], 'Bell Gargoyles')

    def test_candidates_diversify_across_chapters_first(self):
        fetcher = self._fetcher_with_index([
            {'title': 'Anor Londo', 'start_time': 100.0, 'end_time': 400.0},
            {'title': 'Back to Anor Londo', 'start_time': 2000.0, 'end_time': 2400.0},
        ])
        candidates = fetcher.search('Anor Londo', count=3)
        self.assertEqual(len(candidates), 3)
        # First two candidates come from the two different chapters (offset 0),
        # third is the second offset of the first chapter.
        self.assertEqual(candidates[0]['segment_start'], 100.0)
        self.assertEqual(candidates[1]['segment_start'], 2000.0)
        self.assertEqual(candidates[2]['segment_start'], 100.0 + CHAPTER_OFFSET_STEP_SECONDS)

    def test_short_chapter_still_yields_offset_zero(self):
        # Chapter shorter than the clip window: offset 0 must still be allowed.
        fetcher = self._fetcher_with_index([
            {'title': 'Capra Demon (Boss)', 'start_time': 500.0, 'end_time': 504.0},
        ])
        candidates = fetcher.search('Capra Demon', count=3)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]['segment_start'], 500.0)

    def test_no_match_returns_empty(self):
        fetcher = self._fetcher_with_index([
            {'title': 'Blighttown', 'start_time': 0.0, 'end_time': 600.0},
        ])
        self.assertEqual(fetcher.search('Ornstein and Smough', count=3), [])


class TestEntityExtractorParsing(unittest.TestCase):
    """Response parsing and class/entity consistency rules (no API calls)."""

    def setUp(self):
        self.extractor = EntityExtractor(api_key='test-key')

    def test_parses_valid_response(self):
        raw = ('[{"id": "beat_001", "beat_class": "game_entity", '
               '"entities": ["Bell Gargoyles"]},'
               '{"id": "beat_002", "beat_class": "abstract", "entities": []}]')
        result = self.extractor._parse_response(raw)
        self.assertEqual(result['beat_001']['beat_class'], 'game_entity')
        self.assertEqual(result['beat_001']['entities'], ['Bell Gargoyles'])
        self.assertEqual(result['beat_002']['beat_class'], 'abstract')

    def test_game_entity_without_entities_demoted_to_abstract(self):
        raw = '[{"id": "beat_001", "beat_class": "game_entity", "entities": []}]'
        result = self.extractor._parse_response(raw)
        self.assertEqual(result['beat_001']['beat_class'], 'abstract')

    def test_invalid_class_with_entities_becomes_game_entity(self):
        raw = '[{"id": "beat_001", "beat_class": "boss_fight", "entities": ["Gwyn"]}]'
        result = self.extractor._parse_response(raw)
        self.assertEqual(result['beat_001']['beat_class'], 'game_entity')

    def test_strips_code_fences(self):
        raw = '```json\n[{"id": "b1", "beat_class": "manual_fill", "entities": []}]\n```'
        result = self.extractor._parse_response(raw)
        self.assertEqual(result['b1']['beat_class'], 'manual_fill')

    def test_garbage_returns_none(self):
        self.assertIsNone(self.extractor._parse_response('not json at all'))
        self.assertIsNone(self.extractor._parse_response(''))

    def test_unavailable_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            extractor = EntityExtractor()
            self.assertFalse(extractor.is_available())
            self.assertIsNone(extractor.extract([{'id': 'b1', 'text': 'x'}], 'Dark Souls'))


class TestGameRouting(unittest.TestCase):
    """beat_class-driven cascade in AssetOrchestrator (fetchers stubbed)."""

    def _orchestrator(self):
        orchestrator = AssetOrchestrator.__new__(AssetOrchestrator)
        orchestrator.output_dir = None
        orchestrator.prefer_stock_for_generic = True
        orchestrator.game = 'Dark Souls'
        orchestrator.fetchers = []
        orchestrator.chaptered_fetcher = None
        orchestrator.wiki_fetcher = None
        return orchestrator

    def test_manual_fill_never_fetches(self):
        orchestrator = self._orchestrator()
        beat = make_beat(beat_class='manual_fill')
        self.assertEqual(orchestrator._fetch_for_game_beat(beat, 3), [])
        self.assertEqual(beat.candidates, [])

    def test_game_entity_uses_chaptered_clips(self):
        orchestrator = self._orchestrator()

        class FakeChaptered:
            def search(self, entity, count=3):
                return [{'id': f'vid@{i}', 'title': f'c{i}', 'thumbnail_url': '',
                         'duration': 9.0, 'segment_start': i * 8.0,
                         'source_url': f'https://yt/v?t={i * 8}'} for i in range(count)]

            def download_by_id(self, asset_id, metadata, target_duration=None,
                               progress_callback=None):
                return f"/tmp/{asset_id.replace('@', '_')}.mp4"

        orchestrator.chaptered_fetcher = FakeChaptered()
        beat = make_beat(beat_class='game_entity', entities=['Bell Gargoyles'])
        paths = orchestrator._fetch_for_game_beat(beat, 3)
        self.assertEqual(len(paths), 3)
        self.assertEqual(len(beat.candidates), 3)
        self.assertTrue(all(c['source'] == 'chaptered_gameplay' for c in beat.candidates))
        self.assertTrue(all(c['local_path'] for c in beat.candidates))

    def test_game_entity_falls_back_to_wiki_still(self):
        orchestrator = self._orchestrator()

        class NoClipChaptered:
            def search(self, entity, count=3):
                return []

        class FakeWiki:
            def search(self, entity, count=1):
                return [{'id': '42', 'title': entity, 'thumbnail_url': '',
                         'image_url': 'https://img', 'page_url': 'https://wiki/page',
                         'source_url': 'https://wiki/page'}]

            def download_by_id(self, asset_id, metadata, target_duration=None,
                               progress_callback=None):
                return '/tmp/still.png'

        orchestrator.chaptered_fetcher = NoClipChaptered()
        orchestrator.wiki_fetcher = FakeWiki()
        beat = make_beat(beat_class='game_entity', entities=['Bell Gargoyles'])
        paths = orchestrator._fetch_for_game_beat(beat, 3)
        self.assertEqual(paths, ['/tmp/still.png'])
        self.assertEqual(beat.candidates[0]['source'], 'wiki_still')

    def test_game_entity_with_no_coverage_flags_manual(self):
        orchestrator = self._orchestrator()

        class Empty:
            def search(self, entity, count=3):
                return []

        orchestrator.chaptered_fetcher = Empty()
        orchestrator.wiki_fetcher = Empty()
        beat = make_beat(beat_class='game_entity', entities=['Bell Gargoyles'])
        self.assertEqual(orchestrator._fetch_for_game_beat(beat, 3), [])
        self.assertEqual(beat.candidates, [])

    def test_abstract_beat_gets_single_stock_candidate(self):
        orchestrator = self._orchestrator()

        class FakePexels:
            name = 'Pexels'

            def search(self, query, count=1):
                return [{'id': 'p1', 'title': 'calm scenery', 'thumbnail_url': '',
                         'duration': 12.0}]

            def download_by_id(self, asset_id, metadata, target_duration=None,
                               progress_callback=None):
                return '/tmp/stock.mp4'

        orchestrator.fetchers = [FakePexels()]
        beat = make_beat(beat_class='abstract')
        paths = orchestrator._fetch_for_game_beat(beat, 3)
        self.assertEqual(paths, ['/tmp/stock.mp4'])
        self.assertEqual(len(beat.candidates), 1)
        self.assertEqual(beat.candidates[0]['source'], 'pexels')

    def test_abstract_beat_never_routes_to_game_fetchers(self):
        orchestrator = self._orchestrator()

        class Exploding:
            def search(self, entity, count=3):
                raise AssertionError('game fetcher must not be called for abstract beats')

        orchestrator.chaptered_fetcher = Exploding()
        orchestrator.wiki_fetcher = Exploding()
        beat = make_beat(beat_class='abstract')
        # No pexels fetcher configured -> manual flag, but no game fetch calls.
        self.assertEqual(orchestrator._fetch_for_game_beat(beat, 3), [])

    def test_fetcher_for_source_normalizes_labels(self):
        orchestrator = self._orchestrator()

        class FakeChaptered:
            name = 'ChapteredGameplay'

        orchestrator.chaptered_fetcher = FakeChaptered()
        self.assertIs(orchestrator._fetcher_for_source('chaptered_gameplay'),
                      orchestrator.chaptered_fetcher)
        self.assertIsNone(orchestrator._fetcher_for_source('pexels'))


class TestWikiSubdomainGuess(unittest.TestCase):
    def test_guesses(self):
        self.assertEqual(guess_wiki_subdomains('Dark Souls'), ['darksouls', 'dark-souls'])
        self.assertEqual(guess_wiki_subdomains('Hades'), ['hades'])
        self.assertEqual(guess_wiki_subdomains(''), [])


class TestXMLGeneratorGameMode(unittest.TestCase):
    """Provenance markers and manual-fill placeholders in FCPXML."""

    def _generate(self, beats, asset_map):
        generator = XMLGenerator()
        with tempfile.TemporaryDirectory() as tmp:
            output = str(Path(tmp) / 'timeline.fcpxml')
            generator.generate(beats, asset_map, output)
            return ET.parse(output).getroot()

    def test_clip_marker_carries_provenance(self):
        beat = make_beat(beat_class='game_entity', entities=['Bell Gargoyles'])
        beat.candidates = [
            {
                'id': 'vid@1000', 'title': 'c', 'thumbnail_url': '', 'duration': 9.0,
                'source': 'chaptered_gameplay', 'local_path': '/tmp/clip1.mp4',
                'metadata': {
                    'chapter_title': 'Bell Gargoyles (Boss)',
                    'segment_start': 1000.0,
                    'source_url': 'https://www.youtube.com/watch?v=vid&t=1000',
                },
            },
            {
                'id': 'vid@1008', 'title': 'c2', 'thumbnail_url': '', 'duration': 9.0,
                'source': 'chaptered_gameplay', 'local_path': '/tmp/clip2.mp4',
                'metadata': {
                    'chapter_title': 'Bell Gargoyles (Boss)',
                    'segment_start': 1008.0,
                    'source_url': 'https://www.youtube.com/watch?v=vid&t=1008',
                },
            },
        ]
        root = self._generate([beat], {beat.id: ['/tmp/clip1.mp4', '/tmp/clip2.mp4']})

        clip = root.find('.//spine/asset-clip')
        self.assertIsNotNone(clip)
        marker = clip.find('marker')
        self.assertIsNotNone(marker)
        note = marker.get('note', '')
        self.assertIn('chaptered_gameplay', note)
        self.assertIn('Bell Gargoyles (Boss)', note)
        self.assertIn('@ 1000s', note)
        self.assertIn('https://www.youtube.com/watch?v=vid&t=1000', note)
        # The alternate stays reachable from inside the editor.
        self.assertIn('t=1008', note)

    def test_manual_fill_beat_gets_labeled_gap(self):
        beat = make_beat(beat_class='manual_fill')
        root = self._generate([beat], {beat.id: []})

        gap = root.find('.//spine/gap')
        self.assertIsNotNone(gap)
        self.assertIn('MANUAL FILL', gap.get('name', ''))
        marker = gap.find('marker')
        self.assertIsNotNone(marker)
        self.assertTrue(marker.get('value', '').startswith('MANUAL:'))

    def test_uncovered_game_entity_gap_names_entities(self):
        beat = make_beat(beat_class='game_entity', entities=['Ornstein and Smough'])
        root = self._generate([beat], {beat.id: []})

        gap = root.find('.//spine/gap')
        marker = gap.find('marker')
        self.assertIn('Ornstein and Smough', marker.get('note', ''))

    def test_legacy_beats_keep_plain_gaps(self):
        beat = make_beat()  # beat_class stays 'unclassified', no game
        root = self._generate([beat], {beat.id: None})

        gap = root.find('.//spine/gap')
        self.assertEqual(gap.get('name'), f'Gap - {beat.id}')
        self.assertIsNone(gap.find('marker'))

    def test_unclassified_gap_in_game_mode_labeled_manual(self):
        # In game mode every gap is intentional, even for beats the
        # classifier skipped - they must read as manual fill, not missing.
        beat = make_beat(game='Dark Souls')
        root = self._generate([beat], {beat.id: []})

        gap = root.find('.//spine/gap')
        self.assertIn('MANUAL FILL', gap.get('name', ''))
        self.assertIsNotNone(gap.find('marker'))

    def test_still_image_asset_has_no_audio(self):
        beat = make_beat(beat_class='game_entity', entities=['Bell Gargoyles'])
        beat.candidates = [{
            'id': '42', 'title': 'Still', 'thumbnail_url': '', 'duration': 0.0,
            'source': 'wiki_still', 'local_path': '/tmp/wikistill_Bell.png',
            'metadata': {'source_url': 'https://wiki/page', 'title': 'Bell Gargoyles'},
        }]
        root = self._generate([beat], {beat.id: ['/tmp/wikistill_Bell.png']})

        asset = root.find('.//resources/asset')
        self.assertEqual(asset.get('hasAudio'), '0')
        keyword = root.find('.//spine/asset-clip/keyword')
        self.assertIn('WikiStill', keyword.get('value', ''))


class TestScriptParserGameMode(unittest.TestCase):
    """Game resolution and classification wiring in the parser."""

    def _parse(self, content, game=None, extract_result=None):
        from screenwrite.parsing.script_parser import ScriptParser
        parser = ScriptParser(use_llm_queries=False, game=game)
        available = extract_result is not None
        with patch.object(parser.entity_extractor, 'is_available', return_value=available), \
             patch.object(parser.entity_extractor, 'extract', return_value=extract_result):
            with tempfile.TemporaryDirectory() as tmp:
                script = Path(tmp) / 'script.md'
                script.write_text(content, encoding='utf-8')
                return parser.parse(str(script), use_cache=False)

    def test_game_header_triggers_classification(self):
        content = (
            "title: My Essay\n"
            "game: Dark Souls\n\n"
            "The Bell Gargoyles are where the difficulty really bares its "
            "teeth and every player remembers that moment vividly forever.\n"
        )
        beats = self._parse(content, extract_result={
            'beat_001': {'beat_class': 'game_entity', 'entities': ['Bell Gargoyles']},
        })
        self.assertEqual(beats[0].game, 'Dark Souls')
        self.assertEqual(beats[0].beat_class, 'game_entity')
        self.assertEqual(beats[0].entities, ['Bell Gargoyles'])

    def test_cli_game_flag_wins_over_header(self):
        content = (
            "game: Dark Souls\n\n"
            "Some narration text that goes on long enough to form a full "
            "beat of at least thirteen words in total here.\n"
        )
        beats = self._parse(content, game='Elden Ring', extract_result={
            'beat_001': {'beat_class': 'abstract', 'entities': []},
        })
        self.assertEqual(beats[0].game, 'Elden Ring')

    def test_no_game_keeps_legacy_pipeline(self):
        content = (
            "title: My Essay\n\n"
            "Some narration text that goes on long enough to form a full "
            "beat of at least thirteen words in total here.\n"
        )
        beats = self._parse(content, extract_result=None)
        self.assertIsNone(beats[0].game)
        self.assertEqual(beats[0].beat_class, 'unclassified')

    def test_extractor_unavailable_leaves_unclassified(self):
        content = (
            "game: Dark Souls\n\n"
            "Some narration text that goes on long enough to form a full "
            "beat of at least thirteen words in total here.\n"
        )
        beats = self._parse(content, extract_result=None)
        self.assertEqual(beats[0].game, 'Dark Souls')
        self.assertEqual(beats[0].beat_class, 'unclassified')

    def test_inline_instruction_wins_over_extraction(self):
        content = (
            "game: Dark Souls\n\n"
            "[@Show: Ornstein and Smough boss arena] The duo fight in Anor "
            "Londo is the wall every player talks about endlessly for years.\n"
        )
        beats = self._parse(content, extract_result={})
        show_beats = [b for b in beats if b.visual_type == 'b-roll']
        self.assertEqual(len(show_beats), 1)
        self.assertEqual(show_beats[0].beat_class, 'game_entity')
        self.assertEqual(show_beats[0].entities, ['Ornstein and Smough boss arena'])


if __name__ == '__main__':
    unittest.main()
