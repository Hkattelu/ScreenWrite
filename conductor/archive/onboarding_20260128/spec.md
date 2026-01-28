# Specification: Streamlined Onboarding & Local Setup

## Overview
The goal of this track is to transform the "git clone" experience into a seamless, one-command setup process. This will lower the barrier to entry for new users and developers, ensuring that system dependencies are verified and the environment is correctly configured with minimal manual intervention.

## Functional Requirements
- **Unified Setup Scripts:** Provide `setup.ps1` (Windows) and `setup.sh` (Unix) that automate:
    - Python version validation (3.7+).
    - Node.js/NPM presence check.
    - Virtual environment (`venv`) creation and activation.
    - Installation of Python dependencies (`requirements.txt`).
    - Installation of Frontend dependencies (`npm install`).
- **System Dependency Checker:**
    - Detect if `ffmpeg` and `yt-dlp` are installed and accessible in the system PATH.
    - If missing, provide the user with clear information and direct download links (Informational approach).
- **Environment Configuration:**
    - Detect missing `.env` files in both the root/backend and frontend.
    - Automatically create `.env` files from templates (`.env.example`).
    - Prompt the user to enter their Gemini API key during the setup flow.
- **Path Validation:** Verify that critical paths are correctly recognized by the environment.

## Non-Functional Requirements
- **Idempotency:** Running the setup script multiple times should not break the environment or duplicate configurations.
- **Clarity:** Output should be clean, using colors or clear headers to distinguish between phases (Checking, Installing, Configuring).

## Acceptance Criteria
- A user can run `git clone` followed by `./setup.ps1` (or `sh setup.sh`) and have a fully functional environment.
- The script correctly identifies missing `ffmpeg` and provides valid download links.
- The script successfully prompts for and saves the Gemini API key into the `.env` file.
- The backend and frontend are ready to be started immediately after the script finishes.

## Out of Scope
- Automated installation of system-level binaries (e.g., auto-installing ffmpeg via Winget/Brew).
- Bundling the app into a standalone executable (Electron/PyInstaller).
- Dockerization.
