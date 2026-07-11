# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ScreenWrite turns a Markdown video script into a DaVinci Resolve / Final Cut timeline (FCPXML 1.8), automatically fetching B-roll from YouTube (yt-dlp) and Pexels. There is a CLI (the primary interface) and a Flask + React web app wrapper around the same `screenwrite` package.

## Commands

Setup & dev (creates venv, installs Python + frontend deps, runs onboarding wizard):
- `./setup.ps1` / `./setup.sh`
- `./run_dev.ps1` / `./run_dev.sh` — starts Flask backend on `:5000` and Vite frontend on `:3000` together.

CLI (entry point `screenwrite.cli:main`, also `python -m screenwrite`):
- `screenwrite script.md -o timeline.fcpxml`
- Useful flags: `--no-fetch`/`--dry-run` (skip downloads), `--resolve` (import into DaVinci), `--disable-youtube` / `--disable-pexels`, `--max-workers N`, `--clear-cache`, `-v`.
- Game-essay mode: `--game "Dark Souls"` (or a `game:` header in the script) activates the game b-roll pipeline described under Architecture; `--wiki-subdomain` overrides the guessed Fandom wiki. Requires `GEMINI_API_KEY`.

Tests & lint (the canonical runner; targets `screenwrite/` and `tests/`):
- `python tests/run_lint_and_tests.py` — runs flake8, pylint, then the unittest suite.
- `--lint-only` / `--tests-only` / `--fast` (skip pylint) / `--coverage` / `-v`.
- Tests run via **unittest discover** (`python -m unittest discover -s tests -p "test_*.py"`), so a single test is `python -m unittest tests.test_beat`. `pyproject.toml` also configures pytest (`pytest tests/test_beat.py`) and some suites use `hypothesis` property tests.

Frontend (in `webapp/frontend/`): `npm run build` (`tsc && vite build`), `npm run lint`, `npm run type-check`.

## Architecture

The pipeline is **parse → fetch → generate**, coordinated by `VideoOrchestrator` (`screenwrite/orchestrator.py`). The CLI builds a config dict from args and runs the orchestrator as a context manager (auto-cleans its temp dir). Understanding these four collaborators is enough to navigate most changes:

1. **`ScriptParser` (`parsing/script_parser.py`)** — Markdown → list of `Beat`s. A `key: value` header block supplies metadata (title/hook/channel/tags) used as B-roll context; `#`/`##` headers add section context; body paragraphs are chunked into 5–10s beats. Inline `[@action: content]` instructions override auto-generated queries. **Search queries are generated here by heuristics** (stop-word stripping + regex patterns defined in `config/constants.py`), *not* by an LLM — the README's "Gemini-powered analysis" is aspirational; Gemini only appears in `onboarding.py`/`utils/env_manager.py` key management today.

2. **`Beat` (`core/beat.py`)** — dataclass per segment. `duration` is auto-derived from word count via `WORDS_PER_SECOND` (2.5) and validated to 3–10s in `__post_init__`. Carries `stock_keyword`, `youtube_search_phrase`, and `asset_paths`.

3. **`AssetOrchestrator` (`fetchers/asset_orchestrator.py`)** — coordinates fetchers with a **YouTube → Pexels fallback** (fetchers tried in priority order). `fetch_assets_batch` parallelizes across beats with a `ThreadPoolExecutor`. The search-then-download path (`search_assets` → `AssetCandidate` → `download_candidate`/`download_segment`) backs the web app's preview/selection UX. Fetchers subclass `base_fetcher.AssetFetcher`: `YouTubeClient` (yt-dlp + ffmpeg) and `PexelsClient` (requests).

4. **`XMLGenerator` (`generators/xml_generator.py`)** — emits FCPXML 1.8. Optional `ResolveIntegration` (`resolve_integration.py`, lazily imported) imports the result into DaVinci.

Cross-cutting: `utils/cache.py` provides persistent beat + asset caching (skippable via `--disable-cache`); all tunable magic numbers and the query-generation stop-word/pattern lists live in `config/constants.py`.

### Game b-roll pipeline (game-essay mode)

Activated by `--game` or a `game:` script header (spec: `game-broll-spec.md` in the parent workspace). Instead of narration-keyword search, beats are LLM-classified (`parsing/entity_extractor.py`, Gemini) into `beat_class` = `game_entity` / `abstract` / `manual_fill`, with named in-game `entities` extracted per beat. Routing (in `AssetOrchestrator.fetch_game_assets_batch`): game_entity → `ChapteredGameplayFetcher` (fuzzy-matches entities against chapter markers of "all bosses"/walkthrough videos read from yt-dlp metadata; 2–3 candidates at different start offsets within matched chapters, loose 9s+ windows) → `WikiStillFetcher` (Fandom infobox still) → labeled manual-fill gap. Abstract beats get at most one Pexels candidate; manual_fill beats never fetch. Every placed clip carries an FCPXML marker with beat text + source URL + chapter timestamp; coverage (clips/stills/uncovered per class) is reported in the CLI summary, never papered over. The game fetchers are deliberately kept out of the legacy fetcher fallback chain — their queries are entity names, not narration keywords. Without a `GEMINI_API_KEY` the classifier can't run and the script falls back to the legacy pipeline with a warning.

### Web app
- **Backend** (`webapp/backend/app.py`): Flask + flask-cors, blueprints registered under `/api`: `upload`, `api`, `export`, `fetch`, `simple_broll`. State is **session-based** — `session_utils.py` persists each session to `SESSION_FOLDER/<id>/state.json` via atomic temp-file rename. Reads `PEXELS_API_KEY` etc. from `.env` (`python-dotenv`).
- **Frontend** (`webapp/frontend/`): React 18 + TypeScript + Vite + Tailwind + framer-motion. Vite dev server proxies `/api` → `:5000`. Pages: `Home`, `Workflow`, `SimpleBRoll`, `SyntaxGuide`.

## Conventions

- External requirements: **FFmpeg** (mandatory whenever fetching), **yt-dlp**, Python 3.8+, Node. `PEXELS_API_KEY` enables stock footage (via flag or env); without it Pexels is silently disabled.
- Python style follows the Google Python Style Guide (`conductor/code_styleguides/python.md`) **except line length is 100** (set by `black` and pylint in `pyproject.toml`), not 80. Run `black` before committing.
- This repo is managed with the **Conductor** workflow: specs, tracks, and product docs live under `conductor/`. Active design specs also live in `.kiro/specs/`. Consult these for product intent before larger changes.

## Running the engine locally (Windows) — environment notes

These save rediscovery when actually fetching assets on this machine:

- **Run through the venv in PowerShell, not the Bash tool.** Invoke `& "venv\Scripts\python.exe" -m screenwrite <script.md> -o out.fcpxml ...`. The agent Bash tool runs in a separate environment where **ffmpeg and the venv are not on PATH** (`shutil.which("ffmpeg")` → `None`), so CLI fetches launched from Bash fail the dependency gate. Native PowerShell has them.
- **ffmpeg** is mandatory for fetching and lives at `C:\Users\himan\ffmpeg\bin\ffmpeg.exe` (on PATH in PowerShell). Its version flag is **`-version`** (single dash) — `--version` exits non-zero on some builds (this previously broke the CLI's dependency check).
- **Keep your clips:** pass `--output-dir <dir>`. Without it the orchestrator creates a temp dir (prefix `screenwrite_`) and **deletes it on exit**, so downloaded clips vanish.
- **API keys** load from `.env` (CLI calls `load_dotenv()`; web backend does too). Missing/invalid keys fall back silently: no `PEXELS_API_KEY` → Pexels disabled (YouTube-only); no/invalid `GEMINI_API_KEY` → LLM visual queries fall back to heuristics. A well-formed Gemini key (`AIza…`) can still be rejected with "API Key not found" if the Generative Language API isn't enabled for its project — verify before assuming the LLM path ran.
- **Quick smoke test without downloads:** add `--dry-run` (parse + FCPXML only).
