import { useCallback, useEffect, useMemo, useState } from 'react';
import './App.css';
import {
  computeStats,
  getDaily,
  getErrorMessage,
  getHealth,
  getWeek,
  getWorstTimes,
} from './api';
import type { DailyData, HealthData, WeekData, WorstWindow } from './api';
import { SpeedChart } from './components/SpeedChart';
import { StatCard } from './components/StatCard';
import { WorstTimesPanel } from './components/WorstTimesPanel';
import { HealthBadge } from './components/HealthBadge';

type View = 'daily' | 'weekly';

const REFRESH_MS = 60_000;
const HEALTH_MS = 10_000;

function toLocalISODate(d: Date): string {
  const tz = d.getTimezoneOffset() * 60_000;
  return new Date(d.getTime() - tz).toISOString().slice(0, 10);
}

function mondayOf(d: Date): string {
  const day = d.getDay() === 0 ? 6 : d.getDay() - 1;
  const monday = new Date(d);
  monday.setDate(d.getDate() - day);
  return toLocalISODate(monday);
}

function prettyDate(iso: string): string {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
}

function App() {
  const today = useMemo(() => toLocalISODate(new Date()), []);
  const [view, setView] = useState<View>('daily');
  const [selectedDate, setSelectedDate] = useState<string>(today);
  const [weekStart, setWeekStart] = useState<string>(() => mondayOf(new Date()));
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const [health, setHealth] = useState<HealthData | null>(null);
  const [healthDown, setHealthDown] = useState<boolean>(false);

  interface FetchResult<T> { key: string; data: T | null; error: string | null; }
  const dailyKey = view === 'daily' ? `${selectedDate}:${refreshKey}` : '';
  const [dailyResult, setDailyResult] = useState<FetchResult<DailyData>>({ key: '', data: null, error: null });
  const dailyLoading = view === 'daily' && dailyResult.key !== dailyKey;
  const daily = dailyResult.data;
  const dailyError = dailyResult.error;

  const worstKey = dailyKey;
  const [worstResult, setWorstResult] = useState<FetchResult<WorstWindow[]>>({ key: '', data: null, error: null });
  const worstLoading = view === 'daily' && worstResult.key !== worstKey;
  const worst = worstResult.data ?? [];

  const weekKey = view === 'weekly' ? `${weekStart}:${refreshKey}` : '';
  const [weekResult, setWeekResult] = useState<FetchResult<WeekData>>({ key: '', data: null, error: null });
  const weekLoading = view === 'weekly' && weekResult.key !== weekKey;
  const week = weekResult.data;
  const weekError = weekResult.error;

  const refreshNow = useCallback(() => setRefreshKey((k) => k + 1), []);

  // Health polling
  useEffect(() => {
    const controller = new AbortController();
    const poll = async () => {
      try {
        const h = await getHealth(controller.signal);
        setHealth(h);
        setHealthDown(false);
      } catch {
        setHealthDown(true);
      }
    };
    poll();
    const id = setInterval(poll, HEALTH_MS);
    return () => {
      clearInterval(id);
      controller.abort();
    };
  }, [refreshKey]);

  // Daily + worst-times fetch
  useEffect(() => {
    if (view !== 'daily') return;
    const key = `${selectedDate}:${refreshKey}`;
    const controller = new AbortController();

    getDaily(selectedDate, controller.signal)
      .then((d) => !controller.signal.aborted && setDailyResult({ key, data: d, error: null }))
      .catch((err) => !controller.signal.aborted && setDailyResult({ key, data: null, error: getErrorMessage(err) }));

    getWorstTimes(selectedDate, controller.signal)
      .then((d) => !controller.signal.aborted && setWorstResult({ key, data: d.worst_windows, error: null }))
      .catch(() => !controller.signal.aborted && setWorstResult({ key, data: [], error: null }));

    return () => controller.abort();
  }, [view, selectedDate, refreshKey]);

  // Weekly fetch
  useEffect(() => {
    if (view !== 'weekly') return;
    const key = `${weekStart}:${refreshKey}`;
    const controller = new AbortController();

    getWeek(weekStart, controller.signal)
      .then((d) => !controller.signal.aborted && setWeekResult({ key, data: d, error: null }))
      .catch((err) => !controller.signal.aborted && setWeekResult({ key, data: null, error: getErrorMessage(err) }));

    return () => controller.abort();
  }, [view, weekStart, refreshKey]);

  // Auto-refresh timer
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(refreshNow, REFRESH_MS);
    return () => clearInterval(id);
  }, [autoRefresh, refreshNow]);

  const dailyStats = useMemo(
    () => computeStats(daily?.samples ?? []),
    [daily],
  );

  const weekStats = useMemo(() => {
    if (!week) return null;
    const all = week.days.flatMap((d) => d.samples);
    const stats = computeStats(all);
    const activeDays = week.days.filter((d) => d.samples.length > 0).length;
    return { ...stats, activeDays };
  }, [week]);

  return (
    <div className="app">
      <div className="app__bg" aria-hidden />
      <header className="app-header">
        <div className="brand">
          <div className="brand__logo" aria-hidden>
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none">
              <path
                d="M3 17l4-5 4 3 5-7 5 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div className="brand__text">
            <h1>Network Speed Monitor</h1>
            <p>Know your true speed, not your tunnel speed.</p>
          </div>
        </div>
        <HealthBadge health={health} unreachable={healthDown} />
      </header>

      <div className="toolbar">
        <div className="tabs" role="tablist">
          <button
            role="tab"
            aria-selected={view === 'daily'}
            className={`tab ${view === 'daily' ? 'tab--active' : ''}`}
            onClick={() => setView('daily')}
          >
            Daily
          </button>
          <button
            role="tab"
            aria-selected={view === 'weekly'}
            className={`tab ${view === 'weekly' ? 'tab--active' : ''}`}
            onClick={() => setView('weekly')}
          >
            Weekly
          </button>
        </div>

        <div className="toolbar__controls">
          {view === 'daily' ? (
            <label className="field">
              <span>Date</span>
              <input
                type="date"
                value={selectedDate}
                max={today}
                onChange={(e) => setSelectedDate(e.target.value)}
              />
            </label>
          ) : (
            <label className="field">
              <span>Week of (Mon)</span>
              <input
                type="date"
                value={weekStart}
                max={today}
                onChange={(e) => setWeekStart(mondayOf(new Date(e.target.value + 'T00:00:00')))}
              />
            </label>
          )}

          <label className="toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span className="toggle__track"><span className="toggle__thumb" /></span>
            <span className="toggle__label">Auto-refresh</span>
          </label>

          <button className="btn btn--primary" onClick={refreshNow}>
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
              <path
                d="M4 12a8 8 0 0 1 13.7-5.7L20 8M20 4v4h-4M20 12a8 8 0 0 1-13.7 5.7L4 16m0 4v-4h4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <main className="content">
        {view === 'daily' ? (
          <DailyView
            date={selectedDate}
            data={daily}
            loading={dailyLoading}
            error={dailyError}
            stats={dailyStats}
            worst={worst}
            worstLoading={worstLoading}
          />
        ) : (
          <WeeklyView
            data={week}
            loading={weekLoading}
            error={weekError}
            stats={weekStats}
          />
        )}
      </main>

      <footer className="app-footer">
        <span>
          {autoRefresh
            ? 'Live · data refreshes automatically every minute'
            : 'Auto-refresh paused'}
        </span>
        <span className="app-footer__brand">Network Speed Monitor v1.0</span>
      </footer>
    </div>
  );
}

interface DailyViewProps {
  date: string;
  data: DailyData | null;
  loading: boolean;
  error: string | null;
  stats: ReturnType<typeof computeStats>;
  worst: WorstWindow[];
  worstLoading: boolean;
}

function DailyView({ date, data, loading, error, stats, worst, worstLoading }: DailyViewProps) {
  if (error) return <ErrorState message={error} />;

  const hasData = (data?.samples.length ?? 0) > 0;

  return (
    <div className="daily-view">
      <section className="stat-grid">
        <StatCard
          label="Avg download"
          value={stats.avgDownload}
          unit="Mbps"
          tone="download"
          hint={`Peak ${stats.peakDownload} Mbps`}
        />
        <StatCard
          label="Avg upload"
          value={stats.avgUpload}
          unit="Mbps"
          tone="upload"
          hint="Across the day"
        />
        <StatCard
          label="Slowest sample"
          value={stats.minDownload}
          unit="Mbps"
          tone="warn"
          hint={data?.worst_15min ? `Worst window ${data.worst_15min.window_start}` : 'Download low'}
        />
        <StatCard
          label="Samples"
          value={stats.sampleCount}
          tone="neutral"
          hint="Minute resolution"
        />
      </section>

      <section className="panel chart-panel">
        <div className="panel__header">
          <div>
            <h2 className="panel__title">Speed timeline</h2>
            <p className="panel__subtitle">{prettyDate(date)}</p>
          </div>
          <Legend />
        </div>
        {loading && !hasData ? (
          <ChartSkeleton />
        ) : (
          <SpeedChart samples={data?.samples ?? []} worst={data?.worst_15min ?? null} height={300} />
        )}
      </section>

      <WorstTimesPanel windows={worst} loading={worstLoading} />
    </div>
  );
}

interface WeeklyViewProps {
  data: WeekData | null;
  loading: boolean;
  error: string | null;
  stats: (ReturnType<typeof computeStats> & { activeDays: number }) | null;
}

function WeeklyView({ data, loading, error, stats }: WeeklyViewProps) {
  if (error) return <ErrorState message={error} />;

  return (
    <div className="weekly-view">
      <section className="stat-grid">
        <StatCard label="Avg download" value={stats?.avgDownload ?? 0} unit="Mbps" tone="download" hint="7-day average" />
        <StatCard label="Avg upload" value={stats?.avgUpload ?? 0} unit="Mbps" tone="upload" hint="7-day average" />
        <StatCard label="Peak download" value={stats?.peakDownload ?? 0} unit="Mbps" tone="neutral" hint="Best sample" />
        <StatCard label="Active days" value={stats?.activeDays ?? 0} unit="/ 7" tone="warn" hint={`${stats?.sampleCount ?? 0} samples`} />
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <h2 className="panel__title">Weekly trend</h2>
            <p className="panel__subtitle">
              {data ? `Week of ${prettyDate(data.week_start)}` : '7 stacked daily graphs'}
            </p>
          </div>
          <Legend />
        </div>

        {loading && !data ? (
          <div className="week-stack">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="week-row">
                <div className="week-row__label skeleton-block" />
                <div className="week-row__chart"><ChartSkeleton compact /></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="week-stack">
            {data?.days.map((day) => {
              const dayStats = computeStats(day.samples);
              return (
                <div key={day.date} className="week-row">
                  <div className="week-row__label">
                    <span className="week-row__day">{prettyDate(day.date)}</span>
                    {day.samples.length > 0 ? (
                      <span className="week-row__stat">
                        <b>{dayStats.avgDownload}</b> Mbps avg
                      </span>
                    ) : (
                      <span className="week-row__stat week-row__stat--muted">no data</span>
                    )}
                  </div>
                  <div className="week-row__chart">
                    <SpeedChart samples={day.samples} compact height={96} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

function Legend() {
  return (
    <div className="legend">
      <span className="legend__item"><i className="legend__swatch legend__swatch--dl" />Download</span>
      <span className="legend__item"><i className="legend__swatch legend__swatch--ul" />Upload</span>
    </div>
  );
}

function ChartSkeleton({ compact = false }: { compact?: boolean }) {
  return <div className={`chart-skeleton ${compact ? 'chart-skeleton--compact' : ''}`} />;
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="error-state">
      <div className="error-state__icon">!</div>
      <div>
        <h3>Unable to load data</h3>
        <p>{message}</p>
      </div>
    </div>
  );
}

export default App;
