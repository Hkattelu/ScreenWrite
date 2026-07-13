import { useEffect, useState } from 'react';
import { AudioLines, FileText, FolderOpen, Play, X } from 'lucide-react';
import { api, hasNativeBridge, pickFile } from '../api';
import type { RunRequest } from '../types';
import PreflightPanel, { usePreflight } from '../components/PreflightPanel';

export default function Home({
  onStart,
  startError,
  lastRequest,
}: {
  onStart: (payload: RunRequest) => void;
  startError: string | null;
  lastRequest: RunRequest | null;
}) {
  const { preflight, loading, refresh } = usePreflight();
  const [script, setScript] = useState(lastRequest?.script_text ?? '');
  const [game, setGame] = useState(lastRequest?.game ?? '');
  const [voPath, setVoPath] = useState<string | null>(lastRequest?.vo_path ?? null);
  const [buildResolve, setBuildResolve] = useState(lastRequest?.resolve ?? false);
  const [dryRun, setDryRun] = useState(lastRequest?.dry_run ?? false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [wikiSubdomain, setWikiSubdomain] = useState(lastRequest?.wiki_subdomain ?? '');
  const [outputPath, setOutputPath] = useState(lastRequest?.output_path ?? '');

  // Prefill the game from settings once (quality-of-life).
  useEffect(() => {
    if (!game) {
      api.getSettings()
        .then((s) => s.defaults.last_game && setGame(s.defaults.last_game))
        .catch(() => undefined);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openScript = async () => {
    const path = await pickFile('script');
    if (!path) return;
    try {
      const { text } = await api.loadScript(path);
      setScript(text);
    } catch {
      /* surfaced by empty editor */
    }
  };

  const onDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setScript(String(reader.result ?? ''));
    reader.readAsText(file);
  };

  const resolveOk = preflight?.resolve?.ok ?? false;
  const geminiOk = preflight?.gemini_key?.ok ?? false;
  const ffmpegOk = preflight?.ffmpeg?.ok ?? false;
  const canRun =
    script.trim().length > 0 &&
    (dryRun || ffmpegOk) &&
    (!buildResolve || resolveOk);

  const start = () =>
    onStart({
      script_text: script,
      game: game.trim() || undefined,
      vo_path: voPath,
      resolve: buildResolve,
      dry_run: dryRun,
      wiki_subdomain: wikiSubdomain.trim() || undefined,
      output_path: outputPath.trim() || undefined,
    });

  return (
    <div className="space-y-4">
      <PreflightPanel preflight={preflight} loading={loading} onRefresh={refresh} />

      <div className="card space-y-4">
        <div>
          <div className="mb-1 flex items-center justify-between">
            <label className="label !mb-0">Script</label>
            {hasNativeBridge() && (
              <button className="btn-secondary !px-2 !py-1 text-xs" onClick={openScript}>
                <FileText className="h-3.5 w-3.5" /> Open file...
              </button>
            )}
          </div>
          <textarea
            className="input h-48 resize-y font-mono text-[13px] leading-relaxed"
            placeholder={'Paste or write your script here - or drop a .md file.\n\ntitle: My Video\ngame: Dark Souls\n\nThe Bell Gargoyles are where the difficulty really bares its teeth...'}
            value={script}
            onChange={(event) => setScript(event.target.value)}
            onDrop={onDrop}
            onDragOver={(event) => event.preventDefault()}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Game</label>
            <input
              className="input"
              placeholder="e.g. Dark Souls (enables gameplay matching)"
              value={game}
              onChange={(event) => setGame(event.target.value)}
            />
            {game.trim() && !geminiOk && (
              <p className="mt-1 text-xs text-amber-400">
                No valid Gemini key - beats will only match [@Show: ...] tags.
              </p>
            )}
          </div>
          <div>
            <label className="label">Voiceover (optional)</label>
            {voPath ? (
              <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm">
                <AudioLines className="h-4 w-4 shrink-0 text-indigo-400" />
                <span className="truncate" title={voPath}>
                  {voPath.split(/[\\/]/).pop()}
                </span>
                <button className="ml-auto text-slate-500 hover:text-slate-300" onClick={() => setVoPath(null)}>
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <button
                className="btn-secondary w-full justify-center"
                onClick={async () => setVoPath(await pickFile('vo'))}
                disabled={!hasNativeBridge()}
                title={hasNativeBridge() ? '' : 'Available in the desktop app'}
              >
                <AudioLines className="h-4 w-4" /> Pick VO audio...
              </button>
            )}
            <p className="mt-1 text-xs text-slate-500">
              With a VO, every cut lands on your real pauses.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-5 border-t border-slate-800 pt-4 text-sm">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              className="h-4 w-4 accent-indigo-500"
              checked={buildResolve}
              onChange={(event) => setBuildResolve(event.target.checked)}
              disabled={!resolveOk}
            />
            <span className={resolveOk ? '' : 'text-slate-500'}>
              Build into DaVinci Resolve
              {!resolveOk && ' (open Resolve Studio with a project first)'}
            </span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              className="h-4 w-4 accent-indigo-500"
              checked={dryRun}
              onChange={(event) => setDryRun(event.target.checked)}
            />
            Preview only (no downloads)
          </label>
          <button
            className="ml-auto text-xs text-slate-500 hover:text-slate-300"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? 'Hide advanced' : 'Advanced...'}
          </button>
        </div>

        {showAdvanced && (
          <div className="grid grid-cols-2 gap-4 border-t border-slate-800 pt-4">
            <div>
              <label className="label">Wiki subdomain override</label>
              <input
                className="input"
                placeholder="e.g. darksouls (for darksouls.fandom.com)"
                value={wikiSubdomain}
                onChange={(event) => setWikiSubdomain(event.target.value)}
              />
            </div>
            <div>
              <label className="label">Save timeline as</label>
              <div className="flex gap-2">
                <input
                  className="input"
                  placeholder="Default: the run folder"
                  value={outputPath}
                  onChange={(event) => setOutputPath(event.target.value)}
                />
                {hasNativeBridge() && (
                  <button
                    className="btn-secondary shrink-0 !px-2.5"
                    onClick={async () => {
                      const path = await pickFile('fcpxml_save');
                      if (path) setOutputPath(path);
                    }}
                  >
                    <FolderOpen className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {startError && (
          <p className="rounded-lg border border-rose-900 bg-rose-950/40 px-3 py-2 text-sm text-rose-300">
            {startError}
          </p>
        )}

        <button className="btn-primary w-full justify-center !py-3 text-base" onClick={start} disabled={!canRun}>
          <Play className="h-5 w-5" />
          {dryRun ? 'Preview pacing' : 'Build my timeline'}
        </button>
      </div>
    </div>
  );
}
