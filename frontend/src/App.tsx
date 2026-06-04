import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './App.css';

const API_BASE = 'http://localhost:8000';

interface SpeedPoint {
  time: string;
  download: number;
  upload: number;
}

interface DailyData {
  date: string;
  samples: SpeedPoint[];
}

interface WeekData {
  week_start: string;
  days: DailyData[];
}

interface WorstWindow {
  window_start: string;
  avg_download: number;
  min_download: number;
}

interface DailyGraphProps { date: string; samples: SpeedPoint[]; }
interface WeeklyStackProps { startDate: string; onLoading?: (v: boolean) => void; onError?: (msg: string) => void; }

interface HealthData {
  last_sample: string;
  total_samples: number;
}

const DailyGraph = ({ date, samples }: DailyGraphProps) => {
  if (!samples || samples.length === 0) {
    return <div className="graph-placeholder">No data for {date}</div>;
  }
  return (
    <div className="daily-graph">
      <h3>{date}</h3>
      <ResponsiveContainer width="100%" height={150}>
        <LineChart data={samples}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="download" stroke="#8884d8" name="Download (Mbps)" dot={false} />
          <Line type="monotone" dataKey="upload" stroke="#82ca9d" name="Upload (Mbps)" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const WeeklyStack = ({ startDate, onLoading, onError }: WeeklyStackProps) => {
  const [weekData, setWeekData] = useState<WeekData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    onLoading?.(true);
    axios
      .get(`${API_BASE}/week`, {
        params: { start_date: startDate },
        signal: controller.signal,
      })
      .then(response => {
        if (!cancelled) {
          setLoading(true);
          setWeekData(response.data);
          setError(null);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setLoading(true);
          const msg = err instanceof Error ? err.message : String(err);
          setError(msg);
          onError?.(msg);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
          onLoading?.(false);
        }
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [startDate, onLoading, onError]);

  if (loading) return <div className="loading">Loading weekly data...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!weekData) return null;

  return (
    <div className="weekly-stack">
      <h2>Weekly Speed Trend (Last 7 Days from {weekData.week_start})</h2>
      {weekData.days.map(day => (
        <DailyGraph key={day.date} date={day.date} samples={day.samples} />
      ))}
    </div>
  );
};

const WorstTimePanel = ({ date }: { date: string }) => {
  const [worst, setWorst] = useState<WorstWindow[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWorst = async () => {
      try {
        const response = await axios.get(`${API_BASE}/worst-times`, {
          params: { period: 'day', date: date }
        });
        setWorst(response.data.worst_windows);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchWorst();
  }, [date]);

  if (loading) return <div>Analyzing worst times...</div>;
  if (!worst || worst.length === 0) return null;
  return (
    <div className="worst-panel">
      <h3>⚠️ Worst 15‑minute periods today</h3>
      <ul>
        {worst.map((w, idx) => (
          <li key={idx}>
            {w.window_start}: {w.avg_download} Mbps avg (min {w.min_download} Mbps)
          </li>
        ))}
      </ul>
    </div>
  );
};

const HealthIndicator = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/health`);
        setHealth(res.data);
      } catch {
        setHealth(null);
      }
    }, 10000);
    return () => clearInterval(interval);
  }, []);
  if (!health) return <div className="health-error">Poller unreachable</div>;
  return (
    <div className="health-ok">
      ✅ Poller active | Last sample: {new Date(health.last_sample).toLocaleString()} | Total samples: {health.total_samples}
    </div>
  );
};

function App() {
  const [startDate, setStartDate] = useState<string>(() => {
    const today = new Date();
    const diff = today.getDay() === 0 ? 6 : today.getDay() - 1;
    const monday = new Date(today);
    monday.setDate(today.getDate() - diff);
    return monday.toISOString().slice(0, 10);
  });
  const [, setGlobalLoading] = useState(false);

  return (
    <div className="App">
      <header className="app-header">
        <h1>Network Speed Monitor</h1>
        <p>Your true speed, not your tunnel speed.</p>
        <HealthIndicator />
        <div className="controls">
          <label>Week starting Monday: </label>
          <input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
          />
          <button onClick={() => window.location.reload()}>Refresh</button>
        </div>
      </header>
      <main>
        <WorstTimePanel date={new Date().toISOString().slice(0,10)} />
        <WeeklyStack
          startDate={startDate}
          onLoading={setGlobalLoading}
          onError={(err) => console.error(err)}
        />
      </main>
      <footer>
        <p>Data refreshes automatically every minute.</p>
      </footer>
    </div>
  );
}

export default App;