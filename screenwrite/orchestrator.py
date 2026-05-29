"""
Main video orchestrator for coordinating all components.

The VideoOrchestrator class manages the complete workflow:
parse â†’ fetch â†’ generate, with comprehensive error handling and logging.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .core.beat import Beat
from .parsing.script_parser import ScriptParser
from .fetchers.asset_orchestrator import AssetOrchestrator
from .generators.xml_generator import XMLGenerator
from .config import MIN_FCPXML_FILE_SIZE
from .utils.error_handling import (
    ensure_output_directory,
    InputValidationError,
    OutputError,
    NetworkError,
    DependencyError,
    handle_graceful_degradation,
    log_error_with_context
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoOrchestrator:
    """
    Main coordinator class that orchestrates the complete video timeline generation workflow.
    
    The orchestrator manages the pipeline: script parsing â†’ asset fetching â†’ FCPXML generation,
    with comprehensive error handling and optional DaVinci Resolve integration.
    """
    
    def __init__(self, 
                 pexels_api_key: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 youtube_enabled: bool = True,
                 pexels_enabled: bool = True,
                 resolve_enabled: bool = False,
                 skip_failed_beats: bool = False,
                 max_workers: int = 4,
                 enable_asset_cache: bool = True,
                 prefer_stock_for_generic: bool = True,
                 use_llm_queries: bool = True,
                 broll_manifest: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize the video orchestrator.
        
        Args:
            pexels_api_key: API key for Pexels. If None, will try environment variable.
            output_dir: Directory for output files. If None, uses temp directory.
            youtube_enabled: Whether to enable YouTube fetching
            pexels_enabled: Whether to enable Pexels fetching  
            resolve_enabled: Whether to enable DaVinci Resolve integration
            skip_failed_beats: Continue processing if some beats fail to fetch assets
            max_workers: Maximum number of parallel download threads (default: 4)
            enable_asset_cache: Whether to use persistent asset cache (default: True)
            prefer_stock_for_generic: Prefer curated stock footage (Pexels) for
                generic beats and YouTube for specific ones (default: True)
            use_llm_queries: Enhance B-roll queries with the LLM query generator
                when an API key is configured (default: True)
            broll_manifest: Optional path to an editor-authored B-roll manifest
                JSON whose per-beat queries override heuristic/LLM queries
            verbose: Enable debug logging
        """
        # Configure logging level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.output_dir = Path(tempfile.mkdtemp(prefix="screenwrite_"))
        
        logger.info(f"Video orchestrator initialized with output directory: {self.output_dir}")
        
        # Initialize components
        self.script_parser = ScriptParser(
            use_llm_queries=use_llm_queries,
            manifest_path=broll_manifest,
        )
        self.asset_orchestrator = AssetOrchestrator(
            pexels_api_key=pexels_api_key,
            output_dir=str(self.output_dir),
            youtube_enabled=youtube_enabled,
            pexels_enabled=pexels_enabled,
            prefer_stock_for_generic=prefer_stock_for_generic
        )
        self.xml_generator = XMLGenerator()
        
        # Configuration
        self.resolve_enabled = resolve_enabled
        self.skip_failed_beats = skip_failed_beats
        self.max_workers = max_workers
        self.enable_asset_cache = enable_asset_cache
        self.resolve_integration = None
        
        if skip_failed_beats:
            logger.info("Skip failed beats mode enabled - will continue processing if some assets fail to fetch")
        
        # Initialize Resolve integration if enabled
        if resolve_enabled:
            try:
                from .resolve_integration import ResolveIntegration
                self.resolve_integration = ResolveIntegration()
                logger.info("DaVinci Resolve integration enabled")
            except ImportError as e:
                logger.warning(f"DaVinci Resolve integration not available: {e}")
                self.resolve_enabled = False
            except Exception as e:
                logger.warning(f"Failed to initialize Resolve integration: {e}")
                self.resolve_enabled = False
        
        # Track workflow state
        self.last_beats: Optional[List[Beat]] = None
        self.last_asset_map: Optional[Dict[str, str]] = None
        self.last_fcpxml_path: Optional[str] = None
    
    def orchestrate(self, 
                   script_path: str, 
                   output_path: str, 
                   skip_fetch: bool = False) -> Dict[str, Any]:
        """
        Execute the complete video orchestration workflow.
        
        Args:
            script_path: Path to the markdown script file
            output_path: Path for the output FCPXML file
            skip_fetch: If True, skip asset fetching and generate empty timeline
            
        Returns:
            Dictionary containing workflow results and status information
            
        Raises:
            FileNotFoundError: If script file doesn't exist
            ValueError: If script is invalid or empty
            IOError: If output file cannot be written
        """
        logger.info(f"Starting video orchestration workflow")
        logger.info(f"Script: {script_path}")
        logger.info(f"Output: {output_path}")
        logger.info(f"Skip fetch: {skip_fetch}")
        
        workflow_result = {
            'success': False,
            'script_path': script_path,
            'output_path': output_path,
            'beats_count': 0,
            'total_duration': 0.0,
            'assets_fetched': 0,
            'fcpxml_generated': False,
            'resolve_imported': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Step 1: Parse script into beats
            logger.info("Step 1: Parsing script into beats")
            beats = self._parse_script(script_path)
            workflow_result['beats_count'] = len(beats)
            total_duration = self.estimate_duration(beats)
            workflow_result['total_duration'] = total_duration
            duration_str = self.format_duration(total_duration)
            logger.info(f"Successfully parsed {len(beats)} beats from script ({duration_str} total)")
            
            # Step 2: Fetch assets (unless skipped)
            asset_map = {}
            if skip_fetch:
                logger.info("Step 2: Skipping asset fetching as requested")
                workflow_result['warnings'].append("Asset fetching was skipped")
            else:
                logger.info("Step 2: Fetching B-roll assets")
                asset_map = self._fetch_assets(beats)
                assets_fetched = sum(1 for path in asset_map.values() if path)
                workflow_result['assets_fetched'] = assets_fetched
                logger.info(f"Successfully fetched {assets_fetched}/{len(beats)} assets")
                
                if assets_fetched == 0:
                    workflow_result['warnings'].append("No assets were successfully fetched")
                elif assets_fetched < len(beats):
                    workflow_result['warnings'].append(f"Only {assets_fetched}/{len(beats)} assets were fetched")
            
            # Step 3: Generate FCPXML timeline
            logger.info("Step 3: Generating FCPXML timeline")
            fcpxml_path = self._generate_timeline(beats, asset_map, output_path)
            workflow_result['fcpxml_generated'] = True
            workflow_result['output_path'] = fcpxml_path
            logger.info(f"Successfully generated FCPXML: {fcpxml_path}")
            
            # Step 4: Optional Resolve integration
            if self.resolve_enabled and self.resolve_integration:
                logger.info("Step 4: Importing to DaVinci Resolve")
                try:
                    resolve_success = self._import_to_resolve(fcpxml_path, asset_map)
                    workflow_result['resolve_imported'] = resolve_success
                    if resolve_success:
                        logger.info("Successfully imported timeline to DaVinci Resolve")
                    else:
                        workflow_result['warnings'].append("Failed to import to DaVinci Resolve")
                except Exception as e:
                    logger.warning(f"Resolve import failed: {e}")
                    workflow_result['warnings'].append(f"Resolve import error: {e}")
            else:
                logger.info("Step 4: Skipping Resolve integration (disabled)")
            
            # Store results for potential reuse
            self.last_beats = beats
            self.last_asset_map = asset_map
            self.last_fcpxml_path = fcpxml_path
            
            workflow_result['success'] = True
            logger.info("Video orchestration workflow completed successfully")
            
        except Exception as e:
            error_msg = f"Workflow failed: {e}"
            logger.error(error_msg)
            workflow_result['errors'].append(error_msg)
            raise RuntimeError(error_msg) from e
        
        return workflow_result
    
    def _parse_script(self, script_path: str) -> List[Beat]:
        """
        Parse markdown script into Beat objects.
        
        Args:
            script_path: Path to the markdown script file
            
        Returns:
            List of Beat objects
            
        Raises:
            InputValidationError: If script file is invalid or cannot be processed
        """
        try:
            # Parse the script using enhanced error handling
            beats = self.script_parser.parse(script_path)
            
            if not beats:
                raise InputValidationError(f"No beats generated from script: {script_path}")
            
            # Log beat summary
            total_duration = sum(beat.duration for beat in beats)
            logger.info(f"Parsed beats summary:")
            logger.info(f"  Total beats: {len(beats)}")
            logger.info(f"  Total duration: {total_duration:.1f} seconds")
            logger.info(f"  Average duration: {total_duration/len(beats):.1f} seconds")
            
            # Log individual beats in debug mode
            for beat in beats:
                logger.debug(f"  {beat}")
            
            return beats
            
        except InputValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Script parsing failed",
                component="VideoOrchestrator",
                script_path=script_path,
                error=e
            )
            raise InputValidationError(f"Failed to parse script: {e}")
    
    
    def estimate_duration(self, beats: List[Beat]) -> float:
        """
        Estimate the total timeline duration from beats.
        
        Args:
            beats: List of Beat objects
            
        Returns:
            Total duration in seconds
        """
        return sum(beat.duration for beat in beats)
    
    def format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string (e.g., "2m 35s")
        """
        minutes, secs = divmod(int(seconds), 60)
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"
    
    def _fetch_assets(self, beats: List[Beat]) -> Dict[str, str]:
        """
        Fetch B-roll assets for all beats with enhanced error handling.
        
        Args:
            beats: List of Beat objects needing assets
            
        Returns:
            Dictionary mapping beat IDs to asset file paths (None if fetch failed)
        """
        if not beats:
            logger.warning("No beats provided for asset fetching")
            return {}
        
        # Check if any fetchers are available
        available_fetchers = self.asset_orchestrator.get_available_fetchers()
        if not available_fetchers:
            logger.error("No asset fetchers available - cannot fetch assets")
            return {beat.id: None for beat in beats}
        
        logger.info(f"Available fetchers: {', '.join(available_fetchers)}")
        
        # Prepare batch queries
        queries = []
        for beat in beats:
            queries.append({
                'id': beat.id,
                'youtube_query': beat.youtube_search_phrase,
                'stock_query': beat.stock_keyword,
                'duration': beat.duration
            })
        
        # Fetch assets in batch with error handling
        try:
            asset_map = self.asset_orchestrator.fetch_assets_batch(
                queries, 
                max_workers=self.max_workers,
                enable_cache=self.enable_asset_cache
            )
            
            # Update beat objects with asset paths
            for beat in beats:
                asset_path = asset_map.get(beat.id)
                if asset_path:
                    # Determine which fetcher was used based on available fetchers
                    if 'youtube' in available_fetchers:
                        beat.asset_paths['youtube'] = asset_path
                    elif 'pexels' in available_fetchers:
                        beat.asset_paths['pexels'] = asset_path
                    else:
                        beat.asset_paths['unknown'] = asset_path
            
            return asset_map
            
        except NetworkError as e:
            logger.warning(f"Network error during asset fetching: {e}")
            # Continue with empty asset map to allow workflow to proceed
            return {beat.id: None for beat in beats}
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Asset fetching failed",
                component="VideoOrchestrator",
                beats_count=len(beats),
                error=e
            )
            # Return empty asset map to allow workflow to continue
            return {beat.id: None for beat in beats}
    
    
    def _generate_timeline(self, 
                          beats: List[Beat], 
                          asset_map: Dict[str, str], 
                          output_path: str) -> str:
        """
        Generate FCPXML timeline from beats and assets with enhanced error handling.
        
        Args:
            beats: List of Beat objects
            asset_map: Mapping of beat IDs to asset file paths
            output_path: Path for output FCPXML file
            
        Returns:
            Path to generated FCPXML file
            
        Raises:
            InputValidationError: If beats list is empty
            OutputError: If output file cannot be written
        """
        if not beats:
            raise InputValidationError("Cannot generate timeline: no beats provided")
        
        try:
            # Ensure output directory exists using enhanced validation
            output_result = ensure_output_directory(output_path)
            if not output_result.is_valid:
                raise OutputError(output_result.error_message)
            
            # Log any warnings from output validation
            for warning in output_result.warnings:
                logger.info(warning)
            
            # Generate FCPXML
            fcpxml_path = self.xml_generator.generate(beats, asset_map, output_path)
            
            # Verify the file was created and has reasonable content
            if not os.path.exists(fcpxml_path):
                raise OutputError(f"FCPXML file was not created: {fcpxml_path}")
            
            # Check file size
            file_size = os.path.getsize(fcpxml_path)
            if file_size == 0:
                raise OutputError(f"FCPXML file is empty: {fcpxml_path}")
            elif file_size < MIN_FCPXML_FILE_SIZE:
                logger.warning(f"FCPXML file is very small ({file_size} bytes): {fcpxml_path}")
            
            # Log timeline summary
            total_duration = sum(beat.duration for beat in beats)
            assets_with_files = sum(1 for path in asset_map.values() if path)
            
            logger.info(f"Generated FCPXML timeline:")
            logger.info(f"  File: {fcpxml_path}")
            logger.info(f"  Size: {file_size} bytes")
            logger.info(f"  Duration: {total_duration:.1f} seconds")
            logger.info(f"  Beats: {len(beats)}")
            logger.info(f"  Assets: {assets_with_files}/{len(beats)}")
            
            return fcpxml_path
            
        except (InputValidationError, OutputError):
            # Re-raise validation and output errors as-is
            raise
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Timeline generation failed",
                component="VideoOrchestrator",
                output_path=output_path,
                beats_count=len(beats),
                error=e
            )
            raise OutputError(f"Failed to generate timeline: {e}")
    
    
    def _import_to_resolve(self, fcpxml_path: str, asset_map: Dict[str, str]) -> bool:
        """
        Import timeline and assets to DaVinci Resolve.
        
        Args:
            fcpxml_path: Path to the FCPXML file
            asset_map: Mapping of beat IDs to asset file paths
            
        Returns:
            True if import succeeded, False otherwise
        """
        if not self.resolve_integration:
            logger.warning("Resolve integration not available")
            return False
        
        try:
            # Get list of asset files
            asset_files = [path for path in asset_map.values() if path and os.path.exists(path)]
            
            # Import to Resolve
            success = self.resolve_integration.import_to_resolve(fcpxml_path, asset_files)
            
            if success:
                logger.info(f"Successfully imported to Resolve:")
                logger.info(f"  Timeline: {fcpxml_path}")
                logger.info(f"  Assets: {len(asset_files)} files")
            else:
                logger.warning("Resolve import failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Resolve import error: {e}")
            return False
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get current workflow status and component availability.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'orchestrator_ready': True,
            'output_dir': str(self.output_dir),
            'components': {
                'script_parser': True,
                'asset_orchestrator': bool(self.asset_orchestrator.get_available_fetchers()),
                'xml_generator': True,
                'resolve_integration': self.resolve_enabled and bool(self.resolve_integration)
            },
            'fetchers': self.asset_orchestrator.get_fetcher_status(),
            'last_workflow': {
                'beats_count': len(self.last_beats) if self.last_beats else 0,
                'assets_count': len([p for p in (self.last_asset_map or {}).values() if p]),
                'fcpxml_path': self.last_fcpxml_path
            }
        }
        
        return status
    
    def cleanup(self) -> None:
        """
        Clean up temporary files and resources.
        
        This method should be called when the orchestrator is no longer needed
        to clean up any temporary files or resources.
        """
        try:
            # Clean up temporary output directory if it was auto-created
            if self.output_dir and self.output_dir.name.startswith("screenwrite_"):
                import shutil
                if self.output_dir.exists():
                    shutil.rmtree(self.output_dir)
                    logger.info(f"Cleaned up temporary directory: {self.output_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary files: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
