# Multi-Agent Orchestration Plan: vid-orchestrator

## Executive Summary
Assemble a virtual software development team using ChatDev-style multi-agent orchestration to build the vid-orchestrator CLI tool from the ralph-prompt specification.

## Team Composition

### 1. **Chief Product Officer (CPO)** - Vision & Requirements
- **Role**: Understands the ralph-prompt requirements
- **Responsibilities**:
  - Parse and clarify the specification
  - Define success criteria
  - Create PRD and feature list
  - Identify risks and dependencies
  
### 2. **Chief Technology Officer (CTO)** - Architecture & Tech Decisions
- **Role**: Technical leadership
- **Responsibilities**:
  - Design system architecture (multi-agent, modular)
  - Choose tech stack (Python 3.12, yt-dlp, etc.)
  - Define data models (Beat dataclass)
  - Plan API integrations
  - Design FCPXML generation strategy

### 3. **Architect** - Detailed Design
- **Role**: Technical blueprint
- **Responsibilities**:
  - Design module structure (core, generators, fetchers, parsing)
  - Define interfaces between agents
  - Create ER diagrams and workflow charts
  - Plan scalability and extensibility

### 4. **Senior Programmer (Agent 1)** - Core Logic
- **Role**: Beat parsing and data flow
- **Responsibilities**:
  - Implement ScriptParser (markdown → beats)
  - Implement Beat dataclass with auto-duration
  - Build parsing logic for 5-10 second beats
  - Create query generation (stock + YouTube keywords)

### 5. **Senior Programmer (Agent 2)** - Asset Fetching
- **Role**: B-roll acquisition
- **Responsibilities**:
  - Implement YouTubeClient (yt-dlp integration)
  - Implement PexelsClient (API integration)
  - Build fallback logic (YouTube → Pexels)
  - Handle video trimming (ffmpeg)

### 6. **Senior Programmer (Agent 3)** - XML Generation
- **Role**: FCPXML timeline creation
- **Responsibilities**:
  - Implement FCPXMLGenerator class
  - Build XML tree structure (spine + connected clips)
  - Handle resource mapping
  - Validate FCPXML output

### 7. **Senior Programmer (Agent 4)** - Integration & CLI
- **Role**: Orchestration and command-line interface
- **Responsibilities**:
  - Implement VideoOrchestrator (main coordinator)
  - Build CLI interface (argparse)
  - Implement DaVinci Resolve integration
  - Create end-to-end workflow

### 8. **Code Reviewer** - Quality Assurance
- **Role**: Code quality and correctness
- **Responsibilities**:
  - Review each agent's code
  - Check for bugs, edge cases, security issues
  - Ensure consistency with architecture
  - Validate API usage and error handling
  - Check documentation quality

### 9. **Test Engineer** - Quality Verification
- **Role**: Testing and validation
- **Responsibilities**:
  - Create unit tests for each module
  - Build integration tests
  - Test with sample markdown script
  - Validate FCPXML output with Resolve/FCP
  - Create test fixtures and mock data

### 10. **Tech Writer** - Documentation
- **Role**: User and developer documentation
- **Responsibilities**:
  - Write usage guide
  - Create API documentation
  - Document architecture decisions
  - Write example scripts
  - Create troubleshooting guide

## Workflow Phases

### Phase 1: Planning (CPO + CTO + Architect)
**Output**: PRD, architecture diagram, module breakdown, success criteria

### Phase 2: Core Development (Programmers 1-4)
**Output**: Working code modules
- Parallel development: Each programmer owns 1-2 modules
- Dependencies: Parser (Agent 1) → Fetchers (Agent 2) → XML Gen (Agent 3) → Orchestrator (Agent 4)

### Phase 3: Integration (Programmer Agent 4 + Code Reviewer)
**Output**: Unified application
- Ensure all modules work together
- Fix integration issues
- Code review and refactor

### Phase 4: Quality Assurance (Code Reviewer + Test Engineer)
**Output**: Tested, validated product
- Unit test coverage >80%
- Integration tests pass
- FCPXML validates in DaVinci Resolve

### Phase 5: Documentation (Tech Writer)
**Output**: Complete documentation
- User guide
- API docs
- Architecture guide
- Example scripts

## Communication Protocol

### Daily Standup Format
```
[Agent Name] - Progress Update
COMPLETED:
- Task 1
- Task 2

IN_PROGRESS:
- Task 3 (70% done, blocked by X)

BLOCKERS:
- Need decision on Y from CTO

NEXT STEPS:
- Complete task 3
- Start task 4
```

### Decision Escalation
1. **Architectural**: → CTO
2. **Technical Trade-off**: → Architect
3. **Feature Scope**: → CPO
4. **Quality Standards**: → Code Reviewer + Test Engineer

## Success Criteria

✓ CLI tool accepts markdown script  
✓ Parses script into 5-10 second beats  
✓ Generates stock + YouTube queries for each beat  
✓ Fetches B-roll from YouTube or Pexels  
✓ Generates valid FCPXML file  
✓ Imports into DaVinci Resolve (optional)  
✓ >80% test coverage  
✓ Full documentation  
✓ Example scripts provided  
✓ Error handling for missing APIs/networks  

## Key Milestones

| Milestone | Owner | ETA | Status |
|-----------|-------|-----|--------|
| PRD & Architecture Review | CPO/CTO/Architect | Week 1 | ⏳ |
| Core Parser Module | Programmer 1 | Week 1-2 | ⏳ |
| Asset Fetchers Module | Programmer 2 | Week 1-2 | ⏳ |
| XML Generator Module | Programmer 3 | Week 1-2 | ⏳ |
| Orchestrator & CLI | Programmer 4 | Week 2 | ⏳ |
| Code Review + Refactor | Code Reviewer | Week 2 | ⏳ |
| Unit + Integration Tests | Test Engineer | Week 2-3 | ⏳ |
| Documentation | Tech Writer | Week 3 | ⏳ |
| Final QA & Release | All | Week 3 | ⏳ |

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| yt-dlp API changes | High | Monitor repo, version pin, fallback to requests |
| Pexels rate limits | Medium | Implement caching, queue management |
| FCPXML format incompatibility | High | Test with real Resolve, validate XML schema |
| FFmpeg not installed | Medium | Graceful fallback, download trimmed from source |
| No API keys provided | Low | Skip B-roll fetch, generate empty timeline |

## Next Steps

1. **Review this plan** with stakeholders
2. **Assign agents** to each role
3. **Begin Phase 1**: CPO extracts requirements, CTO designs tech stack
4. **Daily standups** to track progress
5. **Weekly reviews** of milestones
