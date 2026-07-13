import { useCallback, useEffect, useState } from 'react';
import { CheckCircle2, RefreshCw, XCircle } from 'lucide-react';
import { api } from '../api';
import type { Preflight } from '../types';

const HINTS: Record<string, string> = {
  ffmpeg: 'Install FFmpeg and add it to PATH (ffmpeg.org/download.html)',
  node: 'Install Node.js (nodejs.org) - YouTube downloads need it',
  ytdlp: 'yt-dlp is missing from the app environment - reinstall the app deps',
  whisper: "Voiceover conform needs faster-whisper: pip install 'screenwrite[vo]'",
  gemini_key: 'Add a Gemini API key in Settings (needed for game mode)',
  pexels_key: 'Optional: add a Pexels key in Settings for stock footage',
  resolve: 'Open DaVinci Resolve Studio with a project to build directly into it',
};

const LABELS: Record<string, string> = {
  ffmpeg: 'FFmpeg',
  node: 'Node.js',
  ytdlp: 'yt-dlp',
  whisper: 'Whisper (VO)',
  gemini_key: 'Gemini key',
  pexels_key: 'Pexels key',
  resolve: 'DaVinci Resolve',
};

// Soft checks don't block runs; they gate specific features only.
const SOFT = new Set(['pexels_key', 'whisper', 'resolve', 'gemini_key']);

export function usePreflight() {
  const [preflight, setPreflight] = useState<Preflight | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setPreflight(await api.preflight(true));
    } catch {
      // Server unreachable; leave the previous state.
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { preflight, loading, refresh };
}

export default function PreflightPanel({
  preflight,
  loading,
  onRefresh,
}: {
  preflight: Preflight | null;
  loading: boolean;
  onRefresh: () => void;
}) {
  if (!preflight) {
    return (
      <div className="card text-sm text-slate-400">Checking your setup...</div>
    );
  }

  const entries = Object.entries(preflight) as [string, { ok: boolean; error?: string }][];
  const problems = entries.filter(([key, state]) => !state.ok && !SOFT.has(key));

  return (
    <div className="card">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-300">
          Setup {problems.length === 0 ? 'looks good' : 'needs attention'}
        </h2>
        <button className="btn-secondary !px-2 !py-1" onClick={onRefresh} disabled={loading}>
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          Check again
        </button>
      </div>
      <ul className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-sm">
        {entries.map(([key, state]) => (
          <li key={key} className="flex items-start gap-2">
            {state.ok ? (
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
            ) : (
              <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" />
            )}
            <span>
              <span className={state.ok ? 'text-slate-200' : 'text-slate-300'}>
                {LABELS[key] ?? key}
              </span>
              {!state.ok && (
                <span className="block text-xs text-slate-500">{HINTS[key] ?? state.error}</span>
              )}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
