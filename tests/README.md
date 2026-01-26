# End-to-End Integration Tests

This directory contains comprehensive end-to-end integration tests for the screenwrite system.

## Overview

The end-to-end integration test validates the complete workflow from markdown script input to FCPXML timeline output, ensuring all components work together correctly.

## Test Coverage

### Requirements Validated

The tests validate the following requirements from the specification:

- **Requirement 1.1**: Script parsing into beats with 5-10 second duration
- **Requirement 1.2**: Stock keyword generation from beat text  
- **Requirement 1.3**: YouTube search phrase generation from beat text
- **Requirement 1.4**: Beat dataclass creation with all required fields
- **Requirement 1.5**: Auto-duration calculation using word count heuristic
- **Requirement 2.1**: Asset fetching workflow invocation
- **Requirement 3.1**: Valid FCPXML 1.8 document generation
- **Requirement 3.2**: Spine track with gaps for each beat
- **Requirement 3.3**: Connected clips alignment on Lane 1
- **Requirement 3.4**: Valid resource references in FCPXML
- **Requirement 3.5**: FCPXML file output creation
- **Requirement 4.1**: CLI interface functionality

### Test Cases

1. **Complete Workflow with Mocked Fetchers**
   - Tests the full pipeline: parse â†’ fetch â†’ generate â†’ validate
   - Uses mocked external APIs for reliable testing
   - Validates beat generation, asset fetching, and FCPXML creation
   - Verifies all query fields are properly generated and non-empty

2. **FCPXML Output Validation**
   - Validates generated FCPXML structure and content
   - Checks XML validity and FCPXML 1.8 compliance
   - Verifies spine gaps, connected clips, and resource references
   - Ensures proper timing and alignment

3. **Workflow with No Assets**
   - Tests timeline generation when asset fetching is skipped
   - Validates gaps-only timeline creation
   - Ensures system works without B-roll footage

4. **CLI Interface Integration**
   - Tests command-line argument parsing
   - Validates CLI workflow execution
   - Ensures proper integration between CLI and orchestrator

5. **Error Handling Integration**
   - Tests graceful handling of invalid inputs
   - Validates error recovery and continuation
   - Ensures system resilience to failures

## Test Structure

### Files

- `test_end_to_end_integration.py` - Main test suite
- `fixtures/sample_script.md` - Sample markdown script for testing
- `__init__.py` - Package initialization

### Mock Strategy

The tests use comprehensive mocking to avoid external dependencies:

- **Asset Orchestrator**: Mocked to return predefined asset paths
- **External APIs**: YouTube and Pexels APIs are mocked
- **File System**: Temporary directories for test isolation

### Test Data

- **Sample Script**: Realistic markdown video script about Python programming
- **Mock Assets**: Simulated video file paths for testing
- **Expected Outputs**: Validated FCPXML structure and content

## Running Tests

### Using unittest

```bash
# Run all tests
python -m unittest tests.test_end_to_end_integration -v

# Run specific test
python -m unittest tests.test_end_to_end_integration.TestEndToEndIntegration.test_complete_workflow_with_mocked_fetchers -v
```

### Using test runner

```bash
python run_tests.py
```

## Test Validation

The tests validate:

1. **Functional Correctness**
   - All workflow steps execute successfully
   - Beat generation follows specification rules
   - FCPXML output is valid and well-formed

2. **Integration Points**
   - Components communicate correctly
   - Data flows properly between stages
   - Error handling works across boundaries

3. **Output Quality**
   - Generated beats have valid durations (5-10 seconds)
   - Search queries are non-empty and meaningful
   - FCPXML structure matches specification

4. **Resilience**
   - System handles missing dependencies gracefully
   - Workflow continues despite individual failures
   - Clear error messages for invalid inputs

## Dependencies

The tests require:

- Python 3.7+
- unittest (built-in)
- unittest.mock (built-in)
- xml.etree.ElementTree (built-in)
- tempfile (built-in)
- pathlib (built-in)

No external testing frameworks are required, making the tests easy to run in any Python environment.

## Maintenance

When adding new features:

1. Add corresponding test cases to validate the feature
2. Update mock configurations if new external dependencies are added
3. Ensure test isolation by using temporary directories
4. Validate both success and failure scenarios
5. Update this documentation with new test coverage
