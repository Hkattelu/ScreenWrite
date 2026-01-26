# Implementation Plan: screenwrite

- [x] 1. Set up project structure and core Beat dataclass






  - Create directory structure: core/, parsing/, fetchers/, generators/
  - Implement Beat dataclass with auto-duration calculation
  - Add validation for 5-10 second duration range
  - _Requirements: 1.4, 1.5_

- [ ]* 1.1 Write property test for Beat duration bounds
  - **Feature: screenwrite, Property 1: Beat Duration Bounds**
  - **Validates: Requirements 1.1, 1.5**

- [ ]* 1.2 Write property test for Beat completeness
  - **Feature: screenwrite, Property 2: Beat Completeness**
  - **Validates: Requirements 1.4**

- [ ]* 1.3 Write property test for duration calculation accuracy
  - **Feature: screenwrite, Property 3: Duration Calculation Accuracy**
  - **Validates: Requirements 1.5**

- [x] 2. Implement script parser





  - Define a markdown script specification
  - Create ScriptParser class to parse markdown files
  - Implement text chunking algorithm for 5-10 second beats
  - Implement stock keyword generation from beat text
  - Implement YouTube search phrase generation from beat text
  - _Requirements: 1.1, 1.2, 1.3_

- [ ]* 2.1 Write property test for query generation non-emptiness
  - **Feature: screenwrite, Property 4: Query Generation Non-Emptiness**
  - **Validates: Requirements 1.2, 1.3**

- [x] 3. Implement YouTube asset fetcher





  - Create YouTubeClient class using yt-dlp
  - Implement YouTube search functionality
  - Implement video download with quality selection
  - Implement video trimming using ffmpeg
  - Add error handling for network failures and missing ffmpeg
  - _Requirements: 2.1, 2.3, 2.4, 7.3_

- [ ]* 3.1 Write property test for YouTube fetcher invocation
  - **Feature: screenwrite, Property 5: YouTube Fetcher Invocation**
  - **Validates: Requirements 2.1, 2.3**

- [ ]* 3.2 Write property test for video trimming
  - **Feature: screenwrite, Property 8: Video Trimming**
  - **Validates: Requirements 2.4**

- [x] 4. Implement Pexels asset fetcher





  - Create PexelsClient class using Pexels API
  - Implement API key handling (argument and environment variable)
  - Implement video search and download
  - Add error handling for missing API key and rate limits
  - _Requirements: 2.5, 2.6, 4.3_

- [ ]* 4.1 Write property test for Pexels fetcher invocation
  - **Feature: screenwrite, Property 7: Pexels Fetcher Invocation**
  - **Validates: Requirements 2.5**

- [x] 5. Implement asset fetcher orchestration with fallback





  - Create base AssetFetcher abstract class
  - Implement fallback logic: YouTube â†’ Pexels
  - Add error handling for all fetcher failures
  - _Requirements: 2.1, 2.2, 2.6, 7.1, 7.2_

- [ ]* 5.1 Write property test for fallback to Pexels
  - **Feature: screenwrite, Property 6: Fallback to Pexels**
  - **Validates: Requirements 2.2**

- [ ]* 5.2 Write property test for error handling continuity
  - **Feature: screenwrite, Property 9: Error Handling Continuity**
  - **Validates: Requirements 2.6, 7.1, 7.2**


- [x] 6. Implement FCPXML generator




  - Create XMLGenerator class using xml.etree.ElementTree
  - Implement FCPXML 1.8 root and format creation
  - Implement resource registration for video files
  - Implement spine track with gaps for each beat
  - Implement connected clips on Lane 1 for B-roll
  - Implement XML validation and pretty-printing
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ]* 6.1 Write property test for FCPXML validity
  - **Feature: screenwrite, Property 10: FCPXML Validity**
  - **Validates: Requirements 3.1**

- [ ]* 6.2 Write property test for spine gap completeness
  - **Feature: screenwrite, Property 11: Spine Gap Completeness**
  - **Validates: Requirements 3.2**

- [ ]* 6.3 Write property test for connected clips alignment
  - **Feature: screenwrite, Property 12: Connected Clips Alignment**
  - **Validates: Requirements 3.3**

- [ ]* 6.4 Write property test for resource reference validity
  - **Feature: screenwrite, Property 13: Resource Reference Validity**
  - **Validates: Requirements 3.4**

- [ ]* 6.5 Write property test for file output existence
  - **Feature: screenwrite, Property 14: File Output Existence**
  - **Validates: Requirements 3.5**

- [x] 7. Implement main orchestrator





  - Create VideoOrchestrator class to coordinate all components
  - Implement workflow: parse â†’ fetch â†’ generate
  - Add comprehensive error handling and logging
  - Implement optional Resolve integration
  - _Requirements: 2.1, 2.2, 3.1, 5.1, 5.2, 5.3, 5.4, 7.1, 7.2_

- [x] 8. Implement CLI interface





  - Create CLI using argparse
  - Add required arguments: script path, output path
  - Add optional arguments: --pexels-key, --resolve, --no-fetch, --verbose
  - Implement help text and error messages
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 8.1 Write property test for CLI argument acceptance
  - **Feature: screenwrite, Property 15: CLI Argument Acceptance**
  - **Validates: Requirements 4.1, 4.2**

- [ ]* 8.2 Write property test for environment variable support
  - **Feature: screenwrite, Property 16: Environment Variable Support**
  - **Validates: Requirements 4.3**

- [ ]* 8.3 Write property test for error message clarity
  - **Feature: screenwrite, Property 17: Error Message Clarity**
  - **Validates: Requirements 4.4, 7.4, 7.5**

- [ ]* 8.4 Write property test for help text availability
  - **Feature: screenwrite, Property 18: Help Text Availability**
  - **Validates: Requirements 4.5**

- [x] 9. Implement Resolve integration (optional)





  - Create ResolveIntegration class using fusionscript
  - Implement bin creation in Resolve project
  - Implement media import to bin
  - Implement FCPXML timeline import
  - Add error handling for Resolve unavailability
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 9.1 Write property test for Resolve bin creation
  - **Feature: screenwrite, Property 19: Resolve Bin Creation**
  - **Validates: Requirements 5.1**

- [ ]* 9.2 Write property test for Resolve asset import
  - **Feature: screenwrite, Property 20: Resolve Asset Import**
  - **Validates: Requirements 5.2**

- [ ]* 9.3 Write property test for Resolve timeline import
  - **Feature: screenwrite, Property 21: Resolve Timeline Import**
  - **Validates: Requirements 5.3**

- [ ]* 9.4 Write property test for graceful degradation without Resolve
  - **Feature: screenwrite, Property 22: Graceful Degradation Without Resolve**
  - **Validates: Requirements 5.4**

- [ ] 10. Checkpoint - Ensure all core functionality tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Add comprehensive error handling





  - Implement input validation for markdown files
  - Implement output directory creation or error handling
  - Implement network error retry logic
  - Implement graceful degradation for missing dependencies
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 11.1 Write property test for missing API key handling
  - **Feature: screenwrite, Property 23: Missing API Key Handling**
  - **Validates: Requirements 7.2**

- [ ]* 11.2 Write property test for FFmpeg unavailability handling
  - **Feature: screenwrite, Property 24: FFmpeg Unavailability Handling**
  - **Validates: Requirements 7.3**

- [ ]* 11.3 Write property test for output directory creation
  - **Feature: screenwrite, Property 25: Output Directory Creation**
  - **Validates: Requirements 7.5**

- [ ] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Create end-to-end integration test





  - Create sample markdown script for testing
  - Implement end-to-end test: parse â†’ fetch â†’ generate â†’ validate
  - Test with mocked external APIs
  - Verify FCPXML output is valid and importable
  - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [ ] 14. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.


