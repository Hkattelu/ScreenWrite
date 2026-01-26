# AGENTS.md - Multi-Agent Development Guide

This document defines the agent roles, responsibilities, communication protocols, and commands for the vid-orchestrator project.

## Overview

The vid-orchestrator project uses a **multi-agent orchestration model** where specialized agents collaborate to build a Python CLI tool that converts markdown video scripts into DaVinci Resolve-compatible timelines with auto-fetched B-roll footage.

---

## Agent Roles

### 1. **CPO (Chief Product Officer)** - Vision & Requirements
**Owns**: Product vision, requirements, scope, success criteria

**Responsibilities**:
- Parse and clarify the ralph-prompt specification
- Define success criteria and acceptance tests
- Create PRD (Product Requirements Document)
- Manage feature prioritization and scope creep
- Define KPIs and metrics

**Command**: `[CPO]` or `@CPO`

**Outputs**:
- `PRD.md` - Product Requirements Document
- `SUCCESS_CRITERIA.md` - Acceptance criteria
- `FEATURE_LIST.md` - Prioritized features

---

### 2. **CTO (Chief Technology Officer)** - Architecture & Tech Stack
**Owns**: Technical strategy, architecture decisions, tech stack, APIs

**Responsibilities**:
- Evaluate and choose tech stack (Python 3.12, libraries, APIs)
- Design system architecture and data flow
- Define API contracts and interfaces
- Plan integration strategy (yt-dlp, Pexels, FCPXML)
- Make technical trade-off decisions
- Identify and mitigate technical risks

**Command**: `[CTO]` or `@CTO`

**Key Decisions**:
- ✅ **Language**: Python 3.12 (mature, rich ecosystem)
- ✅ **YouTube**: yt-dlp (free, reliable, no API key)
- ✅ **Stock Footage**: Pexels API (free tier available)
- ✅ **Timeline Format**: FCPXML 1.8 (Resolve native)
- ✅ **XML Library**: xml.etree.ElementTree (stdlib)
- ✅ **Video Processing**: ffmpeg (mandatory for trimming)

**Outputs**:
- `TECH_STACK.md` - Technology choices and rationale
- `ARCHITECTURE.md` - System architecture diagram
- `API_CONTRACTS.md` - Interface specifications

---

### 3. **Architect** - Detailed System Design
**Owns**: Module structure, interfaces, design patterns, scalability

**Responsibilities**:
- Design module structure and folder hierarchy
- Define data models (Beat dataclass)
- Create ER diagrams and workflow charts
- Design error handling and fallback strategies
- Plan extensibility and scalability
- Document design decisions

**Command**: `[Architect]` or `@Architect`

**Module Structure**:
```
vid_orchestrator/
├── core/
│   ├── beat.py                      # Beat dataclass
├── parsing/
│   ├── script_parser.py             # Markdown → beats
├── fetchers/
│   ├── base_fetcher.py              # Base class
│   ├── youtube_client.py            # yt-dlp wrapper
│   ├── pexels_client.py             # Pexels API client
│   ├── asset_orchestrator.py        # Fetcher coordinator
├── generators/
│   ├── xml_generator.py             # FCPXML builder
├── utils/
│   ├── error_handling.py            # Error utilities
├── orchestrator.py                  # Main coordinator
├── cli.py                           # CLI interface
├── resolve_integration.py           # Resolve integration
└── __main__.py                      # Entry point
```

**Outputs**:
- `ARCHITECTURE_DIAGRAM.md` - Visual system design
- `MODULE_CONTRACTS.md` - Interface specifications
- `DATA_FLOW.md` - Data flow diagram

---

### 4. **Programmer 1** - Script Parser & Beat Generation
**Owns**: `core/beat.py`, `parsing/script_parser.py`

**Responsibilities**:
- Implement Beat dataclass with auto-duration calculation
- Implement ScriptParser (markdown → beats)
- Extract headers for context
- Chunk text into 5-10 second segments
- Generate stock footage keywords
- Generate YouTube search phrases
- Validate beats (duration, content, queries)

**Command**: `[P1]`, `@Programmer1`, or `@P1`

**Deliverables**:
- `core/beat.py` - Complete Beat dataclass
- `parsing/script_parser.py` - ScriptParser class
- `tests/test_beat.py` - Unit tests
- `tests/test_script_parser.py` - Parser tests

**Success Criteria**:
- ✓ Beat duration auto-calculates within ±2 seconds
- ✓ Parses sample markdown into 5-10 second beats
- ✓ Generated queries are contextually relevant
- ✓ 90%+ test coverage
- ✓ Handles edge cases (empty scripts, special chars)

---

### 5. **Programmer 2** - Asset Fetchers
**Owns**: `fetchers/youtube_client.py`, `fetchers/pexels_client.py`, `fetchers/asset_orchestrator.py`

**Responsibilities**:
- Implement YouTubeClient (yt-dlp wrapper)
- Implement PexelsClient (Pexels API client)
- Handle video downloading and trimming (ffmpeg)
- Implement fallback logic (YouTube → Pexels)
- Handle rate limiting and API errors
- Implement retry logic and graceful degradation
- Manage temporary files and caching

**Command**: `[P2]`, `@Programmer2`, or `@P2`

**Deliverables**:
- `fetchers/base_fetcher.py` - Base class
- `fetchers/youtube_client.py` - YouTube integration
- `fetchers/pexels_client.py` - Pexels integration
- `fetchers/asset_orchestrator.py` - Fallback coordinator
- `tests/test_youtube_client.py` - YouTube tests (mocked)
- `tests/test_pexels_client.py` - Pexels tests (mocked)

**Success Criteria**:
- ✓ YouTube downloads work with yt-dlp
- ✓ Pexels API integration functional
- ✓ Fallback logic tested and working
- ✓ Network errors handled gracefully
- ✓ 80%+ test coverage (with mocks)
- ✓ Timeout handling (60s default)

**Dependencies**:
- Requires `core/beat.py` from P1

---

### 6. **Programmer 3** - XML Timeline Generator
**Owns**: `generators/xml_generator.py`

**Responsibilities**:
- Implement FCPXMLGenerator class
- Build FCPXML 1.8 document structure
- Create format specification (1920x1080, 30fps)
- Manage media resource registration
- Generate spine track with gaps (voiceover placeholders)
- Add connected clips lane for B-roll
- Handle timing and offset calculations
- Validate XML output
- Write to file with proper encoding

**Command**: `[P3]`, `@Programmer3`, or `@P3`

**Deliverables**:
- `generators/xml_generator.py` - FCPXMLGenerator class
- `tests/test_xml_generator.py` - XML generation tests
- `examples/sample_timeline.fcpxml` - Example output
- `docs/FCPXML_STRUCTURE.md` - XML documentation

**Success Criteria**:
- ✓ Generated FCPXML imports into DaVinci Resolve
- ✓ Gaps appear on spine, B-roll on Lane 1
- ✓ All timestamps calculated correctly
- ✓ Handles resources properly
- ✓ 85%+ test coverage
- ✓ Validates against FCPXML schema

**Dependencies**:
- Requires `core/beat.py` from P1

---

### 7. **Programmer 4** - Orchestrator & CLI
**Owns**: `orchestrator.py`, `cli.py`, `resolve_integration.py`

**Responsibilities**:
- Implement VideoOrchestrator (main coordinator)
- Coordinate Parser, Fetchers, and Generator
- Manage dependency flow and error propagation
- Implement CLI interface (argparse)
- Parse arguments and validate inputs
- Implement optional DaVinci Resolve integration
- Create end-to-end workflow
- Handle logging and verbose output
- Implement graceful error handling

**Command**: `[P4]`, `@Programmer4`, or `@P4`

**Deliverables**:
- `orchestrator.py` - Main coordinator
- `cli.py` - CLI interface
- `resolve_integration.py` - Resolve integration
- `__main__.py` - Entry point
- `tests/test_orchestrator.py` - Integration tests
- `tests/test_cli.py` - CLI tests

**Success Criteria**:
- ✓ CLI accepts all documented arguments
- ✓ End-to-end workflow completes successfully
- ✓ FCPXML generated and valid
- ✓ Resolve integration optional but functional
- ✓ Error handling for all edge cases
- ✓ Verbose logging works
- ✓ 80%+ test coverage

**Dependencies**:
- Requires all modules from P1, P2, P3

---

### 8. **Code Reviewer** - Quality & Correctness
**Owns**: Code quality, consistency, security, correctness

**Responsibilities**:
- Review each programmer's code
- Check for bugs, edge cases, security issues
- Ensure consistency with architecture
- Validate API usage and error handling
- Review documentation quality
- Suggest optimizations
- Ensure test coverage targets met
- Create code review reports

**Command**: `[Reviewer]`, `@CodeReviewer`, or `@Reviewer`

**Review Checklist**:
- [ ] Code follows project style guide
- [ ] All functions have docstrings
- [ ] Error handling is comprehensive
- [ ] Edge cases are handled
- [ ] No security vulnerabilities
- [ ] Test coverage ≥ target %
- [ ] Code is maintainable
- [ ] No dead code
- [ ] Consistent with architecture
- [ ] API contracts respected

**Outputs**:
- `REVIEW_REPORT.md` - Code review findings
- `CODE_STYLE_GUIDE.md` - Style guidelines

---

### 9. **Test Engineer** - Quality Verification
**Owns**: Testing, validation, quality assurance

**Responsibilities**:
- Create unit tests for each module
- Build integration tests
- Test with sample markdown scripts
- Validate FCPXML output
- Test with real DaVinci Resolve
- Create test fixtures and mock data
- Track test coverage
- Document known limitations
- Perform regression testing

**Command**: `[TestEng]`, `@TestEngineer`, or `@QA`

**Test Suites**:
```
tests/
├── unit/
│   ├── test_beat.py
│   ├── test_script_parser.py
│   ├── test_youtube_client.py
│   ├── test_pexels_client.py
│   ├── test_xml_generator.py
│   └── test_cli.py
├── integration/
│   ├── test_parser_to_fetchers.py
│   ├── test_fetchers_to_xml.py
│   └── test_end_to_end.py
└── fixtures/
    ├── sample_script.md
    ├── mocked_responses.json
    └── expected_output.fcpxml
```

**Coverage Targets**:
- `core/`: 90%+
- `parsing/`: 90%+
- `fetchers/`: 80%+ (with mocks)
- `generators/`: 85%+
- `orchestrator.py`: 80%+
- `cli.py`: 75%+
- **Overall**: 80%+

**Commands**:
```bash
# Run all tests
python -m pytest tests/ -v --cov=vid_orchestrator --cov-report=html

# Run specific test suite
python -m pytest tests/unit/test_beat.py -v

# Run with coverage report
python run_tests.py
```

**Outputs**:
- `TEST_REPORT.md` - Test results and coverage
- `KNOWN_ISSUES.md` - Known limitations and issues
- Coverage reports (HTML)

---

### 10. **Tech Writer** - Documentation
**Owns**: User docs, API docs, examples, guides

**Responsibilities**:
- Write user guide and quick start
- Create complete CLI reference
- Document API and module interfaces
- Write architecture guide
- Create troubleshooting guide
- Provide example scripts
- Document configuration options
- Create setup and installation guides
- Maintain changelog

**Command**: `[Writer]`, `@TechWriter`, or `@Docs`

**Documentation Deliverables**:
- `README.md` - Main overview and quick start
- `docs/INSTALLATION.md` - Installation guide
- `docs/USAGE_GUIDE.md` - Detailed CLI reference
- `docs/API.md` - API documentation
- `docs/ARCHITECTURE.md` - Architecture guide
- `docs/TROUBLESHOOTING.md` - Troubleshooting guide
- `docs/SCRIPT_FORMAT.md` - Markdown format spec
- `examples/sample_script.md` - Example script
- `examples/tutorial_video.md` - Tutorial example
- `CHANGELOG.md` - Version history

**Outputs**:
- Markdown documentation (5+ files)
- Example scripts (3+ files)
- Screenshots/diagrams
- API reference

---

## Communication Protocols

### Daily Standup Format

Use this format for daily progress reports:

```
[Agent Name]

TODAY COMPLETED:
- ✅ Task 1
- ✅ Task 2

TODAY IN_PROGRESS:
- 🔄 Task 3 (70% done)

BLOCKERS:
- 🚫 Waiting on [Agent] for [deliverable]

NEXT 24H:
- Task 4
- Task 5
```

### Code Review Format

Use this format for code reviews:

```
[Code Reviewer] → [Target Programmer]

MODULE: [name]

REVIEW FINDINGS:
✓ Strengths:
- [positive aspect]

⚠️  Issues Found:
1. [Issue] - Severity: [Critical|High|Medium|Low]
   Location: [file:line]
   Suggestion: [fix recommendation]

APPROVAL: [Approved | Changes Required | Request Changes]
```

### Decision Making

**Format**:
```
[Agent] DECISION: [Decision]
RATIONALE: [Why this choice]
IMPACT: [What changes]
ALTERNATIVES CONSIDERED: [Other options]
```

**Escalation Path**:
1. **Architecture**: → CTO
2. **Technical Trade-off**: → Architect
3. **Scope/Features**: → CPO
4. **Quality/Testing**: → Code Reviewer + Test Engineer
5. **Deadlock**: → CPO (executive decision)

### Status Reporting

**Weekly Status Check**:
```json
{
  "week": "Week N",
  "phase": "Phase Name",
  "completion": "X%",
  "on_track": true/false,
  "blockers": ["blocker 1", "blocker 2"],
  "next_milestone": "Milestone name",
  "risks": ["risk 1"]
}
```

---

## Project Phases

### Phase 1: Planning (Week 1)
**Owners**: CPO, CTO, Architect

**Deliverables**:
- PRD and feature list
- Architecture diagram
- Tech stack decision
- Module design
- Success criteria

**Output**: Approved design document, team kickoff

---

### Phase 2: Development (Week 1-2)
**Owners**: P1, P2, P3, P4

**Parallel Development**:
- P1: Script parser (foundation)
- P2: Asset fetchers
- P3: XML generator
- P4: Orchestrator & CLI

**Synchronization Points**:
- P1 → P2, P3 (Beat dataclass)
- P2, P3 → P4 (All modules)

**Output**: All modules complete with unit tests

---

### Phase 3: Integration (Week 2)
**Owners**: P4, Code Reviewer

**Tasks**:
- Integrate all modules
- Fix integration issues
- Code review and refactor
- End-to-end testing

**Output**: Working application, code reviews complete

---

### Phase 4: Quality Assurance (Week 2-3)
**Owners**: Code Reviewer, Test Engineer

**Tasks**:
- Full code review
- Comprehensive test suite
- Bug fixes
- Coverage verification
- Real-world testing (Resolve import)

**Output**: Tested, validated product (80%+ coverage)

---

### Phase 5: Documentation (Week 3)
**Owners**: Tech Writer

**Tasks**:
- Write user guide
- Create API docs
- Document architecture
- Create examples
- Troubleshooting guide

**Output**: Complete documentation, examples, guides

---

### Phase 6: Release (Week 4)
**Owners**: All

**Tasks**:
- Final QA
- Documentation review
- Release packaging
- Version bump

**Output**: Production-ready release

---

## Command Reference

### Common Commands

**Run tests**:
```bash
python run_tests.py
```

**Run with coverage**:
```bash
python -m pytest tests/ --cov=vid_orchestrator --cov-report=html
```

**Run CLI**:
```bash
python -m vid_orchestrator script.md --output timeline.fcpxml --verbose
```

**Lint code**:
```bash
python -m flake8 vid_orchestrator/
python -m pylint vid_orchestrator/
```

**Run linting and tests**:
```bash
python run_lint_and_tests.py
```

**Validate syntax**:
```bash
python validate_syntax.py
```

### Agent Commands (Thread Format)

- `[CPO]` - Chief Product Officer
- `[CTO]` - Chief Technology Officer
- `[Architect]` - System Architect
- `[P1]` or `@Programmer1` - Parser Agent
- `[P2]` or `@Programmer2` - Fetchers Agent
- `[P3]` or `@Programmer3` - XML Generator Agent
- `[P4]` or `@Programmer4` - Orchestrator Agent
- `[Reviewer]` - Code Reviewer
- `[TestEng]` - Test Engineer
- `[Writer]` - Tech Writer

---

## Success Criteria

✅ **Functional**
- [ ] Parses markdown scripts into 5-10 second beats
- [ ] Auto-calculates beat duration
- [ ] Generates stock keywords and YouTube phrases
- [ ] Downloads B-roll from YouTube
- [ ] Falls back to Pexels when needed
- [ ] Generates valid FCPXML 1.8
- [ ] Imports successfully into DaVinci Resolve

✅ **Quality**
- [ ] 80%+ test coverage
- [ ] 0 critical bugs
- [ ] Code reviewed and approved
- [ ] All edge cases handled
- [ ] Network errors graceful

✅ **Documentation**
- [ ] README with quick start
- [ ] Complete API docs
- [ ] Usage guide with examples
- [ ] Architecture documentation
- [ ] Troubleshooting guide
- [ ] 3+ example scripts

✅ **Process**
- [ ] Daily standups completed
- [ ] Weekly milestone reviews
- [ ] Decisions documented
- [ ] Changelog maintained

---

## File Locations

**Core Documentation**:
- `README.md` - Main overview
- `MULTI_AGENT_PLAN.md` - Original planning doc
- `ORCHESTRATION_SUMMARY.md` - Orchestration details
- `AGENTS.md` - This file

**Source Code**:
- `vid_orchestrator/` - Main package
- `tests/` - Test suite
- `docs/` - User documentation
- `examples/` - Example scripts

**Configuration**:
- `.flake8` - Linting config
- `.pylintrc` - Pylint config
- `requirements.txt` - Python dependencies

**Scripts**:
- `orchestrate_agents.py` - Agent orchestration
- `run_tests.py` - Test runner
- `run_lint_and_tests.py` - Lint + test runner
- `validate_syntax.py` - Syntax validator

---

## Resources

- **ralph-prompt.md** - Original specification
- **MULTI_AGENT_PLAN.md** - Detailed planning
- **ORCHESTRATION_SUMMARY.md** - Team structure
- **team_log.json** - Collaboration log (generated by orchestrate_agents.py)

---

## Quick Reference

| Role | Owns | Phase | Status |
|------|------|-------|--------|
| CPO | Vision, scope, success | Planning | Lead |
| CTO | Tech decisions, APIs | Planning | Lead |
| Architect | Design, modules | Planning | Lead |
| P1 | Beat parser | Dev | P0 (foundation) |
| P2 | Asset fetchers | Dev | P0 (depends on P1) |
| P3 | XML generator | Dev | P0 (depends on P1) |
| P4 | Orchestrator, CLI | Dev | P1 (depends on P1-3) |
| Reviewer | Code quality | Integration | P0 |
| TestEng | Testing, validation | QA | P0 |
| Writer | Documentation | Docs | P1 |

---

**Last Updated**: Jan 20, 2026  
**Version**: 1.0  
**Status**: Active
