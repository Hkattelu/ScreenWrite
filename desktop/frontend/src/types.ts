// Shapes shared with the desktop server (see desktop/runner/events.py and
// desktop/server/runs.py for the source of truth).

export interface RunEvent {
  seq: number;
  ts: number;
  type: 'run_started' | 'step' | 'beat_progress' | 'log' | 'result' | 'fatal';
  step?: string;
  label?: string;
  done?: number;
  total?: number;
  level?: string;
  logger?: string;
  message?: string;
  success?: boolean;
  error?: string;
}

export type RunStateName =
  | 'idle'
  | 'running'
  | 'succeeded'
  | 'failed'
  | 'cancelled'
  | 'crashed';

export interface RunSnapshot {
  run_id: string | null;
  state: RunStateName;
  step?: string | null;
  beat_done?: number;
  beat_total?: number;
  started_at?: number;
  events: RunEvent[];
  last_seq: number;
  fatal?: { error?: string; traceback?: string; log_tail?: string } | null;
}

export interface CoverageCounts {
  game_entity_clips: number;
  game_entity_stills: number;
  game_entity_uncovered: number;
  abstract_stock: number;
  abstract_uncovered: number;
  manual_fill: number;
}

export interface VoPacingRow {
  beat_id: string;
  est: number;
  start: number;
  end: number;
  duration: number;
  coverage: number;
  matched: boolean;
}

export interface WorkflowResult {
  success: boolean;
  beats_count: number;
  total_duration: number;
  assets_fetched: number;
  fcpxml_generated: boolean;
  resolve_imported: boolean;
  resolve_native_built?: boolean;
  vo_conformed?: boolean;
  vo_matched_beats?: number;
  vo_pacing?: VoPacingRow[];
  coverage?: { counts: CoverageCounts; notes: string[] };
  warnings: string[];
  errors: string[];
  output_path?: string;
}

export interface RunResult {
  run_id: string;
  workflow_result: WorkflowResult;
  fcpxml_path?: string;
  run_dir: string;
}

export interface CheckState {
  ok: boolean;
  error?: string;
  project_name?: string;
}

export interface Preflight {
  ffmpeg: CheckState;
  node: CheckState;
  ytdlp: CheckState;
  whisper: CheckState;
  gemini_key: CheckState;
  pexels_key: CheckState;
  resolve?: CheckState;
}

export interface SettingsPayload {
  gemini_key: string | null;
  pexels_key: string | null;
  defaults: {
    media_dir: string;
    whisper_model: string | null;
    max_workers: number;
    last_game: string;
    prefer_stock_for_generic: boolean;
    use_llm_queries: boolean;
    skip_failed_beats: boolean;
  };
}

export interface RunRequest {
  script_text: string;
  game?: string;
  vo_path?: string | null;
  output_path?: string;
  resolve?: boolean;
  dry_run?: boolean;
  wiki_subdomain?: string;
  whisper_model?: string;
}
