import { useCallback, useEffect, useState } from 'react';
import { Clapperboard, Settings as SettingsIcon } from 'lucide-react';
import { api } from './api';
import type { RunRequest } from './types';
import Home from './screens/Home';
import Progress from './screens/Progress';
import Report from './screens/Report';
import Settings from './screens/Settings';

type View = 'home' | 'progress' | 'report' | 'settings';

export default function App() {
  const [view, setView] = useState<View>('home');
  const [runId, setRunId] = useState<string | null>(null);
  const [lastRequest, setLastRequest] = useState<RunRequest | null>(null);
  const [startError, setStartError] = useState<string | null>(null);

  // Reattach: if a run is already active (window reloaded), jump to Progress.
  useEffect(() => {
    api
      .currentRun()
      .then((snap) => {
        if (snap.state === 'running' && snap.run_id) {
          setRunId(snap.run_id);
          setView('progress');
        }
      })
      .catch(() => undefined);
  }, []);

  const startRun = useCallback(async (payload: RunRequest) => {
    setStartError(null);
    try {
      const { run_id } = await api.startRun(payload);
      setLastRequest(payload);
      setRunId(run_id);
      setView('progress');
    } catch (error) {
      setStartError(error instanceof Error ? error.message : String(error));
    }
  }, []);

  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-5">
      <header className="mb-6 flex items-center justify-between">
        <button
          className="flex items-center gap-2 text-lg font-bold text-slate-100"
          onClick={() => view !== 'progress' && setView('home')}
        >
          <Clapperboard className="h-6 w-6 text-indigo-400" />
          ScreenWrite
        </button>
        {view !== 'progress' && (
          <button
            className="btn-secondary"
            onClick={() => setView(view === 'settings' ? 'home' : 'settings')}
          >
            <SettingsIcon className="h-4 w-4" />
            {view === 'settings' ? 'Back' : 'Settings'}
          </button>
        )}
      </header>

      <main className="flex-1">
        {view === 'home' && (
          <Home onStart={startRun} startError={startError} lastRequest={lastRequest} />
        )}
        {view === 'progress' && runId && (
          <Progress
            runId={runId}
            onFinished={() => setView('report')}
            onCancelled={() => setView('home')}
          />
        )}
        {view === 'report' && runId && (
          <Report runId={runId} onRunAgain={() => setView('home')} />
        )}
        {view === 'settings' && <Settings />}
      </main>
    </div>
  );
}
