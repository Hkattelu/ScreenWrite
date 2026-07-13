import { useEffect, useState } from 'react';
import { CheckCircle2, Eraser, KeyRound, Loader2, XCircle } from 'lucide-react';
import { api } from '../api';
import type { SettingsPayload } from '../types';

type KeyTestState = { testing: boolean; ok?: boolean; message?: string };

function KeyField({
  label,
  masked,
  hint,
  onSave,
  onTest,
  testState,
}: {
  label: string;
  masked: string | null;
  hint: string;
  onSave: (value: string) => void;
  onTest: (value?: string) => void;
  testState: KeyTestState;
}) {
  const [value, setValue] = useState('');

  return (
    <div>
      <label className="label">{label}</label>
      <div className="flex gap-2">
        <input
          className="input"
          type="password"
          placeholder={masked ? `Configured (${masked}) - paste to replace` : 'Paste your key'}
          value={value}
          onChange={(event) => setValue(event.target.value)}
        />
        <button
          className="btn-secondary shrink-0"
          onClick={() => {
            if (value.trim()) onSave(value.trim());
            onTest(value.trim() || undefined);
            setValue('');
          }}
          disabled={testState.testing || (!value.trim() && !masked)}
        >
          {testState.testing ? <Loader2 className="h-4 w-4 animate-spin" /> : <KeyRound className="h-4 w-4" />}
          {value.trim() ? 'Save & test' : 'Test'}
        </button>
      </div>
      {testState.ok !== undefined && !testState.testing && (
        <p className={`mt-1 flex items-center gap-1 text-xs ${testState.ok ? 'text-emerald-400' : 'text-rose-400'}`}>
          {testState.ok ? <CheckCircle2 className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
          {testState.message}
        </p>
      )}
      <p className="mt-1 text-xs text-slate-500">{hint}</p>
    </div>
  );
}

export default function Settings() {
  const [settings, setSettings] = useState<SettingsPayload | null>(null);
  const [geminiTest, setGeminiTest] = useState<KeyTestState>({ testing: false });
  const [pexelsTest, setPexelsTest] = useState<KeyTestState>({ testing: false });
  const [cacheMessage, setCacheMessage] = useState('');

  useEffect(() => {
    api.getSettings().then(setSettings).catch(() => undefined);
  }, []);

  const saveKey = async (provider: 'gemini' | 'pexels', value: string) => {
    const updated = await api.putSettings({ keys: { [provider]: value } });
    setSettings(updated);
  };

  const testKey = async (
    provider: 'gemini' | 'pexels',
    setState: (s: KeyTestState) => void,
    key?: string,
  ) => {
    setState({ testing: true });
    try {
      const result = await api.testKey(provider, key);
      setState({ testing: false, ok: result.ok, message: result.message });
    } catch (error) {
      setState({ testing: false, ok: false, message: String(error) });
    }
  };

  if (!settings) {
    return <div className="card text-sm text-slate-400">Loading settings...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="card space-y-5">
        <h2 className="text-sm font-semibold text-slate-300">API keys</h2>
        <KeyField
          label="Gemini API key"
          masked={settings.gemini_key}
          hint="Powers game-entity matching. Free at aistudio.google.com/apikey"
          onSave={(value) => saveKey('gemini', value)}
          onTest={(key) => testKey('gemini', setGeminiTest, key)}
          testState={geminiTest}
        />
        <KeyField
          label="Pexels API key (optional)"
          masked={settings.pexels_key}
          hint="Adds stock footage for non-game beats. Free at pexels.com/api"
          onSave={(value) => saveKey('pexels', value)}
          onTest={(key) => testKey('pexels', setPexelsTest, key)}
          testState={pexelsTest}
        />
      </div>

      <div className="card space-y-3">
        <h2 className="text-sm font-semibold text-slate-300">Storage</h2>
        <p className="text-xs text-slate-500">
          Downloaded footage: <span className="font-mono">{settings.defaults.media_dir}</span>
        </p>
        <div className="flex items-center gap-3">
          <button
            className="btn-secondary"
            onClick={async () => {
              try {
                await api.clearCache();
                setCacheMessage('Caches cleared - the next run refetches everything.');
              } catch (error) {
                setCacheMessage(String(error));
              }
            }}
          >
            <Eraser className="h-4 w-4" /> Clear caches & game library
          </button>
          {cacheMessage && <span className="text-xs text-slate-400">{cacheMessage}</span>}
        </div>
      </div>
    </div>
  );
}
