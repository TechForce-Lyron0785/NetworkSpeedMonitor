import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

interface Sample { time: string; download: number; upload: number; }
interface DayData { date: string; samples: Sample[]; }
interface WeekData { days: DayData[]; }

// Mock data for 7 days
const generateMockSamples = (): Sample[] => {
  const samples = [];
  for (let hour = 0; hour < 24; hour++) {
    for (let minute = 0; minute < 60; minute += 5) {
      // Simulate a speed pattern: lower in evening
      const speedBase = 80 - (hour >= 18 ? 40 : 0) + Math.sin(hour) * 10;
      const download = Math.max(5, speedBase + (Math.random() * 20 - 10));
      const upload = download * 0.3;
      samples.push({
        time: `${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}`,
        download: parseFloat(download.toFixed(1)),
        upload: parseFloat(upload.toFixed(1)),
      });
    }
  }
  // Return only every 12th sample to reduce data (minute resolution)
  return samples.filter((_, idx) => idx % 12 === 0);
};

const DailyGraph = ({ date, samples }: DayData) => {
  if (!samples || samples.length === 0) {
    return <div className="graph-placeholder">No data for {date}</div>;
  }
  return (
    <div className="daily-graph">
      <h3>{date}</h3>
      <ResponsiveContainer width="100%" height={150}>
        <LineChart data={samples}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="download"
            stroke="#8884d8"
            name="Download (Mbps)"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="upload"
            stroke="#82ca9d"
            name="Upload (Mbps)"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const WeeklyStack = () => {
  const [weekData, setWeekData] = useState<WeekData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error] = useState(null);

  useEffect(() => {
    // Simulate API call (will later be replaced with real fetch)
    const mockWeek: DayData[] = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - startDate.getDay()); // go to Monday
    for (let i = 0; i < 7; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      const dateStr = date.toISOString().slice(0, 10);
      mockWeek.push({
        date: dateStr,
        samples: generateMockSamples(),
      });
    }
    setTimeout(() => {
      setWeekData({ days: mockWeek });
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="weekly-stack">
      <h2>Weekly Speed Trend (Last 7 Days)</h2>
      {weekData?.days.map((day) => (
        <DailyGraph key={day.date} date={day.date} samples={day.samples} />
      ))}
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <h1>Network Speed Monitor</h1>
        <p>Your true speed, not your tunnel speed.</p>
      </header>
      <main>
        <WeeklyStack />
      </main>
      <footer>
        <p>
          Data refreshes automatically every minute. Poller running in
          background.
        </p>
      </footer>
    </div>
  );
}

export default App;
