import type {
  Preflight,
  RunRequest,
  RunResult,
  RunSnapshot,
  SettingsPayload,
} from './types';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || body.message || `HTTP ${response.status}`);
  }
  return body as T;
}

export const api = {
  preflight: (includeResolve = true) =>
    request<Preflight>(`/api/preflight?resolve=${includeResolve ? 1 : 0}`),

  getSettings: () => request<SettingsPayload>('/api/settings'),

  putSettings: (payload: {
    keys?: { gemini?: string; pexels?: string };
    defaults?: Partial<SettingsPayload['defaults']>;
  }) => request<SettingsPayload>('/api/settings', {
    method: 'PUT',
    body: JSON.stringify(payload),
  }),

  testKey: (provider: 'gemini' | 'pexels', key?: string) =>
    request<{ ok: boolean; message: string }>('/api/settings/test-key', {
      method: 'POST',
      body: JSON.stringify({ provider, key }),
    }),

  loadScript: (path: string) =>
    request<{ text: string; path: string }>('/api/script/load', {
      method: 'POST',
      body: JSON.stringify({ path }),
    }),

  startRun: (payload: RunRequest) =>
    request<{ run_id: string }>('/api/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  currentRun: (afterSeq = 0) =>
    request<RunSnapshot>(`/api/run/current?after_seq=${afterSeq}`),

  cancelRun: (runId: string) =>
    request<{ cancelled: boolean }>(`/api/run/${runId}/cancel`, { method: 'POST' }),

  runResult: (runId: string) => request<RunResult>(`/api/run/${runId}/result`),

  reveal: (path: string) =>
    request<{ ok: boolean }>('/api/reveal', {
      method: 'POST',
      body: JSON.stringify({ path }),
    }),

  clearCache: () => request<{ ok: boolean }>('/api/cache/clear', { method: 'POST' }),
};

// ---------------------------------------------------------------------------
// pywebview bridge: native file dialogs give REAL paths (browser inputs
// can't). In --dev (plain browser) these return null and the UI hides the
// affordance or falls back to drag-drop/paste.
// ---------------------------------------------------------------------------

interface PywebviewApi {
  pick_file: (kind: string) => Promise<string | null>;
}

declare global {
  interface Window {
    pywebview?: { api: PywebviewApi };
  }
}

export function hasNativeBridge(): boolean {
  return typeof window.pywebview?.api?.pick_file === 'function';
}

export async function pickFile(
  kind: 'script' | 'vo' | 'fcpxml_save' | 'folder',
): Promise<string | null> {
  if (!hasNativeBridge()) return null;
  try {
    return await window.pywebview!.api.pick_file(kind);
  } catch {
    return null;
  }
}
