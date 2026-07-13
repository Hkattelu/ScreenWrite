import { useEffect, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clapperboard,
  FolderOpen,
  Image,
  RotateCcw,
  XCircle,
} from 'lucide-react';
import { api } from '../api';
import type { RunResult } from '../types';

export default function Report({
  runId,
  onRunAgain,
}: {
  runId: string;
  onRunAgain: () => void;
}) {
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.runResult(runId).then(setResult).catch((e) => setError(String(e)));
  }, [runId]);

  if (error) {
    return (
      <div className="card">
        <p className="flex items-center gap-2 text-rose-300">
          <XCircle className="h-5 w-5" /> The run ended without a result. Check the
          run folder's log for details.
        </p>
        <button className="btn-secondary mt-4" onClick={onRunAgain}>
          <RotateCcw className="h-4 w-4" /> Back
        </button>
      </div>
    );
  }
  if (!result) {
    return <div className="card text-sm text-slate-400">Loading result...</div>;
  }

  const wf = result.workflow_result;
  const counts = wf.coverage?.counts;

  const coverageCards = counts
    ? [
        { label: 'Gameplay clips', value: counts.game_entity_clips, icon: Clapperboard, tone: 'text-sky-400' },
        { label: 'Wiki stills', value: counts.game_entity_stills, icon: Image, tone: 'text-emerald-400' },
        { label: 'Need your shot', value: counts.game_entity_uncovered + counts.abstract_uncovered + counts.manual_fill, icon: AlertTriangle, tone: 'text-rose-400' },
        { label: 'Stock footage', value: counts.abstract_stock, icon: Image, tone: 'text-amber-400' },
      ]
    : [];

  return (
    <div className="space-y-4">
      <div className={`card border-l-4 ${wf.success ? 'border-l-emerald-500' : 'border-l-rose-500'}`}>
        <p className="flex items-center gap-2 text-base font-semibold">
          {wf.success ? (
            <>
              <CheckCircle2 className="h-5 w-5 text-emerald-400" /> Your timeline is ready
            </>
          ) : (
            <>
              <XCircle className="h-5 w-5 text-rose-400" /> The run hit a problem
            </>
          )}
        </p>
        <p className="mt-1 text-sm text-slate-400">
          {wf.beats_count} beats · {Math.round(wf.total_duration)}s
          {wf.vo_conformed && ` · cut to your voiceover (${wf.vo_matched_beats}/${wf.beats_count} beats matched)`}
          {wf.resolve_native_built && ' · built inside DaVinci Resolve'}
        </p>
      </div>

      {coverageCards.length > 0 && (
        <div className="grid grid-cols-4 gap-3">
          {coverageCards.map(({ label, value, icon: Icon, tone }) => (
            <div key={label} className="card !p-4 text-center">
              <Icon className={`mx-auto mb-1 h-5 w-5 ${tone}`} />
              <div className="text-2xl font-bold text-slate-100">{value}</div>
              <div className="text-xs text-slate-400">{label}</div>
            </div>
          ))}
        </div>
      )}

      {wf.vo_pacing && wf.vo_pacing.length > 0 && (
        <div className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-300">Voiceover pacing</h3>
          <div className="max-h-56 overflow-y-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-500">
                <tr>
                  <th className="pb-1 pr-4">Beat</th>
                  <th className="pb-1 pr-4">Estimated</th>
                  <th className="pb-1 pr-4">In your VO</th>
                  <th className="pb-1 pr-4">Length</th>
                  <th className="pb-1">Found</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                {wf.vo_pacing.map((row) => (
                  <tr key={row.beat_id} className={row.matched ? '' : 'text-rose-400'}>
                    <td className="py-0.5 pr-4 font-mono">{row.beat_id}</td>
                    <td className="py-0.5 pr-4">{row.est.toFixed(1)}s</td>
                    <td className="py-0.5 pr-4">
                      {row.start.toFixed(1)}-{row.end.toFixed(1)}s
                    </td>
                    <td className="py-0.5 pr-4">{row.duration.toFixed(1)}s</td>
                    <td className="py-0.5">{row.matched ? 'yes' : 'NOT IN VO'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {(wf.warnings.length > 0 || wf.errors.length > 0) && (
        <div className="card">
          <h3 className="mb-2 text-sm font-semibold text-slate-300">Things to know</h3>
          <ul className="space-y-1 text-sm">
            {wf.errors.map((line, index) => (
              <li key={`e${index}`} className="flex gap-2 text-rose-300">
                <XCircle className="mt-0.5 h-4 w-4 shrink-0" /> {line}
              </li>
            ))}
            {wf.warnings.map((line, index) => (
              <li key={`w${index}`} className="flex gap-2 text-amber-300/90">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" /> {line}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-3">
        {result.fcpxml_path && (
          <button className="btn-primary" onClick={() => api.reveal(result.fcpxml_path!)}>
            <FolderOpen className="h-4 w-4" /> Show timeline file
          </button>
        )}
        <button className="btn-secondary" onClick={() => api.reveal(result.run_dir)}>
          <FolderOpen className="h-4 w-4" /> Open run folder
        </button>
        <button className="btn-secondary ml-auto" onClick={onRunAgain}>
          <RotateCcw className="h-4 w-4" /> Run again
        </button>
      </div>
    </div>
  );
}
