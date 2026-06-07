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

const API_BASE = 'http://127.0.0.1:8000';

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

const TodayGraph = () => {
  const [todayData, setTodayData] = useState<DailyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchToday = async () => {
      try {
        const today = new Date().toISOString().slice(0, 10);
        const response = await axios.get(`${API_BASE}/daily`, {
          params: { date: today }
        });
        setTodayData(response.data);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setLoading(false);
      }
    };
    fetchToday();
    const interval = setInterval(fetchToday, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading today's data...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!todayData) return null;

  const generateFullTimeRange = () => {
    const fullRange = [];
    for (let h = 0; h < 24; h++) {
      for (let m = 0; m < 60; m += 5) {
        fullRange.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
      }
    }
    return fullRange;
  };

  // Map API data times to nearest 5-minute interval
  const mapTo5MinInterval = (time: string): string => {
    const [hours, minutes] = time.split(':').map(Number);
    const roundedMinutes = Math.round(minutes / 5) * 5;
    const adjustedHours = roundedMinutes === 60 ? hours + 1 : hours;
    const adjustedMinutes = roundedMinutes === 60 ? 0 : roundedMinutes;
    return `${String(adjustedHours % 24).padStart(2, '0')}:${String(adjustedMinutes).padStart(2, '0')}`;
  };

  const mappedSamples = todayData.samples.map(sample => ({
    ...sample,
    time: mapTo5MinInterval(sample.time)
  }));

  const fullTimeRange = generateFullTimeRange();
  const mergedData = fullTimeRange.map(time => {
    const sample = mappedSamples.find(s => s.time === time);
    return sample || { time, download: 0, upload: 0 };
  });

  return (
    <div className="today-graph" style={{ marginBottom: '2rem', backgroundColor: 'rgb(37 63 38 / 41%)' }} key={todayData.date}>
      <h2>Today's Speed Summary - {todayData.date}</h2>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={mergedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }} 
            interval="preserveStartEnd"
            domain={['00:00', '23:55']}
            type="category"
          />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(139, 92, 246, 0.15)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '12px',
              boxShadow: '0 8px 32px rgba(139, 92, 246, 0.2)',
              backdropFilter: 'blur(12px)'
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="download" 
            stroke="var(--primary)" 
            strokeWidth={3}
            name="Download (Mbps)" 
            dot={false} 
            activeDot={{ r: 8 }}
          />
          <Line 
            type="monotone" 
            dataKey="upload" 
            stroke="var(--secondary)" 
            strokeWidth={3}
            name="Upload (Mbps)" 
            dot={false} 
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const DailyGraph = ({ date, samples }: DailyGraphProps) => {
  if (!samples || samples.length === 0) {
    return <div className="graph-placeholder">No data for {date}</div>;
  }

  const generateFullTimeRange = () => {
    const fullRange = [];
    for (let h = 0; h < 24; h++) {
      for (let m = 0; m < 60; m += 5) {
        fullRange.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
      }
    }
    return fullRange;
  };

  // Map API data times to nearest 5-minute interval
  const mapTo5MinInterval = (time: string): string => {
    const [hours, minutes] = time.split(':').map(Number);
    const roundedMinutes = Math.round(minutes / 5) * 5;
    const adjustedHours = roundedMinutes === 60 ? hours + 1 : hours;
    const adjustedMinutes = roundedMinutes === 60 ? 0 : roundedMinutes;
    return `${String(adjustedHours % 24).padStart(2, '0')}:${String(adjustedMinutes).padStart(2, '0')}`;
  };

  const mappedSamples = samples.map(sample => ({
    ...sample,
    time: mapTo5MinInterval(sample.time)
  }));

  const fullTimeRange = generateFullTimeRange();
  const mergedData = fullTimeRange.map(time => {
    const sample = mappedSamples.find(s => s.time === time);
    return sample || { time, download: 0, upload: 0 };
  });

  return (
    <div className="daily-graph">
      <h3>{date}</h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={mergedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 10 }} 
            interval="preserveStartEnd"
            domain={['00:00', '23:55']}
            type="category"
          />
          <YAxis domain={[0, 100]} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(139, 92, 246, 0.15)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '12px',
              boxShadow: '0 8px 32px rgba(139, 92, 246, 0.2)',
              backdropFilter: 'blur(12px)'
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="download" stroke="var(--primary)" strokeWidth={2} name="Download (Mbps)" dot={false} activeDot={{ r: 6 }} />
          <Line type="monotone" dataKey="upload" stroke="var(--secondary)" strokeWidth={2} name="Upload (Mbps)" dot={false} activeDot={{ r: 6 }} />
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
    
    const fetchWeek = () => {
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
    };
    
    fetchWeek();
    const interval = setInterval(fetchWeek, 60000);
    
    return () => {
      cancelled = true;
      controller.abort();
      clearInterval(interval);
    };
  }, [startDate]);

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
    const interval = setInterval(fetchWorst, 60000);
    return () => clearInterval(interval);
  }, [date]);

  if (loading) return <div className="loading">Analyzing worst times...</div>;
  if (!worst || worst.length === 0) return null;
  return (
    <div className="worst-panel">
      <h3>Worst 15-minute periods today</h3>
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
      Poller active | Last sample: {new Date(health.last_sample).toLocaleString()} | Total samples: {health.total_samples}
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
          <label>Week starting Monday:</label>
          <input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
            title="Select week start date"
            aria-label="Select week start date"
          />
        </div>
      </header>
      <main>
        <TodayGraph />
        <WeeklyStack
          startDate={startDate}
          onLoading={setGlobalLoading}
          onError={(err) => console.error(err)}
        />
        <WorstTimePanel date={new Date().toISOString().slice(0,10)} />
      </main>
      <footer>
        <p>Data refreshes automatically every minute.</p>
      </footer>
    </div>
  );
}

export default App;