"""
DaVinci Resolve integration module.

This module provides optional integration with DaVinci Resolve via fusionscript,
allowing automatic import of generated timelines and assets into Resolve projects.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import os

from .config import DEFAULT_FRAMERATE, STILL_IMAGE_EXTENSIONS
from .utils.provenance import build_provenance_note

logger = logging.getLogger(__name__)


def _bootstrap_resolve_script_import() -> None:
    """
    Make `import DaVinciResolveScript` work without manual env setup.

    Resolve ships the module outside site-packages; if it isn't already
    importable, append the platform-default Scripting/Modules directory to
    sys.path and point RESOLVE_SCRIPT_LIB at fusionscript. Existing env vars
    always win.
    """
    try:
        import DaVinciResolveScript  # noqa: F401
        return
    except ImportError:
        pass

    if sys.platform.startswith('win'):
        api_default = os.path.join(
            os.getenv('PROGRAMDATA', r'C:\ProgramData'),
            r'Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting')
        lib_default = (r'C:\Program Files\Blackmagic Design\DaVinci Resolve'
                       r'\fusionscript.dll')
    elif sys.platform == 'darwin':
        api_default = ('/Library/Application Support/Blackmagic Design'
                       '/DaVinci Resolve/Developer/Scripting')
        lib_default = ('/Applications/DaVinci Resolve/DaVinci Resolve.app'
                       '/Contents/Libraries/Fusion/fusionscript.so')
    else:
        api_default = '/opt/resolve/Developer/Scripting'
        lib_default = '/opt/resolve/libs/Fusion/fusionscript.so'

    api_dir = os.getenv('RESOLVE_SCRIPT_API') or api_default
    modules_dir = os.path.join(api_dir, 'Modules')
    if os.path.isdir(modules_dir) and modules_dir not in sys.path:
        sys.path.append(modules_dir)
        logger.debug(f"Added Resolve scripting modules to sys.path: {modules_dir}")
    os.environ.setdefault('RESOLVE_SCRIPT_LIB', lib_default)


class ResolveIntegration:
    """
    Handles integration with DaVinci Resolve via fusionscript.
    
    This class provides methods to import FCPXML timelines and media assets
    directly into an open DaVinci Resolve project, creating bins and organizing
    assets for immediate editing.
    """
    
    def __init__(self):
        """
        Initialize Resolve integration.
        
        Raises:
            ImportError: If fusionscript is not available
            RuntimeError: If DaVinci Resolve is not running
        """
        self.resolve = None
        self.project_manager = None
        self.current_project = None
        
        try:
            # Try to import and connect to DaVinci Resolve
            self._connect_to_resolve()
            logger.info("Successfully connected to DaVinci Resolve")
        except Exception as e:
            logger.error(f"Failed to connect to DaVinci Resolve: {e}")
            raise
    
    def _connect_to_resolve(self):
        """
        Connect to DaVinci Resolve via fusionscript.
        
        Raises:
            ImportError: If fusionscript module is not available
            RuntimeError: If Resolve is not running or connection fails
        """
        try:
            # Import DaVinci Resolve Python API (bootstrap default paths first)
            _bootstrap_resolve_script_import()
            import DaVinciResolveScript as dvr_script
            self.resolve = dvr_script.scriptapp("Resolve")
            
            if not self.resolve:
                raise RuntimeError("Could not connect to DaVinci Resolve. Is Resolve running?")
            
            # Get project manager
            self.project_manager = self.resolve.GetProjectManager()
            if not self.project_manager:
                raise RuntimeError("Could not access Resolve project manager")
            
            # Get current project
            self.current_project = self.project_manager.GetCurrentProject()
            if not self.current_project:
                raise RuntimeError("No project is currently open in DaVinci Resolve")
            
        except ImportError as e:
            raise ImportError(
                "DaVinci Resolve Python API not available. "
                "Make sure DaVinci Resolve is installed and fusionscript is accessible."
            ) from e
    
    def import_to_resolve(self, fcpxml_path: str, asset_files: List[str]) -> bool:
        """
        Import FCPXML timeline and assets to DaVinci Resolve.
        
        Args:
            fcpxml_path: Path to the FCPXML file to import
            asset_files: List of asset file paths to import
            
        Returns:
            True if import succeeded, False otherwise
        """
        if not self.current_project:
            logger.error("No current project available in Resolve")
            return False
        
        try:
            # Step 1: Create a new bin for the imported assets
            bin_name = f"screenwrite-{os.path.basename(fcpxml_path).replace('.fcpxml', '')}"
            media_pool = self.current_project.GetMediaPool()
            
            if not media_pool:
                logger.error("Could not access media pool")
                return False
            
            # Create bin
            bin_created = self._create_bin(media_pool, bin_name)
            if not bin_created:
                logger.warning(f"Failed to create bin '{bin_name}', using root folder")
            
            # Step 2: Import media assets
            if asset_files:
                assets_imported = self._import_media(media_pool, asset_files)
                logger.info(f"Imported {assets_imported}/{len(asset_files)} media assets")
            else:
                logger.info("No media assets to import")
            
            # Step 3: Import FCPXML timeline
            timeline_imported = self._import_timeline(fcpxml_path)
            
            if timeline_imported:
                logger.info("Successfully imported FCPXML timeline to Resolve")
                return True
            else:
                logger.error("Failed to import FCPXML timeline")
                return False
                
        except Exception as e:
            logger.error(f"Resolve import failed: {e}")
            return False
    
    def _create_bin(self, media_pool, bin_name: str) -> bool:
        """
        Create a new bin in the media pool.
        
        Args:
            media_pool: DaVinci Resolve media pool object
            bin_name: Name for the new bin
            
        Returns:
            True if bin was created successfully, False otherwise
        """
        try:
            # Get root folder
            root_folder = media_pool.GetRootFolder()
            if not root_folder:
                logger.error("Could not access root folder")
                return False
            
            # Create subfolder (bin)
            new_bin = media_pool.AddSubFolder(root_folder, bin_name)
            if new_bin:
                logger.info(f"Created bin: {bin_name}")
                return True
            else:
                logger.warning(f"Failed to create bin: {bin_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating bin: {e}")
            return False
    
    def _import_media(self, media_pool, asset_files: List[str]) -> int:
        """
        Import media files into the current bin.
        
        Args:
            media_pool: DaVinci Resolve media pool object
            asset_files: List of file paths to import
            
        Returns:
            Number of files successfully imported
        """
        if not asset_files:
            return 0
        
        imported_count = 0
        
        try:
            # Filter to existing files
            existing_files = [f for f in asset_files if os.path.exists(f)]
            if len(existing_files) != len(asset_files):
                missing_count = len(asset_files) - len(existing_files)
                logger.warning(f"{missing_count} asset files not found on disk")
            
            if not existing_files:
                logger.warning("No valid asset files to import")
                return 0
            
            # Import files
            imported_clips = media_pool.ImportMedia(existing_files)
            
            if imported_clips:
                imported_count = len(imported_clips)
                logger.info(f"Successfully imported {imported_count} media files")
            else:
                logger.warning("Media import returned no clips")
            
        except Exception as e:
            logger.error(f"Error importing media: {e}")
        
        return imported_count
    
    def _import_timeline(self, fcpxml_path: str) -> bool:
        """
        Import FCPXML timeline into the project.
        
        Args:
            fcpxml_path: Path to the FCPXML file
            
        Returns:
            True if timeline was imported successfully, False otherwise
        """
        try:
            if not os.path.exists(fcpxml_path):
                logger.error(f"FCPXML file not found: {fcpxml_path}")
                return False
            
            # Get media pool for timeline import
            media_pool = self.current_project.GetMediaPool()
            if not media_pool:
                logger.error("Could not access media pool for timeline import")
                return False
            
            # Import FCPXML
            # Note: The exact API method may vary depending on Resolve version
            try:
                # Try the standard import method
                imported_timeline = media_pool.ImportTimelineFromFile(fcpxml_path)
                
                if imported_timeline:
                    timeline_name = imported_timeline.GetName()
                    logger.info(f"Successfully imported timeline: {timeline_name}")
                    return True
                else:
                    logger.error("Timeline import returned None")
                    return False
                    
            except AttributeError:
                # Fallback for different Resolve API versions
                logger.warning("ImportTimelineFromFile not available, trying alternative method")
                
                # Alternative: Use project-level import
                result = self.project_manager.ImportProject(fcpxml_path)
                if result:
                    logger.info("Successfully imported FCPXML as project")
                    return True
                else:
                    logger.error("Alternative timeline import failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Error importing timeline: {e}")
            return False
    
    def get_resolve_info(self) -> Dict[str, Any]:
        """
        Get information about the current Resolve session.
        
        Returns:
            Dictionary with Resolve session information
        """
        info = {
            'connected': bool(self.resolve),
            'project_available': bool(self.current_project),
            'project_name': None,
            'resolve_version': None
        }
        
        try:
            if self.resolve:
                info['resolve_version'] = self.resolve.GetVersion()
            
            if self.current_project:
                info['project_name'] = self.current_project.GetName()
                
        except Exception as e:
            logger.debug(f"Error getting Resolve info: {e}")
        
        return info
    
    def is_available(self) -> bool:
        """
        Check if Resolve integration is available and working.
        
        Returns:
            True if Resolve is connected and a project is open, False otherwise
        """
        return bool(self.resolve and self.current_project)


# Marker colors by beat class / outcome (all legal Resolve marker colors).
MARKER_COLOR_MANUAL = "Red"
MARKER_COLOR_GAMEPLAY = "Blue"
MARKER_COLOR_STILL = "Green"
MARKER_COLOR_STOCK = "Yellow"
MARKER_COLOR_VO_SKIPPED = "Purple"


class ResolveTimelineBuilder:
    """
    Builds the ScreenWrite project natively inside DaVinci Resolve.

    Instead of importing a finished FCPXML wholesale, this constructs:
    - one Media Pool bin per beat holding its candidate clips,
    - a timeline where the top candidate sits enabled on V1 and alternates
      are stacked DISABLED on V2/V3 at the same position (picking = toggling),
    - the VO on audio track 1 starting at 0,
    - a colored timeline marker per beat carrying script text + provenance
      (Red=manual fill, Blue=gameplay, Green=wiki still, Yellow=stock,
      Purple=beat skipped by VO conform).

    Every Resolve call is defensive: the API returns None/False on failure,
    and the orchestrator falls back to FCPXML import if build() reports
    failure or raises.
    """

    MAX_ALTERNATE_TRACKS = 3

    def __init__(self, integration: ResolveIntegration,
                 framerate: int = DEFAULT_FRAMERATE,
                 width: int = 1920, height: int = 1080):
        """
        Args:
            integration: Connected ResolveIntegration (project must be open).
            framerate: Timeline framerate (must match beat quantization).
            width, height: Timeline resolution.
        """
        self.integration = integration
        self.framerate = framerate
        self.width = width
        self.height = height

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _norm(path: str) -> str:
        return os.path.normcase(os.path.normpath(path))

    def _frames_to_tc(self, frames: int) -> str:
        """Frames -> HH:MM:SS:FF timecode string at the builder framerate."""
        fps = self.framerate
        total_seconds, ff = divmod(int(frames), fps)
        hh, rem = divmod(total_seconds, 3600)
        mm, ss = divmod(rem, 60)
        return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

    def _beat_layout(self, beats) -> List[Dict[str, Any]]:
        """
        Compute each beat's (record position, duration) in frames.

        VO-conformed beats carry absolute positions (vo_start); otherwise
        positions accumulate from durations. Zero-duration beats stay in the
        layout (they still get a marker) but place no clips.
        """
        layout = []
        cursor = 0
        for beat in beats:
            duration_frames = round(beat.duration * self.framerate)
            if beat.vo_start is not None:
                record_frames = round(beat.vo_start * self.framerate)
            else:
                record_frames = cursor
            layout.append({
                'beat': beat,
                'record_frames': record_frames,
                'duration_frames': duration_frames,
            })
            cursor = record_frames + duration_frames
        return layout

    def _marker_color(self, beat, placed_any: bool) -> str:
        if beat.vo_matched is False:
            return MARKER_COLOR_VO_SKIPPED
        if not placed_any:
            return MARKER_COLOR_MANUAL
        sources = {c.get('source') for c in beat.candidates}
        if 'chaptered_gameplay' in sources:
            return MARKER_COLOR_GAMEPLAY
        if 'wiki_still' in sources:
            return MARKER_COLOR_STILL
        if 'pexels' in sources:
            return MARKER_COLOR_STOCK
        return MARKER_COLOR_MANUAL

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, beats, vo_path: Optional[str], timeline_name: str) -> Dict[str, Any]:
        """
        Construct bins, timeline, clips, VO, and markers for the given beats.

        Returns:
            {'success': bool, 'timeline_name': str, 'warnings': [str, ...]}
        """
        warnings: List[str] = []
        result = {'success': False, 'timeline_name': timeline_name, 'warnings': warnings}

        project = self.integration.current_project
        if not project:
            warnings.append("No open Resolve project")
            return result
        media_pool = project.GetMediaPool()
        if not media_pool:
            warnings.append("Could not access Resolve media pool")
            return result

        # 1. Project settings (may be locked; warn and continue).
        for key, value in (
            ("timelineFrameRate", str(self.framerate)),
            ("timelineResolutionWidth", str(self.width)),
            ("timelineResolutionHeight", str(self.height)),
        ):
            if not project.SetSetting(key, value):
                warnings.append(f"Could not set project setting {key}={value}")

        # 2. Bin tree + per-beat candidate import.
        root = media_pool.GetRootFolder()
        run_bin = media_pool.AddSubFolder(root, f"screenwrite-{timeline_name}") or root
        items_by_path: Dict[str, Any] = {}
        for beat in beats:
            paths = [c['local_path'] for c in beat.candidates[:self.MAX_ALTERNATE_TRACKS]
                     if c.get('local_path') and os.path.exists(c['local_path'])]
            if not paths:
                continue
            label = beat.entities[0] if beat.entities else beat.beat_class
            beat_bin = media_pool.AddSubFolder(run_bin, f"{beat.id} - {label}") or run_bin
            media_pool.SetCurrentFolder(beat_bin)
            imported = media_pool.ImportMedia(paths) or []
            for item in imported:
                try:
                    file_path = item.GetClipProperty("File Path")
                except Exception:  # noqa: BLE001 - API objects can misbehave
                    continue
                if file_path:
                    items_by_path[self._norm(file_path)] = item

        # 3. VO import (into the run bin).
        vo_item = None
        if vo_path and os.path.exists(vo_path):
            media_pool.SetCurrentFolder(run_bin)
            vo_imported = media_pool.ImportMedia([vo_path]) or []
            vo_item = vo_imported[0] if vo_imported else None
            if vo_item is None:
                warnings.append(f"Could not import VO audio: {vo_path}")

        # 4. Timeline.
        media_pool.SetCurrentFolder(run_bin)
        timeline = media_pool.CreateEmptyTimeline(timeline_name)
        if not timeline:
            fallback_name = f"{timeline_name}-{time.strftime('%H%M%S')}"
            timeline = media_pool.CreateEmptyTimeline(fallback_name)
            result['timeline_name'] = fallback_name
        if not timeline:
            warnings.append("Could not create a timeline")
            return result
        project.SetCurrentTimeline(timeline)

        actual_fps = str(timeline.GetSetting("timelineFrameRate") or "")
        if actual_fps and float(actual_fps) != float(self.framerate):
            warnings.append(
                f"Timeline frame rate is {actual_fps}, expected {self.framerate} - "
                f"clip positions may be off"
            )

        # 5. Enough video tracks for the alternates.
        layout = self._beat_layout(beats)
        tracks_needed = max(
            [min(len(entry['beat'].candidates), self.MAX_ALTERNATE_TRACKS)
             for entry in layout] + [1]
        )
        if hasattr(timeline, 'AddTrack'):
            guard = 0
            while timeline.GetTrackCount("video") < tracks_needed and guard < 8:
                if not timeline.AddTrack("video"):
                    warnings.append("Could not add a video track for alternates")
                    break
                guard += 1
        elif tracks_needed > 1:
            warnings.append(
                "This Resolve version lacks Timeline.AddTrack - alternates "
                "limited to existing tracks"
            )

        # 6. Record-frame base. recordFrame is absolute (timeline start
        #    timecode, typically 01:00:00:00); marker frameIds are relative.
        try:
            base = int(timeline.GetStartFrame() or 0)
        except Exception:  # noqa: BLE001
            base = 0
        offset_correction = 0
        calibrated = False

        # 7. Clips: top candidate enabled on V1, alternates disabled above.
        placed_clips = 0
        for entry in layout:
            beat = entry['beat']
            duration_frames = entry['duration_frames']
            record_frames = entry['record_frames']
            if duration_frames <= 0:
                continue

            enabled_placed = False
            for k, candidate in enumerate(beat.candidates[:self.MAX_ALTERNATE_TRACKS]):
                local_path = candidate.get('local_path')
                item = items_by_path.get(self._norm(local_path)) if local_path else None
                if item is None:
                    continue

                # Stills have no intrinsic length - set their media pool
                # duration to the beat window before appending.
                if Path(local_path).suffix.lower() in STILL_IMAGE_EXTENSIONS:
                    try:
                        item.SetClipProperty("Duration", self._frames_to_tc(duration_frames))
                    except Exception:  # noqa: BLE001
                        warnings.append(f"{beat.id}: could not set still duration")

                clip_info = {
                    "mediaPoolItem": item,
                    "startFrame": 0,
                    "endFrame": duration_frames,
                    "trackIndex": k + 1,
                    "recordFrame": base + record_frames + offset_correction,
                    "mediaType": 1,
                }
                appended = media_pool.AppendToTimeline([clip_info]) or []
                timeline_item = appended[0] if appended else None
                if timeline_item is None:
                    warnings.append(
                        f"{beat.id}: candidate {k + 1} failed to place on the timeline"
                    )
                    continue

                # One-time calibration: if this Resolve interprets recordFrame
                # differently (relative vs absolute), measure the delta on the
                # first placed clip and correct everything that follows.
                if not calibrated:
                    calibrated = True
                    try:
                        actual_start = int(timeline_item.GetStart())
                        expected = base + record_frames + offset_correction
                        delta = actual_start - expected
                    except Exception:  # noqa: BLE001
                        delta = 0
                    if delta != 0:
                        offset_correction = -delta
                        warnings.append(
                            f"recordFrame calibration: correcting subsequent "
                            f"clips by {-delta} frames"
                        )

                if enabled_placed:
                    if hasattr(timeline_item, 'SetClipEnabled'):
                        timeline_item.SetClipEnabled(False)
                    else:
                        warnings.append(
                            "This Resolve version lacks SetClipEnabled - "
                            "alternates left enabled (mute their tracks manually)"
                        )
                else:
                    enabled_placed = True
                    if k > 0:
                        warnings.append(
                            f"{beat.id}: top candidate failed; alternate "
                            f"{k + 1} promoted"
                        )
                placed_clips += 1

        # 8. VO on audio track 1 at timeline start.
        if vo_item is not None:
            audio_end = max(
                (entry['record_frames'] + entry['duration_frames'] for entry in layout),
                default=0,
            )
            vo_info = {
                "mediaPoolItem": vo_item,
                "startFrame": 0,
                "endFrame": audio_end,
                "trackIndex": 1,
                "recordFrame": base + offset_correction,
                "mediaType": 2,
            }
            if not (media_pool.AppendToTimeline([vo_info]) or []):
                warnings.append("Could not place VO audio on the timeline")

        # 9. Markers (frameId is relative to timeline start - no base). Added
        #    after clips/VO exist so the positions are inside the timeline.
        for entry in layout:
            beat = entry['beat']
            placed_any = bool(entry['duration_frames'] > 0 and any(
                items_by_path.get(self._norm(c.get('local_path') or ''))
                for c in beat.candidates[:self.MAX_ALTERNATE_TRACKS]
            ))
            color = self._marker_color(beat, placed_any)
            note_parts = [beat.text[:180]]
            if beat.candidates:
                top_path = beat.candidates[0].get('local_path')
                provenance = build_provenance_note(beat, top_path) if top_path else None
                if provenance:
                    note_parts.append(provenance)
            if color == MARKER_COLOR_MANUAL:
                note_parts.append(
                    f"MANUAL FILL - no coverage for {beat.entities}" if beat.entities
                    else "MANUAL FILL - creator-supplied shot needed"
                )
            custom_data = json.dumps({
                'beat_id': beat.id,
                'beat_class': beat.beat_class,
                'entities': beat.entities,
                'source_url': ((beat.candidates[0].get('metadata') or {}).get('source_url')
                               if beat.candidates else None),
                'vo_matched': beat.vo_matched,
            })
            marker_frame = entry['record_frames'] + offset_correction
            if not timeline.AddMarker(marker_frame, color, beat.id,
                                      "\n".join(note_parts), 1, custom_data):
                warnings.append(f"{beat.id}: could not add timeline marker")

        result['success'] = placed_clips > 0 or vo_item is not None
        if not result['success']:
            warnings.append("Nothing could be placed on the timeline")
        logger.info(
            "Native Resolve build: %d clips placed, %d warnings",
            placed_clips, len(warnings)
        )
        return result
