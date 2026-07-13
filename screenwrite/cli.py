"""
Command-line interface for screenwrite.

Provides a user-friendly CLI for converting markdown scripts into FCPXML timelines
with automatic B-roll fetching from YouTube and Pexels.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .orchestrator import VideoOrchestrator
from .utils.logging import setup_logging, get_logger
from .utils.script_linter import lint_script_file, print_lint_issues
from .utils.cache import clear_cache
from .utils.error_handling import (
    validate_markdown_file,
    ensure_output_directory,
    validate_api_key,
    check_dependency,
    InputValidationError,
    OutputError,
    DependencyError,
    log_error_with_context
)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='screenwrite',
        description='Convert markdown video scripts into FCPXML timelines with automatic B-roll fetching',
        epilog='''
Examples:
  %(prog)s script.md --output timeline.fcpxml
  %(prog)s script.md --output timeline.fcpxml --pexels-key YOUR_KEY --verbose
  %(prog)s script.md --output timeline.fcpxml --resolve --no-fetch
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        'script',
        type=str,
        help='Path to the markdown script file'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output.fcpxml',
        help='Output FCPXML file path (default: output.fcpxml)'
    )
    
    parser.add_argument(
        '--pexels-key',
        type=str,
        help='Pexels API key (can also be set via PEXELS_API_KEY environment variable)'
    )
    
    parser.add_argument(
        '--resolve',
        action='store_true',
        help='Enable DaVinci Resolve integration (import timeline and assets)'
    )
    
    parser.add_argument(
        '--no-fetch',
        action='store_true',
        help='Skip asset fetching and generate empty timeline with gaps only'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose debug logging'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory for temporary files and downloaded assets'
    )
    
    parser.add_argument(
        '--disable-youtube',
        action='store_true',
        help='Disable YouTube asset fetching'
    )
    
    parser.add_argument(
        '--disable-pexels',
        action='store_true',
        help='Disable Pexels asset fetching'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse and generate FCPXML without fetching assets (implies --no-fetch)'
    )
    
    parser.add_argument(
        '--skip-failed-beats',
        action='store_true',
        help='Continue processing if some beats fail to fetch assets (graceful degradation)'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of parallel download threads (default: 4)'
    )
    
    parser.add_argument(
        '--disable-cache',
        action='store_true',
        help='Disable persistent asset caching'
    )

    parser.add_argument(
        '--prefer-youtube',
        action='store_true',
        help='Always try YouTube before Pexels (default: prefer Pexels stock for '
             'generic beats, YouTube for specific ones)'
    )

    parser.add_argument(
        '--disable-llm-queries',
        action='store_true',
        help='Disable LLM (Gemini) B-roll query generation and use heuristics only'
    )

    parser.add_argument(
        '--game',
        type=str,
        help='Game the script is about (e.g. "Dark Souls"). Activates the game '
             'b-roll pipeline: beats are matched to chaptered gameplay videos '
             'by extracted entity. Can also be set with a "game:" header in the '
             'script; this flag wins. Requires GEMINI_API_KEY.'
    )

    parser.add_argument(
        '--wiki-subdomain',
        type=str,
        help='Fandom wiki subdomain for the game (e.g. "darksouls" for '
             'darksouls.fandom.com). Only needed when the guess from the game '
             'title is wrong.'
    )

    parser.add_argument(
        '--vo',
        type=str,
        metavar='AUDIO',
        help='Recorded voiceover audio file. Beats are conformed to its real '
             'timing (local Whisper transcription with word timestamps) so '
             'cuts land on your pauses instead of word-count estimates. '
             'Requires: pip install "screenwrite[vo]". Combine with --dry-run '
             'for a pacing preview without downloads.'
    )

    parser.add_argument(
        '--whisper-model',
        type=str,
        help='faster-whisper model for --vo transcription (default: small.en)'
    )

    parser.add_argument(
        '--resolve-fcpxml',
        action='store_true',
        help='With --resolve: force the legacy FCPXML import instead of the '
             'native project build (bins per beat, stacked alternates, markers)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear all cached beats and assets before running'
    )
    
    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments and provide helpful error messages.
    
    Args:
        args: Parsed command-line arguments
        
    Raises:
        InputValidationError: If validation fails
        OutputError: If output validation fails
    """
    # Validate script file using comprehensive validation
    try:
        validation_result = validate_markdown_file(args.script)
        
        if not validation_result.is_valid:
            raise InputValidationError(validation_result.error_message)
        
        # Print any warnings from script validation
        for warning in validation_result.warnings:
            print(f"Warning: {warning}", file=sys.stderr)
            
    except InputValidationError:
        raise
    except Exception as e:
        raise InputValidationError(f"Failed to validate script file: {e}")
    
    # Validate and ensure output directory
    try:
        output_result = ensure_output_directory(args.output)
        
        if not output_result.is_valid:
            raise OutputError(output_result.error_message)
        
        # Print any warnings from output validation
        for warning in output_result.warnings:
            print(f"Info: {warning}", file=sys.stderr)
            
    except OutputError:
        raise
    except Exception as e:
        raise OutputError(f"Failed to validate output path: {e}")
    
    # Check for FFmpeg dependency (now mandatory for fetching).
    # ffmpeg's version flag is '-version' (single dash); '--version' makes some
    # builds exit non-zero and falsely fail the check.
    if not args.no_fetch:
        ffmpeg_result = check_dependency('ffmpeg', 'FFmpeg', version_flag='-version')
        if not ffmpeg_result.is_valid:
            raise DependencyError(
                f"FFmpeg is required for asset fetching. Details: {ffmpeg_result.error_message}\n"
                f"Please install FFmpeg and ensure it is in your system PATH, or use --no-fetch."
            )
    
    # Validate API key configuration
    pexels_key = args.pexels_key or os.getenv('PEXELS_API_KEY')
    if pexels_key and not args.disable_pexels:
        validation_result = validate_api_key(pexels_key, 'Pexels')
        if not validation_result.is_valid:
            raise InputValidationError(
                f"Invalid Pexels API key: {validation_result.error_message}\n"
                f"Please provide a valid key or use --disable-pexels"
            )
        
        # Print any API key warnings
        for warning in validation_result.warnings:
            print(f"Warning: {warning}", file=sys.stderr)
    
    elif not pexels_key and not args.disable_pexels and not args.no_fetch:
        print(f"Warning: No Pexels API key provided", file=sys.stderr)
        print(f"Pexels fetching will be disabled. To enable:", file=sys.stderr)
        print(f"  - Use --pexels-key YOUR_KEY", file=sys.stderr)
        print(f"  - Set PEXELS_API_KEY environment variable", file=sys.stderr)
        print(f"  - Use --disable-pexels to suppress this warning", file=sys.stderr)
    
    # Validate VO conform prerequisites early (before any downloads)
    if args.vo:
        if not Path(args.vo).is_file():
            raise InputValidationError(f"VO audio file not found: {args.vo}")
        import importlib.util
        if importlib.util.find_spec('faster_whisper') is None:
            raise DependencyError(
                "--vo requires faster-whisper, which is not installed.\n"
                "Install it with: pip install 'screenwrite[vo]' "
                "(or pip install faster-whisper)"
            )
    elif args.whisper_model:
        print("Warning: --whisper-model has no effect without --vo", file=sys.stderr)

    # Check for conflicting options
    if args.disable_youtube and args.disable_pexels and not args.no_fetch:
        raise InputValidationError(
            "Cannot disable both YouTube and Pexels fetching without --no-fetch. "
            "Either enable at least one fetcher or use --no-fetch for empty timeline."
        )
    
    # Validate output directory if specified
    if args.output_dir:
        output_dir_path = Path(args.output_dir)
        if output_dir_path.exists() and not output_dir_path.is_dir():
            raise OutputError(
                f"Output directory path exists but is not a directory: {args.output_dir}"
            )





def print_workflow_summary(result: dict) -> None:
    """
    Print a summary of the workflow results.
    
    Args:
        result: Workflow result dictionary from VideoOrchestrator
    """
    print("\n" + "="*60)
    print("WORKFLOW SUMMARY")
    print("="*60)
    
    print(f"Status: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Script: {result['script_path']}")
    print(f"Output: {result['output_path']}")
    print(f"Beats processed: {result['beats_count']}")
    
    # Display timeline duration if available
    if 'total_duration' in result and result['total_duration']:
        minutes, seconds = divmod(int(result['total_duration']), 60)
        if minutes > 0:
            duration_str = f"{minutes}m {seconds}s"
        else:
            duration_str = f"{seconds}s"
        print(f"Timeline duration: {duration_str}")
    
    if result.get('vo_conformed'):
        print(f"VO conformed: Yes ({result.get('vo_matched_beats', '?')}/"
              f"{result['beats_count']} beats matched)")
    print(f"Assets fetched: {result['assets_fetched']}")
    print(f"FCPXML generated: {'Yes' if result['fcpxml_generated'] else 'No'}")
    if result.get('resolve_native_built'):
        print("Resolve: native project built (bins + stacked alternates + markers)")
    else:
        print(f"Resolve imported: {'Yes' if result['resolve_imported'] else 'No'}")
    
    # Print detailed metrics
    if result['beats_count'] > 0:
        success_rate = (result['assets_fetched'] / result['beats_count']) * 100 if result['beats_count'] > 0 else 0
        print(f"\nAsset Fetching Metrics:")
        print(f"  Total beats: {result['beats_count']}")
        print(f"  Assets fetched: {result['assets_fetched']}")
        print(f"  Success rate: {success_rate:.1f}%")
        if result['beats_count'] != result['assets_fetched']:
            print(f"  Skipped/failed: {result['beats_count'] - result['assets_fetched']}")
    
    # Print game-mode coverage (which source each class of beat got)
    coverage = result.get('coverage')
    if coverage:
        counts = coverage['counts']
        print(f"\nGame B-roll Coverage:")
        print(f"  Entity beats with gameplay clips: {counts['game_entity_clips']}")
        print(f"  Entity beats with wiki stills:    {counts['game_entity_stills']}")
        print(f"  Entity beats uncovered (manual):  {counts['game_entity_uncovered']}")
        print(f"  Abstract beats with stock:        {counts['abstract_stock']}")
        print(f"  Abstract beats uncovered:         {counts['abstract_uncovered']}")
        print(f"  Manual-fill beats (by design):    {counts['manual_fill']}")

    # Print warnings
    if result['warnings']:
        print(f"\nWarnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    # Print errors
    if result['errors']:
        print(f"\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("="*60)


def main() -> int:
    """
    Main CLI entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Load environment variables from a project-local .env, if present, so
        # PEXELS_API_KEY / GEMINI_API_KEY can be configured there.
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        # Parse command-line arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Handle dry-run mode
        if args.dry_run:
            args.no_fetch = True
            print("Dry-run mode: skipping asset fetching", file=sys.stderr)
        
        # Set up logging
        setup_logging(args.verbose)
        
        # Validate arguments with comprehensive error handling
        validate_arguments(args)
        
        # Clear cache if requested
        if args.clear_cache:
            print("Clearing cache...", file=sys.stderr)
            clear_cache()
        
        # Lint script for quality issues (verbose mode)
        if args.verbose:
            try:
                lint_issues = lint_script_file(args.script)
                print_lint_issues(lint_issues, verbose=True)
            except Exception as e:
                logger.debug(f"Script linting failed: {e}")
        
        # Get API key from argument or environment
        pexels_key = args.pexels_key or os.getenv('PEXELS_API_KEY')
        
        # Configure orchestrator
        orchestrator_config = {
            'pexels_api_key': pexels_key,
            'output_dir': args.output_dir,
            'youtube_enabled': not args.disable_youtube,
            'pexels_enabled': not args.disable_pexels and bool(pexels_key),
            'resolve_enabled': args.resolve,
            'skip_failed_beats': args.skip_failed_beats,
            'max_workers': args.max_workers,
            'enable_asset_cache': not args.disable_cache,
            'prefer_stock_for_generic': not args.prefer_youtube,
            'use_llm_queries': not args.disable_llm_queries,
            'game': args.game,
            'wiki_subdomain': args.wiki_subdomain,
            'vo_path': args.vo,
            'whisper_model': args.whisper_model,
            'resolve_force_fcpxml': args.resolve_fcpxml,
            'verbose': args.verbose
        }
        
        # Get logger for status messages
        logger = logging.getLogger(__name__)
        
        print(f"Starting screenwrite...")
        print(f"Script: {args.script}")
        print(f"Output: {args.output}")
        
        if args.verbose:
            logger.debug("Configuration:")
            logger.debug(f"  Script: {args.script}")
            logger.debug(f"  Output: {args.output}")
            logger.debug(f"  Output directory: {args.output_dir or 'default'}")
            logger.debug(f"  YouTube enabled: {orchestrator_config['youtube_enabled']}")
            logger.debug(f"  Pexels enabled: {orchestrator_config['pexels_enabled']}")
            logger.debug(f"  Resolve integration: {orchestrator_config['resolve_enabled']}")
            logger.debug(f"  Pexels API key: {'*' * 5 + pexels_key[-5:] if pexels_key else 'Not set'}")
            logger.debug(f"  FFmpeg: Available")
        
        # Create and run orchestrator
        with VideoOrchestrator(**orchestrator_config) as orchestrator:
            # Execute workflow
            result = orchestrator.orchestrate(
                script_path=args.script,
                output_path=args.output,
                skip_fetch=args.no_fetch
            )
            
            # Print summary
            print_workflow_summary(result)
            
            # Return appropriate exit code
            return 0 if result['success'] else 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    
    except InputValidationError as e:
        print(f"\nInput validation error: {e}", file=sys.stderr)
        return 1
    
    except OutputError as e:
        print(f"\nOutput error: {e}", file=sys.stderr)
        return 1
    
    except DependencyError as e:
        print(f"\nDependency error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        
        # Log detailed error information if verbose mode is available
        verbose = getattr(args, 'verbose', False) if 'args' in locals() else False
        if verbose:
            import traceback
            traceback.print_exc()
        else:
            print("Run with --verbose for detailed error information.", file=sys.stderr)
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
