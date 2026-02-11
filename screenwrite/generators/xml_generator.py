"""
FCPXML Generator for creating Final Cut Pro XML timelines.

This module generates FCPXML 1.8 documents compatible with DaVinci Resolve
and Final Cut Pro, containing spine tracks with gaps for voiceover and
connected clips for B-roll ScreenWrite.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from pathlib import Path
import os

from ..core.beat import Beat
from ..config import (
    DEFAULT_FRAMERATE,
    DEFAULT_VIDEO_WIDTH,
    DEFAULT_VIDEO_HEIGHT,
    MIN_FCPXML_FILE_SIZE,
)


class XMLGenerator:
    """
    Generates FCPXML 1.8 timelines from Beat objects and asset mappings.
    
    Creates a timeline with:
    - Spine track containing gaps for each beat (voiceover placeholders)
    - Connected clips on Lane 1 for B-roll ScreenWrite
    - Proper resource registration for all video files
    - Valid FCPXML 1.8 structure
    """
    
    def __init__(self, framerate: int = DEFAULT_FRAMERATE):
        """
        Initialize the XML generator.
        
        Args:
            framerate: Timeline framerate (default: 30fps)
        """
        self.framerate = framerate
        self.format_id = "r1"
        self.next_resource_id = 2  # r1 is reserved for format
        self.asset_to_resource_id = {}  # Track asset path to resource ID mapping
    
    def generate(self, beats: List[Beat], asset_map: Dict[str, str], output_path: str) -> str:
        """
        Generate FCPXML timeline from beats and assets.
        
        Args:
            beats: List of Beat objects representing the timeline segments
            asset_map: Mapping of beat IDs to asset file paths
            output_path: Path where FCPXML file will be written
            
        Returns:
            Path to the generated FCPXML file
            
        Raises:
            ValueError: If beats list is empty or asset paths are invalid
            IOError: If output file cannot be written
        """
        if not beats:
            raise ValueError("Cannot generate FCPXML: beats list is empty")
        
        # Reset resource tracking for this generation
        self.next_resource_id = 2
        self.asset_to_resource_id = {}
        
        # Create FCPXML root structure
        root = self._create_root()
        
        # Create resources section
        resources = self._create_resources(asset_map)
        root.append(resources)
        
        # Create library with project and sequence
        library = self._create_library(beats, asset_map)
        root.append(library)
        
        # Validate XML structure
        if not self._validate_xml(root):
            raise ValueError("Generated FCPXML failed validation")
        
        # Write to file with pretty formatting
        self.write(root, output_path)
        
        return output_path
    
    def _create_root(self) -> ET.Element:
        """Create FCPXML root element with version 1.8."""
        root = ET.Element("fcpxml")
        root.set("version", "1.8")
        return root
    
    def _create_resources(self, asset_map: Dict[str, Any]) -> ET.Element:
        """
        Create resources section with format and media resources.
        
        Args:
            asset_map: Mapping of beat IDs to asset file path or list of paths
            
        Returns:
            Resources XML element
        """
        resources = ET.Element("resources")
        
        # Add format resource (1920x1080 30fps)
        format_elem = self._create_format()
        resources.append(format_elem)
        
        # Collect all unique asset paths
        unique_assets = set()
        for val in asset_map.values():
            if isinstance(val, list):
                for path in val:
                    if path: unique_assets.add(path)
            elif val:
                unique_assets.add(val)

        for asset_path in unique_assets:
            # For Resolve compatibility, use 'asset' elements directly in resources
            # instead of wrapping them in 'media'
            asset_elem = self._create_asset_resource(asset_path)
            resources.append(asset_elem)
        
        return resources

    def _create_format(self) -> ET.Element:
        """Create format resource for the timeline."""
        format_elem = ET.Element("format")
        format_elem.set("id", self.format_id)
        format_elem.set("name", f"FFVideoFormat{DEFAULT_VIDEO_HEIGHT}p{self.framerate}")
        # Dynamic frame duration based on framerate
        format_elem.set("frameDuration", f"1/{self.framerate}s")
        format_elem.set("width", str(DEFAULT_VIDEO_WIDTH))
        format_elem.set("height", str(DEFAULT_VIDEO_HEIGHT))
        format_elem.set("colorSpace", "1-1-1 (Rec. 709)")
        return format_elem

    def _create_asset_resource(self, asset_path: str) -> ET.Element:
        """
        Create asset resource element for a video file.
        
        Args:
            asset_path: Path to the video file
            
        Returns:
            Asset XML element with unique resource ID
        """
        resource_id = f"r{self.next_resource_id}"
        self.asset_to_resource_id[asset_path] = resource_id
        self.next_resource_id += 1
        
        # Get file info
        file_path = Path(asset_path)
        filename = file_path.name
        
        # Create asset element
        asset = ET.Element("asset")
        asset.set("id", resource_id)
        asset.set("name", filename)
        asset.set("uid", f"asset-{resource_id}")
        asset.set("start", "0/1s")
        # Added duration for better FCPX/Resolve compatibility (10 hours)
        asset.set("duration", "36000/1s")
        asset.set("hasVideo", "1")
        asset.set("format", self.format_id)
        asset.set("hasAudio", "1")
        
        # Add media-rep with file path
        media_rep = ET.SubElement(asset, "media-rep")
        media_rep.set("kind", "original-media")
        media_rep.set("sig", f"sig-{resource_id}")
        
        # Absolute path with standard file:/// protocol
        abs_path = os.path.abspath(asset_path).replace('\\', '/')
        if not abs_path.startswith('/'):
            media_rep.set("src", f"file:///{abs_path}")
        else:
            media_rep.set("src", f"file://{abs_path}")
        
        return asset

    def _create_library(self, beats: List[Beat], asset_map: Dict[str, str]) -> ET.Element:
        """
        Create library element containing the project and sequence.
        
        Args:
            beats: List of Beat objects
            asset_map: Mapping of beat IDs to asset file paths
            
        Returns:
            Library XML element
        """
        library = ET.Element("library")
        library.set("location", "file:///")
        
        # Create event
        event = ET.SubElement(library, "event")
        event.set("name", "Timeline")
        event.set("uid", "event-1")
        
        # Create project
        project = ET.SubElement(event, "project")
        project.set("name", "Project")
        project.set("uid", "project-1")
        project.set("id", "project-1")
        
        # Create sequence
        sequence = ET.SubElement(project, "sequence")
        sequence.set("format", self.format_id)
        sequence.set("duration", f"{self._frames_to_timecode(self._calculate_total_frames(beats))}")
        sequence.set("tcStart", "0/1s")
        sequence.set("tcFormat", "NDF")
        sequence.set("audioLayout", "stereo")
        sequence.set("audioRate", "48k")
        
        # Create spine with asset-clips (Primary Storyline)
        spine = self._create_spine(beats, asset_map)
        sequence.append(spine)
        
        return library
    
    def _create_spine(self, beats: List[Beat], asset_map: Dict[str, Any]) -> ET.Element:
        """
        Create spine track with clips for each beat.
        
        Args:
            beats: List of Beat objects
            asset_map: Mapping of beat IDs to asset file paths or lists
            
        Returns:
            Spine XML element with clip/gap elements
        """
        spine = ET.Element("spine")
        current_offset = 0.0
        
        for beat in beats:
            asset_val = asset_map.get(beat.id)
            # Use the first asset if it's a list
            asset_path = asset_val[0] if isinstance(asset_val, list) and asset_val else asset_val
            
            duration_tc = self._seconds_to_timecode(beat.duration)
            offset_tc = self._seconds_to_timecode(current_offset)
            
            if asset_path:
                # Primary asset-clip
                resource_id = self._get_resource_id_for_asset(asset_path)
                clip = ET.SubElement(spine, "asset-clip")
                clip.set("name", f"Clip - {beat.id}")
                clip.set("offset", offset_tc)
                clip.set("ref", resource_id)
                clip.set("duration", duration_tc)
                clip.set("start", "0/1s")

                # Add Marker with script text
                marker = ET.SubElement(clip, "marker")
                marker.set("start", "0/1s")
                marker.set("duration", "1/30s")
                marker.set("value", beat.text)
                marker.set("note", "Script Text")
                
                # Add Keywords for organization
                keywords = ET.SubElement(clip, "keyword")
                keywords.set("start", "0/1s")
                keywords.set("duration", duration_tc)
                
                # Determine keyword from beat context or fetcher
                kw_val = "ScreenWrite"
                if "pexels" in asset_path.lower():
                    kw_val += ", Stock"
                elif "youtube" in asset_path.lower():
                    kw_val += ", YouTube"
                
                keywords.set("value", kw_val)
            else:
                # Placeholder gap if no asset
                gap = ET.SubElement(spine, "gap")
                gap.set("name", f"Gap - {beat.id}")
                gap.set("offset", offset_tc)
                gap.set("duration", duration_tc)
                gap.set("start", "0/1s")
            
            current_offset += beat.duration
        
        return spine

    def _get_resource_id_for_asset(self, asset_path: str) -> str:
        """
        Get the resource ID for a given asset path.
        
        Args:
            asset_path: Path to the asset file
            
        Returns:
            Resource ID string (e.g., "r2")
        """
        return self.asset_to_resource_id.get(asset_path, "r2")  # Default fallback

    def _calculate_total_frames(self, beats: List[Beat]) -> int:
        """Calculate total timeline duration in frames."""
        total_seconds = sum(beat.duration for beat in beats)
        return int(total_seconds * self.framerate)
    
    def _seconds_to_timecode(self, seconds: float) -> str:
        """Convert seconds to FCPXML timecode format."""
        frames = int(seconds * self.framerate)
        return f"{frames}/{self.framerate}s"
    
    def _frames_to_timecode(self, frames: int) -> str:
        """Convert frames to FCPXML timecode format."""
        return f"{frames}/{self.framerate}s"
    
    def _validate_xml(self, root: ET.Element) -> bool:
        """
        Validate the generated FCPXML structure.
        
        Args:
            root: Root XML element to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check root element
            if root.tag != "fcpxml" or root.get("version") != "1.8":
                return False
            
            # Check for required child elements
            resources = root.find("resources")
            library = root.find("library")
            
            if resources is None or library is None:
                return False
            
            # Check resources has format
            format_elem = resources.find("format")
            if format_elem is None or format_elem.get("id") != self.format_id:
                return False
            
            # Check library structure
            event = library.find("event")
            if event is None:
                return False
            
            project = event.find("project")
            if project is None:
                return False
            
            sequence = project.find("sequence")
            if sequence is None:
                return False
            
            spine = sequence.find("spine")
            if spine is None:
                return False
            
            # Validate spine has gaps
            gaps = spine.findall("gap")
            # Also allow asset-clips
            clips = spine.findall("asset-clip")
            if not gaps and not clips:
                return False
            
            return True
            
        except Exception:
            return False
    
    def write(self, root: ET.Element, output_path: str) -> None:
        """
        Write XML to file with pretty formatting.
        
        Args:
            root: Root XML element to write
            output_path: Path where file will be written
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Pretty print the XML
            self._indent(root)
            
            # Create tree and write to file
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding="utf-8", xml_declaration=True)
            
        except Exception as e:
            raise IOError(f"Failed to write FCPXML to {output_path}: {e}")
    
    def _indent(self, elem: ET.Element, level: int = 0) -> None:
        """
        Add pretty-printing indentation to XML elements.
        
        Args:
            elem: XML element to indent
            level: Current indentation level
        """
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent