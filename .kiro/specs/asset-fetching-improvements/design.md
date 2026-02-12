# Design Document: Asset Fetching Improvements

## Overview

This design addresses two critical issues in the asset fetching system:

1. **Query Text Bug**: The system uses stale or incorrect query text when fetching assets because beat updates from the frontend are not persisted before the fetch operation begins
2. **Poor User Experience**: Users receive no feedback during asset fetching and cannot preview or select from multiple asset candidates

The solution implements a two-phase approach: (1) fix the query bug by ensuring beat data is saved before fetching, and (2) add a search preview system that allows users to see thumbnails and select assets before downloading.

## Architecture

### Current Flow (Problematic)

```
User edits beat → Frontend state updates → User clicks "Fetch Asset" 
→ refreshBeatAsset() called → Backend reads OLD beat data from session state 
→ Wrong query used
```

### Fixed Flow

```
User edits beat → Frontend state updates → User saves changes 
→ updateBeats() persists to backend → User clicks "Fetch Asset" 
→ refreshBeatAsset() called → Backend reads CURRENT beat data 
→ Correct query used
```

### New Search Preview Flow

```
User clicks "Fetch Asset" → Frontend calls searchAssets() 
→ Backend searches without downloading → Returns metadata + thumbnails 
→ Frontend shows modal with previews → User selects asset 
→ Frontend calls downloadAsset() → Backend downloads selected asset 
→ Frontend updates UI with downloaded asset
```

## Components and Interfaces

### Backend Components

#### 1. Search Endpoint (`/session/<session_id>/search/<beat_id>`)

**Purpose**: Search for asset candidates without downloading

**Request**: POST with optional custom query
```python
{
    "custom_query": Optional[str],  # Override beat's search terms
    "source": Optional[str]  # "youtube", "stock", or "auto"
}
```

**Response**: Asset candidate metadata
```python
{
    "success": bool,
    "candidates": [
        {
            "id": str,  # Unique identifier for this candidate
            "title": str,
            "thumbnail_url": str,
            "duration": float,  # in seconds
            "source": str,  # "youtube" or "pexels"
            "query_used": str,  # The actual query that found this
            "metadata": dict  # Source-specific metadata
        }
    ],
    "query_used": str,  # The query that was executed
    "beat_id": str
}
```

#### 2. Download Endpoint (`/session/<session_id>/download/<beat_id>`)

**Purpose**: Download a specific asset candidate

**Request**: POST with candidate selection
```python
{
    "candidate_id": str,
    "source": str,  # "youtube" or "pexels"
    "metadata": dict  # Candidate metadata from search
}
```

**Response**: Downloaded asset information
```python
{
    "success": bool,
    "file_path": str,
    "beat_id": str,
    "error": Optional[str]
}
```

#### 3. Modified Refresh Endpoint

**Purpose**: Ensure beat data is current before any operation

**Changes**:
- Add logging to trace query text through pipeline
- Verify field name mapping (youtube_phrase → youtube_search_phrase)
- Return detailed error messages

#### 4. AssetOrchestrator Enhancements

**New Method**: `search_assets()`
```python
def search_assets(
    self,
    youtube_query: str,
    stock_query: str,
    duration: float,
    count: int = 5
) -> List[AssetCandidate]:
    """
    Search for assets without downloading.
    
    Returns metadata for candidates including thumbnails.
    """
```

**AssetCandidate Structure**:
```python
@dataclass
class AssetCandidate:
    id: str
    title: str
    thumbnail_url: str
    duration: float
    source: str  # "youtube" or "pexels"
    metadata: dict  # Source-specific data needed for download
```

### Frontend Components

#### 1. AssetSearchModal Component

**Purpose**: Display search results with thumbnail previews

**Props**:
```typescript
interface AssetSearchModalProps {
    sessionId: string
    beatId: string
    isOpen: boolean
    onClose: () => void
    onAssetSelected: (beatId: string, filePath: string) => void
}
```

**Features**:
- Grid layout of thumbnail previews
- Display title, duration, source for each candidate
- Loading state during search
- Error handling
- Custom query input field
- Download progress indicator

#### 2. BeatAsset Component Updates

**Changes**:
- Replace direct refresh call with modal trigger
- Show search modal instead of immediate fetch
- Display download progress when asset is being downloaded
- Handle error states from download failures

#### 3. BeatList Component Updates

**Changes**:
- Ensure beat updates are saved before allowing asset fetch
- Pass modal state management to BeatAsset components
- Handle asset selection callbacks

### Data Flow

#### Phase 1: Fix Query Bug

1. **Frontend**: User edits beat in BeatList
2. **Frontend**: handleSave() calls updateBeats() API
3. **Backend**: /session/<id>/beats endpoint saves beat data
4. **Frontend**: User clicks "Fetch Asset"
5. **Backend**: /session/<id>/fetch/<beat_id> reads LATEST beat data
6. **Backend**: Correct query text used in AssetOrchestrator

#### Phase 2: Search Preview

1. **Frontend**: User clicks "Fetch Asset" → Opens AssetSearchModal
2. **Frontend**: Modal calls searchAssets(sessionId, beatId)
3. **Backend**: /session/<id>/search/<beat_id> endpoint
4. **Backend**: AssetOrchestrator.search_assets() queries sources
5. **Backend**: Returns candidate metadata (no downloads)
6. **Frontend**: Modal displays thumbnails in grid
7. **Frontend**: User selects candidate
8. **Frontend**: Calls downloadAsset(sessionId, beatId, candidateId)
9. **Backend**: /session/<id>/download/<beat_id> downloads selected asset
10. **Backend**: Returns file path
11. **Frontend**: Updates assets state, closes modal

## Data Models

### Beat Model Consistency

**Backend (Python)**:
```python
@dataclass
class Beat:
    id: str
    text: str
    stock_keyword: str
    youtube_search_phrase: str  # Note: different from frontend
    duration: float
    visual_type: str
    visual_content: Optional[str]
```

**Frontend (TypeScript)**:
```typescript
interface Beat {
    id: string
    text: string
    stock_keyword: string
    youtube_phrase: string  // Note: different from backend
    duration: number
    visual_type: string
    visual_content?: string
}
```

**Mapping Strategy**:
- Backend accepts both `youtube_phrase` and `youtube_search_phrase`
- When reading from session state, check both field names
- When saving to session state, normalize to `youtube_phrase` for frontend compatibility
- Log field name mappings for debugging

### Session State Structure

```python
{
    "sessionId": str,
    "status": str,  # "idle", "fetching", "complete", "error"
    "beats": List[dict],  # Beat objects as dicts
    "assets": Dict[str, Union[str, List[str]]],  # beat_id → file path(s)
    "config": dict,
    "createdAt": str,
    "updatedAt": str,
    "completedAt": Optional[str]
}
```

### Asset Candidate Model

**Backend**:
```python
@dataclass
class AssetCandidate:
    id: str  # Unique identifier (video_id for YouTube, id for Pexels)
    title: str
    thumbnail_url: str
    duration: float
    source: str  # "youtube" or "pexels"
    metadata: dict  # Source-specific data
```

**Frontend**:
```typescript
interface AssetCandidate {
    id: string
    title: string
    thumbnail_url: string
    duration: number
    source: 'youtube' | 'pexels'
    metadata: Record<string, any>
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several properties can be consolidated:

**Consolidations**:
- Properties 2.2 and 8.2 both test that candidates have required fields → Combine into one property
- Properties 1.3 and 1.2 both test query correctness → Combine into one property about query flow
- Properties 4.2, 4.3, and 4.5 all test asset storage → Combine into one comprehensive storage property
- Properties 6.1, 6.2, 6.3, and 6.5 all test field name mapping → Combine into one round-trip property
- Properties 3.3 and 3.4 both test download completion states → Combine into one property about state transitions

**Redundancies Eliminated**:
- Property 1.5 is subsumed by the comprehensive field mapping property (6.x consolidated)
- Property 2.4 is redundant with 2.2 (both test candidate field completeness)
- Property 8.3 is redundant with 4.2 (both test download result storage)

### Correctness Properties

Property 1: Query text persistence and usage
*For any* beat with modified search terms, when the beat is saved and then a fetch is initiated, the Asset_Orchestrator should receive and use the exact modified search terms, not stale or incorrect terms.
**Validates: Requirements 1.1, 1.2, 1.3**

Property 2: Field name round-trip consistency
*For any* beat data sent from Frontend with youtube_phrase field, when it is saved to the Backend and read back, the data should be correctly mapped to youtube_search_phrase internally and back to youtube_phrase when returned to Frontend.
**Validates: Requirements 1.5, 6.1, 6.2, 6.3, 6.5**

Property 3: Search without download
*For any* search operation, when the search endpoint is called, the system should return candidate metadata without creating any downloaded files on disk.
**Validates: Requirements 2.1**

Property 4: Candidate metadata completeness
*For any* asset candidate returned by the search endpoint, the candidate should include all required fields: id, title, thumbnail_url, duration, source, and query_used.
**Validates: Requirements 2.2, 8.2**

Property 5: Single asset download on selection
*For any* asset candidate selection, when a user selects one candidate from multiple options, exactly one download should be initiated and it should be for the selected candidate.
**Validates: Requirements 2.5**

Property 6: Download state transitions
*For any* asset download operation, when the download completes (successfully or with error), the system should transition to the appropriate final state: either (asset_path set, loading=false) for success or (error_message set, loading=false) for failure.
**Validates: Requirements 3.3, 3.4**

Property 7: Independent asset progress tracking
*For any* set of concurrent asset downloads, each download should maintain independent progress state such that updating one download's progress does not affect another's progress state.
**Validates: Requirements 3.5**

Property 8: Asset storage with metadata
*For any* downloaded asset, when stored in Session_State, the system should include the file path, beat_id, and query metadata, and this data should be retrievable for display.
**Validates: Requirements 4.2, 4.3, 4.5**

Property 9: Search preserves existing assets
*For any* beat with an existing asset, when a new search is initiated (but not completed with download), the existing asset should remain unchanged in Session_State.
**Validates: Requirements 4.4**

Property 10: Exploratory search immutability
*For any* search with a custom query, when the search is performed without explicit save, the beat's stored search terms (youtube_phrase, stock_keyword) should remain unchanged.
**Validates: Requirements 5.2, 5.5**

Property 11: Optional search term update on download
*For any* asset download with a custom query, when the user chooses to update search terms, the beat's search terms should be updated; when the user chooses not to update, the beat's search terms should remain unchanged.
**Validates: Requirements 5.4**

Property 12: Error response format consistency
*For any* API error (search failure, download failure, validation error), the response should be a JSON object with an "error" field containing a descriptive message and an appropriate HTTP status code.
**Validates: Requirements 7.3, 8.4**

Property 13: API response structure consistency
*For any* successful API response, all field names should follow snake_case convention, and the search endpoint should return an array structure while the download endpoint should return an object structure.
**Validates: Requirements 8.1, 8.5**

## Error Handling

### Frontend Error Handling

**Network Errors**:
- Display user-friendly error messages in modal
- Provide retry button for failed searches
- Show specific error for timeout vs. server error

**Validation Errors**:
- Validate beat has search terms before allowing fetch
- Show warning if both youtube_phrase and stock_keyword are empty
- Disable fetch button when beat is in invalid state

**State Errors**:
- Handle race conditions between multiple fetch operations
- Prevent duplicate downloads of same asset
- Clear error state when modal is closed

### Backend Error Handling

**Session Errors**:
- Return 404 if session doesn't exist
- Return 404 if beat_id not found in session
- Validate session state structure before operations

**Search Errors**:
- Catch and log API errors from YouTube/Pexels
- Return empty candidate list if all sources fail
- Include error details in response for debugging

**Download Errors**:
- Catch download failures and return descriptive errors
- Clean up partial downloads on failure
- Log full error context (beat_id, query, source, exception)

**Field Mapping Errors**:
- Accept both youtube_phrase and youtube_search_phrase
- Log warnings for unexpected field names
- Provide default empty strings for missing fields

### Error Logging Strategy

**Log Levels**:
- ERROR: Download failures, API errors, unexpected exceptions
- WARNING: Field name mismatches, empty search results
- INFO: Search operations, download completions, query text used
- DEBUG: Field mappings, state transitions, API calls

**Log Context**:
- Always include: session_id, beat_id, timestamp
- For searches: query_text, source, candidate_count
- For downloads: candidate_id, file_path, duration
- For errors: exception type, stack trace, request data

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Test specific field name mappings (youtube_phrase ↔ youtube_search_phrase)
- Test empty search results handling
- Test modal open/close behavior
- Test API error response formats
- Test specific download failure scenarios

**Property-Based Tests**: Verify universal properties across all inputs
- Test query text preservation across random beat modifications
- Test field name round-trip with randomly generated beat data
- Test candidate metadata completeness with random search results
- Test download state transitions with random success/failure scenarios
- Test concurrent download independence with random operation sequences

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python backend tests, `fast-check` for TypeScript frontend tests

**Test Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with: `Feature: asset-fetching-improvements, Property N: [property text]`
- Use custom generators for Beat, AssetCandidate, and SessionState objects

**Example Test Structure** (Python):
```python
from hypothesis import given, strategies as st

@given(
    beat=beat_strategy(),
    modified_query=st.text(min_size=1, max_size=100)
)
def test_query_persistence_property(beat, modified_query):
    """
    Feature: asset-fetching-improvements, Property 1: Query text persistence
    
    For any beat with modified search terms, the orchestrator should use
    the exact modified terms.
    """
    # Test implementation
```

### Testing Priorities

**Phase 1 (Query Bug Fix)**:
1. Property test: Query text persistence (Property 1)
2. Property test: Field name round-trip (Property 2)
3. Unit test: Specific field mapping examples
4. Integration test: End-to-end beat edit → save → fetch flow

**Phase 2 (Search Preview)**:
1. Property test: Search without download (Property 3)
2. Property test: Candidate metadata completeness (Property 4)
3. Unit test: Modal rendering with sample candidates
4. Property test: Single asset download (Property 5)
5. Integration test: Search → preview → select → download flow

**Phase 3 (Enhanced UX)**:
1. Property test: Download state transitions (Property 6)
2. Property test: Independent progress tracking (Property 7)
3. Property test: Search preserves assets (Property 9)
4. Unit test: Error message display
5. Integration test: Multiple concurrent downloads

### Test Data Generators

**Beat Generator** (Hypothesis):
```python
@st.composite
def beat_strategy(draw):
    return {
        'id': draw(st.text(min_size=5, max_size=20)),
        'text': draw(st.text(min_size=10, max_size=200)),
        'youtube_phrase': draw(st.text(min_size=0, max_size=100)),
        'stock_keyword': draw(st.text(min_size=0, max_size=100)),
        'duration': draw(st.floats(min_value=3.0, max_value=10.0))
    }
```

**AssetCandidate Generator** (fast-check):
```typescript
const assetCandidateArbitrary = fc.record({
    id: fc.string({ minLength: 5, maxLength: 50 }),
    title: fc.string({ minLength: 1, maxLength: 100 }),
    thumbnail_url: fc.webUrl(),
    duration: fc.float({ min: 1, max: 600 }),
    source: fc.constantFrom('youtube', 'pexels'),
    metadata: fc.dictionary(fc.string(), fc.anything())
})
```

## Implementation Notes

### Phase 1: Query Bug Fix (Priority 1)

**Backend Changes**:
1. Modify `/session/<id>/fetch/<beat_id>` endpoint to log query text at entry
2. Add field name mapping logic to accept both youtube_phrase and youtube_search_phrase
3. Add validation to ensure beat data is current (check updatedAt timestamp)
4. Log the complete query flow: endpoint → beat data → orchestrator

**Frontend Changes**:
1. Ensure BeatList.handleSave() calls updateBeats() before allowing fetch
2. Add loading state during beat save operation
3. Disable "Fetch Asset" button until save completes
4. Show toast notification on successful save

**Testing**:
- Write property test for query persistence
- Write unit tests for field name mapping
- Manual testing: Edit beat → save → fetch → verify logs show correct query

### Phase 2: Search Preview (Priority 2)

**Backend Changes**:
1. Create `/session/<id>/search/<beat_id>` endpoint
2. Implement AssetOrchestrator.search_assets() method
3. Add AssetCandidate dataclass
4. Modify YouTube and Pexels fetchers to support search-only mode
5. Create `/session/<id>/download/<beat_id>` endpoint

**Frontend Changes**:
1. Create AssetSearchModal component
2. Add searchAssets() and downloadAsset() API functions
3. Modify BeatAsset to trigger modal instead of direct fetch
4. Add thumbnail grid layout in modal
5. Add download progress indicator

**Testing**:
- Write property test for search without download
- Write property test for candidate metadata completeness
- Write unit test for modal rendering
- Integration test: Full search → select → download flow

### Phase 3: Enhanced UX (Priority 3)

**Backend Changes**:
1. Add progress tracking to download operations
2. Implement concurrent download management
3. Add custom query support to search endpoint

**Frontend Changes**:
1. Add custom query input to modal
2. Implement per-asset progress tracking
3. Add error recovery UI
4. Add option to update beat search terms on download

**Testing**:
- Write property test for independent progress tracking
- Write property test for exploratory search immutability
- Write unit tests for error states
- Integration test: Concurrent downloads

### Migration Strategy

**Backward Compatibility**:
- Keep existing `/session/<id>/fetch/<beat_id>` endpoint working
- Support both old (direct fetch) and new (search + download) flows
- Gradually migrate UI to use new flow
- Deprecate old endpoint after migration complete

**Data Migration**:
- No schema changes required
- Existing assets remain compatible
- Session state structure unchanged

### Performance Considerations

**Search Performance**:
- Limit search to 5 candidates per source by default
- Implement timeout for search operations (10 seconds)
- Cache thumbnail URLs to avoid repeated fetches
- Use concurrent requests to YouTube and Pexels APIs

**Download Performance**:
- Download only selected asset (not all candidates)
- Show progress for downloads > 5MB
- Implement download cancellation
- Clean up failed downloads immediately

**Frontend Performance**:
- Lazy load thumbnail images in modal
- Virtualize candidate list for > 20 results
- Debounce custom query input
- Use React.memo for candidate cards

## Security Considerations

**Input Validation**:
- Sanitize custom query inputs
- Validate beat_id format
- Validate candidate_id before download
- Limit query length to prevent abuse

**API Security**:
- Validate session_id exists before operations
- Check file paths don't escape session directory
- Rate limit search and download endpoints
- Validate thumbnail URLs before displaying

**Error Information**:
- Don't expose internal paths in error messages
- Sanitize exception messages before returning to frontend
- Log sensitive errors server-side only
- Return generic errors for security-related failures
