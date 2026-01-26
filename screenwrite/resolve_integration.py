"""
DaVinci Resolve integration module.

This module provides optional integration with DaVinci Resolve via fusionscript,
allowing automatic import of generated timelines and assets into Resolve projects.
"""

import logging
from typing import List, Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


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
            # Import DaVinci Resolve Python API
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
