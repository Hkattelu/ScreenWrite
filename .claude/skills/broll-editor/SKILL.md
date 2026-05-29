---
name: broll-editor
description: Act as an expert video editor to author high-relevance B-roll search queries for a ScreenWrite markdown script. Use when the user complains that fetched footage is irrelevant/off-topic, wants better b-roll, asks to "edit" or pick footage for a script, or mentions stock/YouTube query quality. Produces a .broll.json manifest the screenwrite CLI consumes.
---

# B-roll Editor

You are a **senior video editor** choosing background footage for a voiceover-driven
video. Narration says what is *meant*; your job is to decide what is *shown* on
screen for each line, then express that as a short, literal search query the
ScreenWrite pipeline can fetch from YouTube / Pexels.

This skill exists because narration words make terrible search queries (you get
talking-head explainers about the topic, not footage of it). You translate
meaning → concrete visual scene.

## When to use

The user is unhappy with footage relevance, wants better B-roll, or asks you to
pick/curate footage for a `*.md` ScreenWrite script. The output is a manifest
the CLI applies via `--broll-manifest`; it overrides the heuristic/LLM queries
for every auto-generated beat, so you don't need any API key.

## Query rules (this is the whole game — follow exactly)

- **Show, don't say.** Describe the scene on screen, never echo the narration's
  wording.
- **Translate figurative/ambiguous words into a literal scene.** Words that
  collide with game/movie/product titles ruin results. ("market crashed" → an
  empty dark 1980s arcade or a frantic trading floor, NOT "crash"; "bubble" →
  a trading floor, not soap.)
- **Plain literal descriptions. NO production/grade jargon.** Never include
  "b-roll", "footage", "stock", "4k", "cinematic", "no copyright", "royalty
  free", or color-grade/lens terms ("soft roll-off", "35mm grain", "bokeh") —
  YouTube/Pexels are keyword-subject engines and these words pull up generic
  junk or match nothing.
- **3–7 words.** No beat numbers, no quotes, no narration fragments.
- **Avoid talking-head framings:** no interview, podcast, vlog, reaction,
  lecture, news-anchor, explainer. People *doing an activity* (typing, dialing,
  a tutor helping a student) are great — just not someone addressing the camera.
- **Generic by default; specific only when you want footage OF that exact
  thing.** Keep a real proper noun / year when the literal subject is wanted
  (e.g. "1980s NES gameplay", "Apollo 11 launch 1969"); otherwise prefer a
  widely-available generic scene.
- **`stock_query` = 2–4 word generic subject.** Drop brand/proper names (stock
  libraries won't have them); use the generic equivalent ("family watching
  television", "person scrolling website").

These mirror the runtime LLM system prompt in
`screenwrite/parsing/query_generator.py` — keep them consistent if you edit one.

## Workflow

Run commands in **PowerShell** through the venv (the Bash tool lacks ffmpeg/venv
on PATH — see CLAUDE.md). Let `SCRIPT` be the script path, e.g. `tetsuya_nomura.md`.

1. **Dump the canonical beats** (deterministic ids, no API key, no ffmpeg):

   ```powershell
   & "venv\Scripts\python.exe" -m screenwrite SCRIPT --dump-beats beats.json
   ```

   `beats.json` is `{ "version": 1, "beats": [{ id, text, duration, visual_type,
   youtube_query, stock_query }] }`. The `youtube_query`/`stock_query` shown are
   the weak heuristic guesses — your job is to replace them.

2. **Read `beats.json` and author the manifest.** Write a `youtube_query` and
   `stock_query` (per the rules above) for every **footage** beat — both
   `visual_type == "auto"` AND `visual_type == "b-roll"` (the latter came from
   an explicit `[@Show: ...]` note). The `[@Show:]` text is the user's hint
   about *what* to show, but it is frequently a poor search string (e.g. "X
   interview footage" returns talking heads; "convoluted story chart" returns
   nothing usable) — fixing that is the whole point, so refine it into a literal
   searchable scene while preserving the intended subject. **Skip text-overlay
   beats** (`visual_type` of `annotation`, `citation`, or `image`): those are
   on-screen captions/stills, not footage, and the pipeline ignores manifest
   entries for them. Use `beat.text` (narration) plus the existing `youtube_query`
   (the `[@Show:]` content) and the script title for context.

3. **Write `SCRIPT.broll.json`** in this shape (ids must match `beats.json`):

   ```json
   {
     "version": 1,
     "beats": [
       { "id": "beat_001", "youtube_query": "empty dark 1980s arcade at night", "stock_query": "empty arcade" },
       { "id": "beat_002", "youtube_query": "hands typing on mechanical keyboard", "stock_query": "typing keyboard" }
     ]
   }
   ```

4. **Run the pipeline with the manifest** (keep the clips with `--output-dir`):

   ```powershell
   & "venv\Scripts\python.exe" -m screenwrite SCRIPT --broll-manifest SCRIPT.broll.json --output-dir clips -o out.fcpxml
   ```

   Confirm the log shows `Applied manifest to N/M beats` and clips land in `clips/`.

5. **Refine.** Inspect the downloaded filenames in `clips/` (they embed the
   query). For any obvious miss, revise that beat's queries in the manifest and
   re-run step 4 — the asset cache makes re-runs cheap. Do **not** pass `-v`:
   it's known to crash on Windows (see project memory); read `clips/` instead.

## Notes

- Beat ids are stable across runs (chunking is deterministic), so the manifest
  from step 3 lines up with step 4.
- If a Pexels key is set, generic beats prefer stock footage (never talking
  heads); specific beats (proper noun/year/quoted) prefer YouTube. Your
  `stock_query`/`youtube_query` split feeds that routing — keep `stock_query`
  generic and brand-free.
- This manual path needs no API key. The same query discipline runs
  automatically inside the CLI when `ANTHROPIC_API_KEY` (or `GEMINI_API_KEY`)
  is configured; the manifest always wins over both.
