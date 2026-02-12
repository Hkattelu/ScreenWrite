# Requirements Document

## Introduction

This specification addresses critical bugs and user experience issues in the asset fetching system. The current implementation has two major problems: (1) incorrect query text being used when fetching assets, causing users to receive irrelevant results, and (2) lack of user feedback during the asset fetching process, leaving users uncertain about system status and unable to preview or select from multiple asset options.

The solution focuses on fixing the query bug, implementing search preview functionality with thumbnails, providing real-time download feedback, and enhancing asset selection capabilities.

## Glossary

- **Beat**: A segment of the screenplay/script that requires visual assets
- **Asset**: A video file (from YouTube or stock footage) associated with a beat
- **Asset_Orchestrator**: Backend component responsible for coordinating asset fetching from multiple sources
- **Session_State**: Backend storage containing the current state of beats and their associated data
- **Query_Text**: The search phrase used to find relevant assets (youtube_phrase or stock_keyword)
- **Asset_Candidate**: A potential asset found during search that can be downloaded
- **Frontend**: React-based user interface (TypeScript)
- **Backend**: Python Flask API server

## Requirements

### Requirement 1: Correct Query Text Usage

**User Story:** As a user, when I edit a beat's search terms and click "Fetch Asset", I want the system to use my edited search terms, not old or incorrect terms, so that I get relevant assets.

#### Acceptance Criteria

1. WHEN a user modifies a beat's youtube_phrase or stock_keyword field, THE Frontend SHALL persist these changes to the Backend before any fetch operation
2. WHEN the fetch endpoint receives a request, THE Backend SHALL read the most recent beat data from Session_State
3. WHEN constructing search queries, THE Asset_Orchestrator SHALL use the query text from the current beat data
4. WHEN logging search operations, THE System SHALL log the actual query text being used for traceability
5. THE System SHALL maintain consistent field naming between Frontend (youtube_phrase) and Backend (youtube_search_phrase) through proper mapping

### Requirement 2: Asset Search Preview

**User Story:** As a user, when I click "Fetch Asset", I want to see a preview of search results with thumbnails before downloading, so I can choose the best asset for my beat.

#### Acceptance Criteria

1. WHEN a user initiates an asset search, THE Backend SHALL return metadata for asset candidates without downloading files
2. THE Asset_Candidate metadata SHALL include title, thumbnail URL, duration, source provider, and unique identifier
3. WHEN search results are available, THE Frontend SHALL display them in a modal dialog with thumbnail previews
4. WHEN displaying search results, THE Frontend SHALL show at least title, thumbnail image, duration, and source for each candidate
5. WHEN a user selects an asset candidate, THE System SHALL initiate download for only the selected asset

### Requirement 3: Download Progress Feedback

**User Story:** As a user, when an asset is being downloaded, I want to see progress feedback and know what's happening, so I'm not left wondering if the system is working.

#### Acceptance Criteria

1. WHEN an asset download begins, THE Frontend SHALL display a loading indicator with status text
2. WHEN download progress updates are available, THE Frontend SHALL reflect the current download state
3. WHEN a download completes successfully, THE Frontend SHALL display the downloaded asset and dismiss the loading indicator
4. IF a download fails, THEN THE System SHALL display a descriptive error message to the user
5. WHEN multiple assets are being processed, THE Frontend SHALL show progress for each asset independently

### Requirement 4: Asset Selection and Management

**User Story:** As a user, when multiple asset candidates are available, I want to easily preview and switch between them, so I can pick the best one for my video.

#### Acceptance Criteria

1. WHEN search results contain multiple candidates, THE Frontend SHALL allow the user to select any candidate for download
2. WHEN an asset is downloaded, THE System SHALL store it with metadata linking it to the beat and search query
3. THE Frontend SHALL display the currently selected asset for each beat
4. WHEN a user wants to change an asset, THE System SHALL allow initiating a new search without losing the current asset
5. THE System SHALL support storing the file path and metadata for downloaded assets in Session_State

### Requirement 5: Search and Fetch Separation

**User Story:** As a user, I want to search for assets with custom queries without permanently changing my beat's search terms, so I can experiment with different searches.

#### Acceptance Criteria

1. THE Backend SHALL provide separate endpoints for searching assets and downloading assets
2. WHEN a user performs a search, THE System SHALL not modify the beat's stored search terms unless explicitly saved
3. THE Frontend SHALL allow users to enter custom search queries in the asset search dialog
4. WHEN a user selects and downloads an asset, THE System SHALL optionally update the beat's search terms based on user choice
5. THE System SHALL maintain the distinction between exploratory searches and committed asset selections

### Requirement 6: Field Name Consistency

**User Story:** As a system architect, I want consistent field naming between Frontend and Backend, so that data flows correctly without mapping errors.

#### Acceptance Criteria

1. THE Backend SHALL accept both youtube_phrase and youtube_search_phrase field names for backward compatibility
2. THE Frontend SHALL use consistent field names (youtube_phrase, stock_keyword) when communicating with the Backend
3. WHEN the Backend reads beat data, THE System SHALL correctly map frontend field names to backend Beat class properties
4. THE System SHALL log warnings when field name mismatches are detected during data mapping
5. THE Backend SHALL normalize field names when storing beat data to Session_State

### Requirement 7: Error Handling and Logging

**User Story:** As a developer, I want comprehensive error handling and logging throughout the asset fetching pipeline, so that I can diagnose issues quickly.

#### Acceptance Criteria

1. WHEN any step in the asset fetching pipeline fails, THE System SHALL log the error with context (beat_id, query_text, source)
2. IF a search returns no results, THEN THE System SHALL return an empty candidate list and log the query that produced no results
3. IF a download fails, THEN THE System SHALL return a descriptive error message indicating the failure reason
4. THE System SHALL log the complete flow of query text from Frontend through Backend to Asset_Orchestrator
5. WHEN field name mapping occurs, THE System SHALL log the mapping for debugging purposes

### Requirement 8: API Response Format

**User Story:** As a frontend developer, I want consistent and well-structured API responses, so that I can reliably display asset information to users.

#### Acceptance Criteria

1. THE search endpoint SHALL return a JSON array of asset candidates with consistent structure
2. EACH asset candidate SHALL include fields: id, title, thumbnail_url, duration, source, and query_used
3. THE download endpoint SHALL return the file path and metadata for the downloaded asset
4. IF an error occurs, THEN THE API SHALL return a JSON error response with status code and descriptive message
5. THE API responses SHALL use consistent field naming conventions (snake_case for JSON)
