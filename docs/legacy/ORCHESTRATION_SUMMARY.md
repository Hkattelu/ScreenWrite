# Multi-Agent Orchestration: screenwrite Development

## ðŸŽ¯ Mission
Build a production-ready CLI tool (`screenwrite`) that converts markdown video scripts into DaVinci Resolve-compatible FCPXML timelines with auto-fetched B-roll, using a coordinated multi-agent team.

---

## ðŸ‘¥ Team Structure

### Leadership
| Role | Responsibilities | Key Decisions |
|------|------------------|---------------|
| **CPO** (Chief Product Officer) | Extract requirements, define success criteria, manage scope | Feature prioritization, deadline management |
| **CTO** (Chief Technology Officer) | Technical strategy, architecture, tech stack decisions | Stack choice (Python 3.12), integration strategy |
| **Architect** | Detailed system design, module interfaces, scalability plan | Module structure, API contracts, design patterns |

### Development Team
| Role | Module(s) | Dependencies |
|------|-----------|--------------|
| **Programmer 1** (Parser) | `core/beat.py`, `parsing/script_parser.py` | None (foundation) |
| **Programmer 2** (Fetchers) | `fetchers/youtube_client.py`, `fetchers/pexels_client.py` | core/beat.py |
| **Programmer 3** (XML Gen) | `generators/xml_generator.py` | core/beat.py |
| **Programmer 4** (Orchestrator) | `orchestrator.py`, `cli.py`, `resolve_integration.py` | All above modules |

### Quality & Delivery
| Role | Responsibilities |
|------|------------------|
| **Code Reviewer** | Review each module for correctness, edge cases, security, consistency |
| **Test Engineer** | Unit tests, integration tests, end-to-end validation, coverage tracking |
| **Tech Writer** | Usage guide, API docs, architecture guide, troubleshooting, examples |

---

## ðŸ“‹ Detailed Responsibilities

### CPO - Chief Product Officer
**Phase 1: Planning**
- [ ] Parse ralph-prompt.md thoroughly
- [ ] Create PRD (Product Requirements Document)
- [ ] Define success criteria and KPIs
- [ ] Identify stakeholders and communication needs
- [ ] Create feature prioritization matrix
- [ ] Set timeline and milestones

**Outputs**: PRD.md, Success_Criteria.md, Feature_List.md

---

### CTO - Chief Technology Officer
**Phase 1: Planning**
- [ ] Evaluate tech stack alternatives
- [ ] Make decision: Python 3.12 + modular agents
- [ ] Decide on FCPXML strategy (v1.8, spine gaps + connected clips)
- [ ] Identify dependencies: yt-dlp, requests, xml.etree, ffmpeg
- [ ] Plan API integrations (Pexels free tier, YouTube search)
- [ ] Define error handling and fallback strategies
- [ ] Plan monitoring/logging approach

**Decisions Made**:
âœ… **Language**: Python 3.12 (mature, rich ecosystem)  
âœ… **XML Library**: xml.etree.ElementTree (stdlib, simple)  
âœ… **YouTube**: yt-dlp (free, reliable, no API key)  
âœ… **Stock ScreenWrite**: Pexels API (free tier available)  
âœ… **Timeline Format**: FCPXML 1.8 (Resolve native, FCP compatible)  

**Outputs**: TechStack.md, API_Design.md, ArchitectureDecisions.md

---

### Architect - System Design
**Phase 1: Planning**
- [ ] Create system architecture diagram
- [ ] Define module interfaces/contracts
- [ ] Design data flow pipeline
- [ ] Plan scalability and extensibility
- [ ] Identify potential bottlenecks
- [ ] Design error handling strategy
- [ ] Create ER diagram for data models
- [ ] Plan folder structure

**Architecture Overview**:
```
screenwrite/
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ beat.py              (Beat dataclass)
â”œâ”€â”€ parsing/
â”‚   â”œâ”€â”€ script_parser.py     (Markdown â†’ beats)
â”œâ”€â”€ fetchers/
â”‚   â”œâ”€â”€ youtube_client.py    (yt-dlp wrapper)
â”‚   â”œâ”€â”€ pexels_client.py     (API client)
â”œâ”€â”€ generators/
â”‚   â”œâ”€â”€ xml_generator.py     (FCPXML builder)
â”œâ”€â”€ orchestrator.py          (Main coordinator)
â”œâ”€â”€ cli.py                   (CLI interface)
â””â”€â”€ resolve_integration.py   (Resolve fusionscript wrapper)
```

**Outputs**: ArchitectureDiagram.md, ModuleContracts.md, DataFlow.md

---

### Programmer 1 - Script Parser Agent
**Module**: `core/` + `parsing/`

**Tasks**:
- [ ] Implement Beat dataclass
  - Fields: id, text, duration, stock_keyword, youtube_search_phrase, paths
  - Auto-calculate duration from word count (2.5 wps heuristic)
  - Post-init validation
  
- [ ] Implement ScriptParser class
  - Parse markdown files into beats
  - Identify section headers (# and ##)
  - Chunk text into 5-10 second segments
  - Generate stock footage keywords (heuristic or NLP)
  - Generate YouTube search phrases

**Deliverables**:
- [ ] `core/beat.py` - Complete with docstrings
- [ ] `parsing/script_parser.py` - Complete with examples
- [ ] Unit tests (beat_test.py, parser_test.py)
- [ ] Example markdown script for testing

**Success Criteria**:
- Beat duration auto-calculates within Â±2 seconds of target
- Parses sample markdown into 5-10 second beats
- Generated queries are contextually relevant
- 90%+ test coverage

---

### Programmer 2 - Asset Fetcher Agent
**Module**: `fetchers/`

**Tasks**:
- [ ] Implement YouTubeClient
  - Search YouTube using yt-dlp
  - Download first result
  - Trim to beat duration using ffmpeg
  - Error handling for network/missing ffmpeg
  
- [ ] Implement PexelsClient
  - Search Pexels API (requires free API key)
  - Download matching video
  - Handle rate limiting
  - Fallback when quota exhausted

- [ ] Implement fallback logic
  - Try YouTube first
  - Fallback to Pexels
  - Handle both API key missing scenarios gracefully

**Deliverables**:
- [ ] `fetchers/youtube_client.py` - Complete with docstrings
- [ ] `fetchers/pexels_client.py` - Complete with docstrings
- [ ] Unit tests with mocked APIs
- [ ] Integration tests with real APIs (optional, gated)

**Success Criteria**:
- YouTube downloads work with yt-dlp
- Pexels API integration works
- Fallback logic tested and working
- Network errors handled gracefully
- 80%+ test coverage (with mocks)

---

### Programmer 3 - XML Generator Agent
**Module**: `generators/`

**Tasks**:
- [ ] Implement FCPXMLGenerator class
  - Initialize FCPXML 1.8 root element
  - Create format specification (1920x1080, 30fps)
  - Manage resource registration (videos)
  - Build timeline sequence with gaps + connected clips

- [ ] Implement gap insertion for voiceover placeholders
  - Primary spine contains gaps matching beat duration
  - Easy for editors to replace with actual voiceover

- [ ] Implement B-roll clip attachment
  - Connected clips on Lane 1
  - Trim to beat duration
  - Proper time offset calculation
  - Resource reference handling

- [ ] Implement XML output
  - Pretty-print FCPXML
  - Validate structure
  - Write to file with proper encoding

**Deliverables**:
- [ ] `generators/xml_generator.py` - Complete with docstrings
- [ ] Unit tests for each XML building component
- [ ] Integration test with real Resolve validation
- [ ] Example FCPXML output

**Success Criteria**:
- Generated FCPXML imports into DaVinci Resolve without errors
- Gaps appear on spine, B-roll on Lane 1
- All timestamps correct
- 85%+ test coverage

---

### Programmer 4 - Orchestrator & CLI Agent
**Module**: `orchestrator.py`, `cli.py`, `resolve_integration.py`

**Tasks**:
- [ ] Implement VideoOrchestrator
  - Coordinate Parsers, Fetchers, Generators
  - Manage dependency flow
  - Handle errors and logging

- [ ] Implement command-line interface
  - Arguments: script path, output path, API keys, options
  - Help text and usage examples
  - Error messages for missing required files

- [ ] Implement Resolve integration
  - Optional: Direct import into running Resolve instance
  - Create bins for assets
  - Import media files
  - Import FCPXML timeline

- [ ] End-to-end workflow
  - Parse script
  - Fetch assets (optional)
  - Generate timeline
  - Save to file
  - Optional: Import to Resolve

**Deliverables**:
- [ ] `orchestrator.py` - Main coordinator
- [ ] `cli.py` - Command-line interface
- [ ] `resolve_integration.py` - Resolve wrapper
- [ ] End-to-end integration tests
- [ ] Example usage scripts

**Success Criteria**:
- CLI accepts markdown script
- End-to-end workflow completes
- Generated FCPXML valid and importable
- All optional features work
- Error handling for edge cases

---

### Code Reviewer
**Phase 3: Integration & Code Review**

**Review Checklist**:
- [ ] Code follows style guide (PEP 8)
- [ ] All functions have docstrings
- [ ] Error handling is comprehensive
- [ ] No security issues (SQL injection, etc.)
- [ ] API usage is correct
- [ ] Resource cleanup (file handles, network)
- [ ] Type hints on all functions
- [ ] No hardcoded paths or credentials
- [ ] Logging is appropriate
- [ ] Comments explain "why", not "what"

**Per-Module Reviews**:
- [ ] Parser: edge cases for markdown
- [ ] Fetchers: network error handling, timeouts
- [ ] XML Gen: FCPXML schema compliance
- [ ] Orchestrator: dependency management
- [ ] CLI: argument validation, help text

**Deliverables**:
- [ ] Code review report for each module
- [ ] List of issues to fix
- [ ] Approval checklist

---

### Test Engineer
**Phase 4: Quality Assurance**

**Testing Strategy**:
- [ ] Unit tests for each module (80%+ coverage)
- [ ] Integration tests for module boundaries
- [ ] End-to-end test with sample script
- [ ] Negative testing (error cases)
- [ ] Performance testing (large scripts)

**Test Plan**:
```
Unit Tests:
  - beat.py: duration calculation, edge cases
  - script_parser.py: parsing logic, edge cases
  - youtube_client.py: yt-dlp wrapper (mocked)
  - pexels_client.py: API client (mocked)
  - xml_generator.py: XML structure, timing
  - orchestrator.py: coordinator logic
  - cli.py: argument parsing

Integration Tests:
  - Parser â†’ Fetchers: beat to asset flow
  - Fetchers â†’ XML Gen: assets to XML
  - Orchestrator â†’ CLI: end-to-end flow

E2E Tests:
  - Sample markdown script â†’ FCPXML â†’ Resolve import
  - Large script (30+ beats)
  - Script with special characters
  - Script with no API keys available
```

**Test Coverage Goals**:
- `core/`: 90%+
- `parsing/`: 90%+
- `fetchers/`: 80%+ (with mocks)
- `generators/`: 85%+
- `orchestrator.py`: 80%+
- `cli.py`: 75%+

**Deliverables**:
- [ ] Test suite (pytest)
- [ ] Coverage report
- [ ] Test documentation
- [ ] Known limitations document

---

### Tech Writer
**Phase 5: Documentation**

**Documentation to Create**:
- [ ] **README.md**
  - What is screenwrite
  - Installation instructions
  - Quick start example
  - Features overview

- [ ] **USAGE_GUIDE.md**
  - Detailed CLI reference
  - Examples for common use cases
  - API key setup (Pexels)
  - Troubleshooting

- [ ] **API.md**
  - Beat dataclass reference
  - ScriptParser API
  - AssetFetcher interfaces
  - XMLGenerator API
  - Orchestrator API

- [ ] **ARCHITECTURE.md**
  - System overview
  - Module descriptions
  - Data flow diagram
  - Design decisions

- [ ] **Examples/**
  - sample_script.md (demo markdown)
  - tutorial_video.md (step-by-step)
  - feature_showcase.md (all features)

- [ ] **TROUBLESHOOTING.md**
  - Common errors
  - FFmpeg not found
  - yt-dlp issues
  - Pexels API limits
  - Resolve compatibility

**Deliverables**:
- [ ] 5+ markdown documentation files
- [ ] 3+ example scripts
- [ ] Screenshots/diagrams
- [ ] Video tutorial (optional)

---

## ðŸ“… Timeline & Milestones

### Week 1: Planning & Design
| Day | Phase | Owners | Deliverables |
|-----|-------|--------|--------------|
| 1-2 | Requirements | CPO | PRD, Feature List, Success Criteria |
| 2-3 | Architecture | CTO, Architect | Tech Stack Decision, Architecture Diagram |
| 3-5 | Design Review | All Leads | Approved designs, module contracts |

### Week 2: Core Development
| Day | Task | Owner | Status |
|-----|------|-------|--------|
| 1-2 | Parser implementation | P1 | Code complete + unit tests |
| 1-2 | Fetcher implementation | P2 | Code complete + unit tests |
| 2-3 | XML Gen implementation | P3 | Code complete + unit tests |
| 3-5 | Orchestrator + CLI | P4 | Code complete + integration tests |

### Week 3: Integration & QA
| Day | Phase | Owners | Status |
|-----|-------|--------|--------|
| 1-2 | Code Review | Reviewer | All modules reviewed, issues documented |
| 2-3 | Bug fixes | P1-P4 | Critical issues fixed, retested |
| 3-4 | Test Suite | Test Eng | 80%+ coverage, all tests passing |
| 4-5 | Docs | Tech Writer | README, API docs, troubleshooting |

### Week 4: Release Prep
| Day | Task | Status |
|-----|------|--------|
| 1-2 | Final QA | All tests passing, coverage â‰¥85% |
| 2-3 | Documentation review | Docs complete and accurate |
| 3-5 | Release packaging | Ready for production |

---

## ðŸŽ¯ Success Criteria (Acceptance)

âœ… **Functional Requirements**
- [ ] Parses markdown scripts into beats
- [ ] Auto-calculates beat duration
- [ ] Generates contextual search queries
- [ ] Downloads B-roll from YouTube (yt-dlp)
- [ ] Downloads B-roll from Pexels (API fallback)
- [ ] Generates valid FCPXML 1.8
- [ ] FCPXML imports into DaVinci Resolve
- [ ] CLI interface works as documented
- [ ] Optional Resolve integration works

âœ… **Quality Requirements**
- [ ] 80%+ test coverage
- [ ] 0 critical bugs
- [ ] Code reviewed and approved
- [ ] All edge cases handled
- [ ] Network errors handled gracefully

âœ… **Documentation Requirements**
- [ ] README with quick start
- [ ] Complete API documentation
- [ ] Usage guide with examples
- [ ] Architecture documentation
- [ ] Troubleshooting guide

âœ… **Process Requirements**
- [ ] Daily standups completed
- [ ] Weekly milestone reviews
- [ ] All decisions documented
- [ ] Change log maintained

---

## ðŸš§ Workflow Commands

### Daily Standup Template
```
[Agent Name]
TODAY COMPLETED:
- âœ… Task 1
- âœ… Task 2

TODAY IN_PROGRESS:
- ðŸ”„ Task 3 (70% done)

BLOCKERS:
- ðŸš« Blocked on X from [Agent]

NEXT 24H:
- Task 4
- Task 5
```

### Code Review Process
```
[Code Reviewer] â†’ [Target Agent]
MODULE: [name]
ISSUES FOUND:
1. [Issue] - Severity: [Critical|High|Medium|Low]
   Suggestion: [Fix]
2. ...
APPROVAL: [Approved|Changes Required]
```

### Status Check Format
```json
{
  "project": "screenwrite",
  "phase": "Development",
  "completion": "45%",
  "blockers": [],
  "next_milestone": "Module completion"
}
```

---

## ðŸ“ž Communication Channels

- **Async**: GitHub Issues (blockers, decisions)
- **Sync**: Daily 15-min standup
- **Escalation**: CTO for technical, CPO for scope
- **Log**: team_log.json tracks all messages
- **Decisions**: Recorded in DECISIONS.md

---

## ðŸŽ“ Knowledge Transfer

### Handoff Documents
1. **Architecture.md** - System overview for all
2. **API.md** - Interface contracts for all
3. **DECISIONS.md** - Why we chose X over Y
4. **TROUBLESHOOTING.md** - Known issues and fixes

### Code Handoff
- [ ] All code has docstrings
- [ ] All functions have examples
- [ ] README in each module
- [ ] Tests serve as usage examples

---

## ðŸš€ Launch Checklist

Before release:
- [ ] All tests passing (80%+ coverage)
- [ ] Code review approved
- [ ] Documentation complete
- [ ] Example scripts working
- [ ] Resolve import tested
- [ ] Error messages clear
- [ ] Installation instructions verified
- [ ] Changelog updated
- [ ] Version bumped (0.1.0)

---

**Status**: Ready for team assignment  
**Next Action**: Assign human agents to each role and begin Phase 1  
**Estimated Completion**: 4 weeks from kickoff


