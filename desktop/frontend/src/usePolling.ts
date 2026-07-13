import { useEffect, useRef, useState } from 'react';
import { api } from './api';
import type { RunEvent, RunSnapshot } from './types';

const TERMINAL_STATES = new Set(['succeeded', 'failed', 'cancelled', 'crashed']);

/**
 * Polls /api/run/current with an after_seq cursor, accumulating events.
 * Stops automatically when the run reaches a terminal state.
 */
export function useRunPolling(active: boolean, intervalMs = 750) {
  const [snapshot, setSnapshot] = useState<RunSnapshot | null>(null);
  const [events, setEvents] = useState<RunEvent[]>([]);
  const cursor = useRef(0);
  const runId = useRef<string | null>(null);

  useEffect(() => {
    if (!active) return;
    let cancelled = false;
    let timer: number | undefined;

    const tick = async () => {
      try {
        const snap = await api.currentRun(cursor.current);
        if (cancelled) return;
        if (snap.run_id !== runId.current) {
          // New run: reset the accumulated feed.
          runId.current = snap.run_id;
          cursor.current = 0;
          setEvents([]);
        }
        if (snap.events.length > 0) {
          setEvents((previous) => [...previous, ...snap.events].slice(-1000));
        }
        cursor.current = Math.max(cursor.current, snap.last_seq);
        setSnapshot(snap);
        if (TERMINAL_STATES.has(snap.state)) return; // stop polling
      } catch {
        // Server hiccup: keep trying.
      }
      timer = window.setTimeout(tick, intervalMs);
    };

    tick();
    return () => {
      cancelled = true;
      if (timer !== undefined) window.clearTimeout(timer);
    };
  }, [active, intervalMs]);

  return { snapshot, events };
}
