# Implementation Plan: Asset Fetching Improvements

## Overview

This implementation plan breaks down the asset fetching improvements into three phases: (1) fixing the query bug by ensuring beat data persistence, (2) implementing search preview functionality with thumbnails, and (3) enhancing the user experience with progress tracking and custom queries. Each phase builds on the previous one, with testing integrated throughout.

## Tasks

- [x] 1. Phase 1: Fix Query Text Bug
  - [x] 1.1 Add field name mapping to backend fetch endpoint
    - Modify `/session/<session_id>/fetch/<beat_id>` endpoint in `webapp/backend/routes/fetch.py`
    - Add logic to accept both `youtube_phrase` and `youtube_search_phrase` field names
    - Map frontend field names to backend Beat class properties
    - Add logging to trace query text through the pipeline
    - _Requirements: 1.1, 1.2, 1.3, 6.1, 6.2, 6.3_
  
  - [x] 1.2 Write property test for query text persistence
    - **Property 1: Query text persistence and usage**
    - **Validates: Requirements 1.1, 1.2, 1.3**
    - Test that modified search terms are correctly used by Asset_Orchestrator
    - Use hypothesis to generate random beat modifications
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [x] 1.3 Write property test for field name round-trip consistency
    - **Property 2: Field name round-trip consistency**
    - **Validates: Requirements 1.5, 6.1, 6.2, 6.3, 6.5**
    - Test that youtube_phrase correctly maps to youtube_search_phrase and back
    - Use hypothesis to generate random beat data with various field names
    - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.5_
  
  - [x] 1.4 Update frontend to save beats before fetch
    - Modify `BeatList.tsx` handleSave() to ensure updateBeats() completes before fetch
    - Add loading state during beat save operation
    - Disable "Fetch Asset" button until save completes
    - _Requirements: 1.1_
  
  - [x] 1.5 Write unit tests for field name mapping
    - Test specific examples: youtube_phrase → youtube_search_phrase
    - Test backward compatibility with both field names
    - Test default values for missing fields
    - _Requirements: 6.1, 6.2, 6.3_

- [ ] 2. Checkpoint - Verify query bug is fixed
  - Ensure all tests pass, manually test beat edit → save → fetch flow, verify logs show correct query text

- [x] 3. Phase 2: Implement Search Preview Backend
  - [x] 3.1 Create AssetCandidate data model
    - Add `AssetCandidate` dataclass in `screenwrite/fetchers/asset_orchestrator.py`
    - Include fields: id, title, thumbnail_url, duration, source, metadata
    - _Requirements: 2.2, 8.2_
  
  - [x] 3.2 Implement search-only mode in AssetOrchestrator
    - Add `search_assets()` method to AssetOrchestrator class
    - Modify YouTube and Pexels fetchers to support search without download
    - Return list of AssetCandidate objects with metadata
    - _Requirements: 2.1_
  
  - [x] 3.3 Create search endpoint
    - Add `/session/<session_id>/search/<beat_id>` POST endpoint in `webapp/backend/routes/fetch.py`
    - Accept optional custom_query and source parameters
    - Call AssetOrchestrator.search_assets()
    - Return JSON array of asset candidates
    - _Requirements: 2.1, 2.2, 5.1, 8.1_
  
  - [x] 3.4 Write property test for search without download
    - **Property 3: Search without download**
    - **Validates: Requirements 2.1**
    - Test that search operations don't create files on disk
    - Use hypothesis to generate random search queries
    - _Requirements: 2.1_
  
  - [x] 3.5 Write property test for candidate metadata completeness
    - **Property 4: Candidate metadata completeness**
    - **Validates: Requirements 2.2, 8.2**
    - Test that all candidates have required fields
    - Use hypothesis to generate random search results
    - _Requirements: 2.2, 8.2_

- [x] 4. Phase 2: Implement Download Endpoint
  - [x] 4.1 Create download endpoint
    - Add `/session/<session_id>/download/<beat_id>` POST endpoint in `webapp/backend/routes/fetch.py`
    - Accept candidate_id, source, and metadata parameters
    - Download only the selected asset
    - Update session state with downloaded asset path
    - Return file path and metadata
    - _Requirements: 2.5, 4.2, 8.3_
  
  - [x] 4.2 Write property test for single asset download
    - **Property 5: Single asset download on selection**
    - **Validates: Requirements 2.5**
    - Test that selecting one candidate downloads exactly one asset
    - Use hypothesis to generate random candidate selections
    - _Requirements: 2.5_
  
  - [x] 4.3 Write property test for asset storage with metadata
    - **Property 8: Asset storage with metadata**
    - **Validates: Requirements 4.2, 4.3, 4.5**
    - Test that downloaded assets are stored with beat_id and query metadata
    - Use hypothesis to generate random downloads
    - _Requirements: 4.2, 4.3, 4.5_

- [-] 5. Phase 2: Implement Search Preview Frontend
  - [x] 5.1 Create AssetSearchModal component
    - Create new component in `webapp/frontend/src/components/AssetSearchModal.tsx`
    - Implement modal dialog with thumbnail grid layout
    - Display candidate title, thumbnail, duration, and source
    - Handle loading, error, and empty states
    - _Requirements: 2.3, 2.4_
  
  - [x] 5.2 Add search and download API functions
    - Add `searchAssets()` function to `webapp/frontend/src/services/api.ts`
    - Add `downloadAsset()` function to `webapp/frontend/src/services/api.ts`
    - Handle API errors and return typed responses
    - _Requirements: 2.1, 2.5_
  
  - [-] 5.3 Update BeatAsset component to use modal
    - Modify `BeatAsset.tsx` to trigger AssetSearchModal instead of direct fetch
    - Pass sessionId, beatId, and callbacks to modal
    - Handle asset selection callback
    - Show download progress indicator
    - _Requirements: 2.3, 3.1_
  
  - [ ] 5.4 Write unit test for modal rendering
    - Test modal displays with sample candidates
    - Test thumbnail grid layout
    - Test candidate selection interaction
    - _Requirements: 2.3, 2.4_

- [ ] 6. Checkpoint - Verify search preview works
  - Ensure all tests pass, manually test search → preview → select → download flow, verify thumbnails display correctly

- [ ] 7. Phase 3: Implement Download Progress Tracking
  - [ ] 7.1 Add download state management to frontend
    - Add download progress state to BeatAsset component
    - Track loading, progress, error states per beat
    - Update UI to show progress indicator during download
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [ ] 7.2 Implement download completion handling
    - Handle successful download: update asset path, dismiss loading
    - Handle failed download: show error message, allow retry
    - Clear error state when modal is closed
    - _Requirements: 3.3, 3.4_
  
  - [ ] 7.3 Write property test for download state transitions
    - **Property 6: Download state transitions**
    - **Validates: Requirements 3.3, 3.4**
    - Test that downloads transition to correct final states
    - Use fast-check to generate random success/failure scenarios
    - _Requirements: 3.3, 3.4_
  
  - [ ] 7.4 Write property test for independent progress tracking
    - **Property 7: Independent asset progress tracking**
    - **Validates: Requirements 3.5**
    - Test that concurrent downloads maintain independent state
    - Use fast-check to generate random concurrent operations
    - _Requirements: 3.5_

- [ ] 8. Phase 3: Implement Custom Query Search
  - [ ] 8.1 Add custom query input to modal
    - Add text input field to AssetSearchModal
    - Allow users to enter custom search queries
    - Update search API call to include custom query
    - _Requirements: 5.3_
  
  - [ ] 8.2 Implement exploratory search immutability
    - Ensure custom searches don't modify beat's stored search terms
    - Add option to update beat search terms on download
    - Update beat data only when user explicitly chooses to save
    - _Requirements: 5.2, 5.4, 5.5_
  
  - [ ] 8.3 Write property test for exploratory search immutability
    - **Property 10: Exploratory search immutability**
    - **Validates: Requirements 5.2, 5.5**
    - Test that custom searches don't modify beat search terms
    - Use fast-check to generate random custom queries
    - _Requirements: 5.2, 5.5_
  
  - [ ] 8.4 Write property test for optional search term update
    - **Property 11: Optional search term update on download**
    - **Validates: Requirements 5.4**
    - Test conditional update of beat search terms
    - Use fast-check to generate random user choices
    - _Requirements: 5.4_

- [ ] 9. Phase 3: Implement Asset Preservation
  - [ ] 9.1 Add asset preservation logic
    - Ensure new searches don't delete existing assets
    - Only update asset when download completes
    - Allow users to revert to previous asset
    - _Requirements: 4.4_
  
  - [ ] 9.2 Write property test for search preserves assets
    - **Property 9: Search preserves existing assets**
    - **Validates: Requirements 4.4**
    - Test that initiating search doesn't remove current asset
    - Use fast-check to generate random search sequences
    - _Requirements: 4.4_

- [ ] 10. Error Handling and Validation
  - [ ] 10.1 Implement backend error handling
    - Add try-catch blocks to all endpoints
    - Return consistent error response format
    - Log errors with full context (session_id, beat_id, query)
    - Handle empty search results gracefully
    - _Requirements: 7.2, 7.3, 8.4_
  
  - [ ] 10.2 Implement frontend error handling
    - Display user-friendly error messages in modal
    - Add retry button for failed searches
    - Validate beat has search terms before allowing fetch
    - Handle network timeouts and server errors
    - _Requirements: 3.4, 7.3_
  
  - [ ] 10.3 Write property test for error response format
    - **Property 12: Error response format consistency**
    - **Validates: Requirements 7.3, 8.4**
    - Test that all errors return consistent JSON format
    - Use hypothesis to generate random error scenarios
    - _Requirements: 7.3, 8.4_
  
  - [ ] 10.4 Write property test for API response structure
    - **Property 13: API response structure consistency**
    - **Validates: Requirements 8.1, 8.5**
    - Test that all responses follow snake_case convention
    - Use hypothesis to generate random API responses
    - _Requirements: 8.1, 8.5_

- [ ] 11. Final Integration and Polish
  - [ ] 11.1 Add loading states and transitions
    - Add smooth transitions between modal states
    - Show skeleton loaders during search
    - Add success animations on download complete
    - _Requirements: 3.1, 3.2_
  
  - [ ] 11.2 Optimize performance
    - Lazy load thumbnail images in modal
    - Implement download cancellation
    - Add timeout for search operations (10 seconds)
    - Clean up failed downloads immediately
    - _Requirements: 2.1, 3.4_
  
  - [ ] 11.3 Write integration tests
    - Test complete flow: edit → save → search → select → download
    - Test concurrent downloads for multiple beats
    - Test error recovery and retry flows
    - _Requirements: 1.1, 2.1, 2.5, 3.3, 3.4_

- [ ] 12. Final checkpoint - Ensure all tests pass
  - Run full test suite, verify all property tests pass with 100+ iterations, manually test all user flows, verify error handling works correctly

## Notes

- All tasks are required for comprehensive implementation
- Each property test should run minimum 100 iterations
- Property tests are tagged with feature name and property number
- Phase 1 (query bug fix) is highest priority and should be completed first
- Phase 2 (search preview) provides the core UX improvement
- Phase 3 (enhanced UX) adds polish and advanced features
- Integration tests validate end-to-end flows across all phases
