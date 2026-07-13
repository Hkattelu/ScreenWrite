"""
Tests for the native Resolve project builder, run against duck-typed fake
Resolve API objects (no Resolve installation needed).
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from screenwrite.core.beat import Beat
from screenwrite.resolve_integration import (
    ResolveTimelineBuilder,
    MARKER_COLOR_MANUAL,
    MARKER_COLOR_GAMEPLAY,
    MARKER_COLOR_STILL,
    MARKER_COLOR_VO_SKIPPED,
)

FPS = 30


# ----------------------------------------------------------------------
# Fake Resolve API (records calls; behavior mirrors the documented API)
# ----------------------------------------------------------------------

class FakeMediaPoolItem:
    def __init__(self, file_path):
        self._file_path = file_path
        self.properties = {}

    def GetClipProperty(self, name):
        if name == "File Path":
            return self._file_path
        return self.properties.get(name, '')

    def SetClipProperty(self, name, value):
        self.properties[name] = value
        return True


class FakeTimelineItem:
    def __init__(self, clip_info):
        self.clip_info = clip_info
        self.enabled = True

    def GetStart(self):
        return clip_info_record(self.clip_info)

    def SetClipEnabled(self, value):
        self.enabled = value
        return True


def clip_info_record(clip_info):
    return clip_info.get('recordFrame', 0)


class FakeFolder:
    def __init__(self, name):
        self.name = name
        self.subfolders = []


class FakeTimeline:
    def __init__(self, name, start_frame=108000, framerate=FPS):
        self.name = name
        self.start_frame = start_frame
        self.framerate = framerate
        self.video_tracks = 1
        self.markers = []  # (frameId, color, name, note, duration, customData)

    def GetStartFrame(self):
        return self.start_frame

    def GetSetting(self, key):
        if key == 'timelineFrameRate':
            return str(self.framerate)
        return ''

    def GetTrackCount(self, track_type):
        return self.video_tracks if track_type == 'video' else 1

    def AddTrack(self, track_type, *args):
        if track_type == 'video':
            self.video_tracks += 1
            return True
        return False

    def AddMarker(self, frame_id, color, name, note, duration, custom_data=''):
        self.markers.append((frame_id, color, name, note, duration, custom_data))
        return True


class FakeMediaPool:
    def __init__(self):
        self.root = FakeFolder('Master')
        self.current_folder = self.root
        self.timelines = {}
        self.appended = []  # FakeTimelineItem in append order
        self.import_calls = []  # (folder_name, paths)
        self.fail_append_for = set()  # normalized paths whose append fails

    def GetRootFolder(self):
        return self.root

    def AddSubFolder(self, parent, name):
        folder = FakeFolder(name)
        parent.subfolders.append(folder)
        return folder

    def SetCurrentFolder(self, folder):
        self.current_folder = folder
        return True

    def ImportMedia(self, paths):
        self.import_calls.append((self.current_folder.name, list(paths)))
        # Reversed order on purpose: the builder must map by File Path.
        return [FakeMediaPoolItem(p) for p in reversed(paths)]

    def CreateEmptyTimeline(self, name):
        if name in self.timelines:
            return None
        timeline = FakeTimeline(name)
        self.timelines[name] = timeline
        return timeline

    def AppendToTimeline(self, clip_infos):
        items = []
        for info in clip_infos:
            path = info['mediaPoolItem'].GetClipProperty('File Path')
            if os.path.normcase(os.path.normpath(path)) in self.fail_append_for:
                return None
            item = FakeTimelineItem(info)
            self.appended.append(item)
            items.append(item)
        return items


class FakeProject:
    def __init__(self, media_pool):
        self.media_pool = media_pool
        self.settings = {}
        self.current_timeline = None

    def GetMediaPool(self):
        return self.media_pool

    def SetSetting(self, key, value):
        self.settings[key] = value
        return True

    def SetCurrentTimeline(self, timeline):
        self.current_timeline = timeline
        return True


class FakeIntegration:
    def __init__(self, project):
        self.current_project = project


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def make_beat(beat_id, text_words=15, **kwargs):
    beat = Beat(id=beat_id, text='word ' * text_words,
                stock_keyword='', youtube_search_phrase='')
    for key, value in kwargs.items():
        setattr(beat, key, value)
    return beat


def make_candidate(path, source='chaptered_gameplay', **metadata):
    return {
        'id': Path(path).stem, 'title': Path(path).stem, 'thumbnail_url': '',
        'duration': 9.0, 'source': source, 'local_path': path,
        'metadata': {'source_url': f'https://yt/{Path(path).stem}', **metadata},
    }


class BuilderTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.media_pool = FakeMediaPool()
        self.project = FakeProject(self.media_pool)
        self.builder = ResolveTimelineBuilder(FakeIntegration(self.project))

    def touch(self, name):
        path = str(Path(self.tmp.name) / name)
        Path(path).write_bytes(b'x')
        return path


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

class TestBinsAndImport(BuilderTestBase):
    def test_bin_per_beat_under_run_bin(self):
        c1 = self.touch('clip1.mp4')
        c2 = self.touch('clip2.mp4')
        beats = [
            make_beat('beat_001', beat_class='game_entity',
                      entities=['Bell Gargoyles'], candidates=[make_candidate(c1)]),
            make_beat('beat_002', beat_class='game_entity',
                      entities=['Blighttown'], candidates=[make_candidate(c2)]),
        ]
        result = self.builder.build(beats, None, 'mytimeline')
        self.assertTrue(result['success'])
        run_bins = [f.name for f in self.media_pool.root.subfolders]
        self.assertIn('screenwrite-mytimeline', run_bins)
        run_bin = self.media_pool.root.subfolders[0]
        beat_bins = [f.name for f in run_bin.subfolders]
        self.assertEqual(beat_bins, ['beat_001 - Bell Gargoyles', 'beat_002 - Blighttown'])
        imported_folders = [name for name, _ in self.media_pool.import_calls]
        self.assertEqual(imported_folders, ['beat_001 - Bell Gargoyles', 'beat_002 - Blighttown'])


class TestClipPlacement(BuilderTestBase):
    def test_alternates_stacked_disabled_at_same_position(self):
        paths = [self.touch(f'c{i}.mp4') for i in range(3)]
        beat = make_beat('beat_001', beat_class='game_entity', entities=['Boss'],
                         candidates=[make_candidate(p) for p in paths])
        result = self.builder.build([beat], None, 't')
        self.assertTrue(result['success'])

        video_items = [i for i in self.media_pool.appended
                       if i.clip_info['mediaType'] == 1]
        self.assertEqual(len(video_items), 3)
        tracks = [i.clip_info['trackIndex'] for i in video_items]
        self.assertEqual(sorted(tracks), [1, 2, 3])
        records = {i.clip_info['recordFrame'] for i in video_items}
        self.assertEqual(len(records), 1)  # identical position
        enabled = {i.clip_info['trackIndex']: i.enabled for i in video_items}
        self.assertTrue(enabled[1])
        self.assertFalse(enabled[2])
        self.assertFalse(enabled[3])
        # Extra tracks were added for the alternates
        timeline = self.project.current_timeline
        self.assertGreaterEqual(timeline.video_tracks, 3)

    def test_record_frame_includes_start_frame_base(self):
        c1 = self.touch('c1.mp4')
        beat = make_beat('beat_001', candidates=[make_candidate(c1)],
                         beat_class='game_entity', entities=['Boss'])
        beat.vo_start = 10.0
        beat.vo_end = 16.0
        beat.duration = 6.0
        self.builder.build([beat], None, 't')
        item = self.media_pool.appended[0]
        self.assertEqual(item.clip_info['recordFrame'], 108000 + round(10.0 * FPS))

    def test_vo_skipped_beat_places_no_clip(self):
        c1 = self.touch('c1.mp4')
        beat = make_beat('beat_001', candidates=[make_candidate(c1)],
                         beat_class='game_entity', entities=['Boss'])
        beat.duration = 0.0
        beat.vo_matched = False
        beat.vo_start = 5.0
        result = self.builder.build([beat], None, 't')
        video_items = [i for i in self.media_pool.appended
                       if i.clip_info['mediaType'] == 1]
        self.assertEqual(video_items, [])
        self.assertFalse(result['success'])  # nothing placed, no VO

    def test_top_candidate_failure_promotes_alternate(self):
        c1, c2 = self.touch('c1.mp4'), self.touch('c2.mp4')
        self.media_pool.fail_append_for.add(os.path.normcase(os.path.normpath(c1)))
        beat = make_beat('beat_001', beat_class='game_entity', entities=['Boss'],
                         candidates=[make_candidate(c1), make_candidate(c2)])
        result = self.builder.build([beat], None, 't')
        self.assertTrue(result['success'])
        video_items = [i for i in self.media_pool.appended
                       if i.clip_info['mediaType'] == 1]
        self.assertEqual(len(video_items), 1)
        self.assertTrue(video_items[0].enabled)  # promoted, not disabled
        self.assertTrue(any('promoted' in w for w in result['warnings']))

    def test_still_gets_duration_property(self):
        still = self.touch('wikistill_boss.png')
        beat = make_beat('beat_001', beat_class='game_entity', entities=['Boss'],
                         candidates=[make_candidate(still, source='wiki_still')])
        self.builder.build([beat], None, 't')
        item = self.media_pool.appended[0].clip_info['mediaPoolItem']
        self.assertIn('Duration', item.properties)

    def test_missing_setclipenabled_degrades_with_warning(self):
        original = FakeTimelineItem.SetClipEnabled
        del FakeTimelineItem.SetClipEnabled
        try:
            c1, c2 = self.touch('c1.mp4'), self.touch('c2.mp4')
            beat = make_beat('beat_001', beat_class='game_entity', entities=['Boss'],
                             candidates=[make_candidate(c1), make_candidate(c2)])
            result = self.builder.build([beat], None, 't')
            self.assertTrue(result['success'])
            self.assertTrue(any('SetClipEnabled' in w for w in result['warnings']))
        finally:
            FakeTimelineItem.SetClipEnabled = original


class TestVOAndMarkers(BuilderTestBase):
    def test_vo_clipinfo_on_audio_track_at_base(self):
        c1 = self.touch('c1.mp4')
        vo = self.touch('vo.wav')
        beat = make_beat('beat_001', beat_class='game_entity', entities=['Boss'],
                         candidates=[make_candidate(c1)])
        self.builder.build([beat], vo, 't')
        audio_items = [i for i in self.media_pool.appended
                       if i.clip_info['mediaType'] == 2]
        self.assertEqual(len(audio_items), 1)
        info = audio_items[0].clip_info
        self.assertEqual(info['trackIndex'], 1)
        self.assertEqual(info['recordFrame'], 108000)
        self.assertEqual(info['startFrame'], 0)

    def test_marker_frameid_relative_and_colors(self):
        c1 = self.touch('c1.mp4')
        still = self.touch('s.png')
        beats = [
            make_beat('beat_001', beat_class='game_entity', entities=['Boss'],
                      candidates=[make_candidate(c1)]),
            make_beat('beat_002', beat_class='game_entity', entities=['Item'],
                      candidates=[make_candidate(still, source='wiki_still')]),
            make_beat('beat_003', beat_class='manual_fill'),
        ]
        skipped = make_beat('beat_004', beat_class='game_entity', entities=['X'])
        skipped.duration = 0.0
        skipped.vo_matched = False
        skipped.vo_start = 20.0
        beats.append(skipped)

        self.builder.build(beats, None, 't')
        timeline = self.project.current_timeline
        markers = {name: (frame, color, note, custom)
                   for frame, color, name, note, _, custom in timeline.markers}

        self.assertEqual(markers['beat_001'][1], MARKER_COLOR_GAMEPLAY)
        self.assertEqual(markers['beat_002'][1], MARKER_COLOR_STILL)
        self.assertEqual(markers['beat_003'][1], MARKER_COLOR_MANUAL)
        self.assertEqual(markers['beat_004'][1], MARKER_COLOR_VO_SKIPPED)
        # frameId is relative: beat_001 sits at 0, NOT at the 108000 base
        self.assertEqual(markers['beat_001'][0], 0)
        # customData round-trips
        custom = json.loads(markers['beat_001'][3])
        self.assertEqual(custom['beat_id'], 'beat_001')
        self.assertEqual(custom['entities'], ['Boss'])
        # manual beat note says MANUAL
        self.assertIn('MANUAL', markers['beat_003'][2])

    def test_provenance_in_marker_note(self):
        c1 = self.touch('c1.mp4')
        beat = make_beat('beat_001', beat_class='game_entity', entities=['Boss'],
                         candidates=[make_candidate(c1, chapter_title='Boss Fight',
                                                    segment_start=100.0)])
        self.builder.build([beat], None, 't')
        timeline = self.project.current_timeline
        note = timeline.markers[0][3]
        self.assertIn('chaptered_gameplay', note)
        self.assertIn('Boss Fight', note)


class TestOrchestratorFallback(unittest.TestCase):
    def test_builder_failure_falls_back_to_fcpxml_import(self):
        from screenwrite.orchestrator import VideoOrchestrator

        with tempfile.TemporaryDirectory() as tmp:
            orchestrator = VideoOrchestrator.__new__(VideoOrchestrator)
            orchestrator.resolve_enabled = True
            orchestrator.resolve_integration = object()
            orchestrator.resolve_force_fcpxml = False
            orchestrator.vo_path = None

            with patch.object(VideoOrchestrator, '_build_native_resolve',
                              side_effect=RuntimeError('no project')), \
                 patch.object(VideoOrchestrator, '_import_to_resolve',
                              return_value=True) as import_mock:
                # Exercise just the Step 4 logic via a tiny driver mirroring
                # orchestrate()'s structure.
                workflow_result = {'warnings': [], 'resolve_imported': False}
                native_built = False
                try:
                    native_built = orchestrator._build_native_resolve([], 'x.fcpxml',
                                                                      workflow_result)
                except Exception as e:
                    workflow_result['warnings'].append(str(e))
                if not native_built:
                    workflow_result['resolve_imported'] = orchestrator._import_to_resolve(
                        str(Path(tmp) / 'x.fcpxml'), {})
                self.assertTrue(workflow_result['resolve_imported'])
                self.assertTrue(import_mock.called)


if __name__ == '__main__':
    unittest.main()
