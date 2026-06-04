import axios from 'axios';

// The FastAPI server runs locally on port 8000 (see backend/api/main.py).
// Allow overriding via Vite env for flexible deployments.
const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') ||
  'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});

export interface SpeedPoint {
  time: string;
  download: number;
  upload: number;
}

export interface WorstWindow {
  window_start: string;
  avg_download: number;
  min_download: number;
  samples: number;
}

export interface DailyData {
  date: string;
  samples: SpeedPoint[];
  worst_15min: WorstWindow | null;
}

export interface WeekData {
  week_start: string;
  days: DailyData[];
}

export interface WorstTimesResponse {
  period: string;
  date?: string;
  worst_windows: WorstWindow[];
}

export interface HealthData {
  status: string;
  last_sample: string | null;
  total_samples: number;
}

export function getDaily(date: string, signal?: AbortSignal) {
  return api
    .get<DailyData>('/daily', { params: { date }, signal })
    .then((r) => r.data);
}

export function getWeek(startDate: string, signal?: AbortSignal) {
  return api
    .get<WeekData>('/week', { params: { start_date: startDate }, signal })
    .then((r) => r.data);
}

export function getWorstTimes(date: string, signal?: AbortSignal) {
  return api
    .get<WorstTimesResponse>('/worst-times', {
      params: { period: 'day', date },
      signal,
    })
    .then((r) => r.data);
}

export function getHealth(signal?: AbortSignal) {
  return api.get<HealthData>('/health', { signal }).then((r) => r.data);
}

// ---- Derived statistics helpers ----

export interface DailyStats {
  avgDownload: number;
  avgUpload: number;
  peakDownload: number;
  minDownload: number;
  sampleCount: number;
}

export function computeStats(samples: SpeedPoint[]): DailyStats {
  if (!samples.length) {
    return {
      avgDownload: 0,
      avgUpload: 0,
      peakDownload: 0,
      minDownload: 0,
      sampleCount: 0,
    };
  }
  const downloads = samples.map((s) => s.download);
  const uploads = samples.map((s) => s.upload ?? 0);
  const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0);
  return {
    avgDownload: round(sum(downloads) / downloads.length),
    avgUpload: round(sum(uploads) / uploads.length),
    peakDownload: round(Math.max(...downloads)),
    minDownload: round(Math.min(...downloads)),
    sampleCount: samples.length,
  };
}

export function round(n: number, digits = 1): number {
  const f = 10 ** digits;
  return Math.round(n * f) / f;
}

export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    if (err.code === 'ERR_NETWORK') {
      return 'Cannot reach the API server at ' + API_BASE + '. Is the poller running?';
    }
    return err.response?.statusText || err.message;
  }
  return err instanceof Error ? err.message : String(err);
}

export { API_BASE };
