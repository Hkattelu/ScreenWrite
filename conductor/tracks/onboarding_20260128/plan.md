# Implementation Plan: Streamlined Onboarding & Local Setup

## Phase 1: Environment & Dependency Validation
- [x] Task: Create a cross-platform dependency checking module in Python
    - [x] Implement version checks for Python (3.7+) and Node.js
    - [x] Implement existence checks for `ffmpeg` and `yt-dlp` in system PATH
    - [x] Define a dictionary of download links/instructions for missing dependencies
- [x] Task: Create .env management utility
    - [x] Implement logic to check for `.env` files based on `.env.example`
    - [x] Implement interactive prompting for the Gemini API key
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Unified Setup Scripts
- [x] Task: Implement `setup.sh` for Unix-like systems
    - [x] Script should handle venv creation, dependency installation (pip & npm), and call the Python validation/onboarding module
- [x] Task: Implement `setup.ps1` for Windows systems
    - [x] Script should mirror the `setup.sh` logic using PowerShell idioms
- [x] Task: Integrate interactive onboarding into the setup flow
    - [x] Ensure the Python utility runs after dependencies are installed to finalize configuration
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Documentation & Verification
- [ ] Task: Update `README.md` with the new "Quick Start" instructions
- [ ] Task: Verify the end-to-end flow on a clean environment simulation
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
