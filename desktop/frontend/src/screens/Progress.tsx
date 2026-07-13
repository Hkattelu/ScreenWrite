import { useEffect, useMemo, useRef, useState } from 'react';
import { Check, Loader2, OctagonX } from 'lucide-react';
import { api } from '../api';
import { useRunPolling } from '../usePolling';
import type { RunEvent } from '../types';

const STEP_ORDER = ['parse', 'vo_conform', 'fetch', 'timeline', 'resolve'] as const;
const STEP_LABELS: Record<string, string> = {
  parse: 'Read script',
  vo_conform: 'Match voiceover',
  fetch: 'Find footage',
  timeline: 'Build timeline',
  resolve: 'Send to Resolve',
};

export default function Progress({
  runId,
  onFinished,
  onCancelled,
}: {
  runId: string;
  onFinished: () => void;
  onCancelled: () => void;
}) {
  const { snapshot, events } = useRunPolling(true);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const feedRef = useRef<HTMLDivElement>(null);
  const [stallSeconds, setStallSeconds] = useState(0);

  const state = snapshot?.state ?? 'running';
  const currentStep = snapshot?.step ?? null;

  // Route on terminal states.
  useEffect(() => {
    if (state === 'succeeded' || state === 'failed' || state === 'crashed') {
      const timer = window.setTimeout(onFinished, 600);
      return () => window.clearTimeout(timer);
    }
    if (state === 'cancelled') {
      const timer = window.setTimeout(onCancelled, 600);
      return () => window.clearTimeout(timer);
    }
    return undefined;
  }, [state, onFinished, onCancelled]);

  // Autoscroll the feed.
  useEffect(() => {
    feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight });
  }, [events.length]);

  // Stall timer for the whisper-model-download hint.
  useEffect(() => {
    setStallSeconds(0);
    const timer = window.setInterval(() => setStallSeconds((s) => s + 1), 1000);
    return () => window.clearInterval(timer);
  }, [events.length, currentStep]);

  const logLines = useMemo(
    () => events.filter((event: RunEvent) => event.type === 'log' || event.type === 'step').slice(-500),
    [events],
  );

  const stepIndex = currentStep ? STEP_ORDER.indexOf(currentStep as never) : -1;
  const beatDone = snapshot?.beat_done ?? 0;
  const beatTotal = snapshot?.beat_total ?? 0;

  return (
    <div className="space-y-4">
      <div className="card">
        <ol className="flex items-center justify-between">
          {STEP_ORDER.map((step, index) => {
            const reached = stepIndex >= index;
            const isCurrent = stepIndex === index && state === 'running';
            return (
              <li key={step} className="flex flex-1 items-center gap-2 last:flex-none">
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs font-bold
                    ${reached ? 'border-indigo-500 bg-indigo-600 text-white' : 'border-slate-700 text-slate-500'}`}
                >
                  {isCurrent ? <Loader2 className="h-4 w-4 animate-spin" /> : reached ? <Check className="h-4 w-4" /> : index + 1}
                </span>
                <span className={`text-xs ${reached ? 'text-slate-200' : 'text-slate-500'}`}>
                  {STEP_LABELS[step]}
                </span>
                {index < STEP_ORDER.length - 1 && (
                  <span className={`mx-2 h-px flex-1 ${stepIndex > index ? 'bg-indigo-600' : 'bg-slate-800'}`} />
                )}
              </li>
            );
          })}
        </ol>

        {currentStep === 'fetch' && beatTotal > 0 && (
          <div className="mt-4">
            <div className="mb-1 flex justify-between text-xs text-slate-400">
              <span>Finding footage for each beat</span>
              <span>
                {beatDone}/{beatTotal}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all"
                style={{ width: `${(beatDone / beatTotal) * 100}%` }}
              />
            </div>
          </div>
        )}

        {currentStep === 'vo_conform' && stallSeconds >= 20 && (
          <p className="mt-3 text-xs text-amber-400">
            Transcribing your voiceover - the first VO run downloads the Whisper
            model (~150 MB), so this step can take a few minutes once.
          </p>
        )}
      </div>

      <div className="card">
        <div
          ref={feedRef}
          className="h-64 overflow-y-auto rounded-lg bg-slate-950/80 p-3 font-mono text-[11px] leading-relaxed text-slate-400"
        >
          {logLines.map((event) => (
            <div key={event.seq} className={event.type === 'step' ? 'text-indigo-300' : event.level === 'WARNING' || event.level === 'ERROR' ? 'text-amber-300' : ''}>
              {event.type === 'step' ? `> ${event.label}` : event.message}
            </div>
          ))}
          {logLines.length === 0 && <div>Starting up...</div>}
        </div>
      </div>

      <div className="flex justify-end">
        {confirmCancel ? (
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-400">Stop this run?</span>
            <button className="btn-danger" onClick={() => api.cancelRun(runId)}>
              Yes, stop
            </button>
            <button className="btn-secondary" onClick={() => setConfirmCancel(false)}>
              Keep going
            </button>
          </div>
        ) : (
          <button className="btn-secondary" onClick={() => setConfirmCancel(true)}>
            <OctagonX className="h-4 w-4" /> Cancel
          </button>
        )}
      </div>
    </div>
  );
}
