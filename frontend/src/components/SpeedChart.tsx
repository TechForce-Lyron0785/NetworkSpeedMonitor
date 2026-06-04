import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { SpeedPoint, WorstWindow } from '../api';

interface SpeedChartProps {
  samples: SpeedPoint[];
  height?: number;
  compact?: boolean;
  worst?: WorstWindow | null;
  yMax?: number;
}

interface TooltipPayloadEntry {
  name?: string;
  value?: number | string;
  color?: string;
  dataKey?: string | number;
}

interface ChartTooltipProps {
  active?: boolean;
  label?: string | number;
  payload?: TooltipPayloadEntry[];
}

function ChartTooltip({ active, label, payload }: ChartTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__time">{label}</div>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="chart-tooltip__row">
          <span className="chart-tooltip__dot" style={{ background: entry.color }} />
          <span className="chart-tooltip__label">{entry.name}</span>
          <span className="chart-tooltip__value">
            {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value} Mbps
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * Compute a 15-minute window's end label, used to shade the worst period.
 */
function windowEnd(start: string): string {
  const [h, m] = start.split(':').map(Number);
  const total = h * 60 + m + 15;
  const eh = Math.floor((total % 1440) / 60);
  const em = total % 60;
  return `${String(eh).padStart(2, '0')}:${String(em).padStart(2, '0')}`;
}

export function SpeedChart({
  samples,
  height = 280,
  compact = false,
  worst = null,
  yMax,
}: SpeedChartProps) {
  if (!samples || samples.length === 0) {
    return <div className="chart-empty">No samples collected</div>;
  }

  const peak = Math.max(...samples.map((s) => Math.max(s.download, s.upload ?? 0)));
  const domainMax = yMax ?? Math.max(20, Math.ceil((peak * 1.15) / 10) * 10);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={samples} margin={{ top: 8, right: 12, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="dlFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.45} />
            <stop offset="100%" stopColor="#22d3ee" stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="ulFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#a78bfa" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.12)" vertical={false} />
        <XAxis
          dataKey="time"
          tick={{ fontSize: compact ? 9 : 11, fill: '#94a3b8' }}
          interval="preserveStartEnd"
          minTickGap={compact ? 24 : 36}
          tickLine={false}
          axisLine={{ stroke: 'rgba(148,163,184,0.2)' }}
        />
        <YAxis
          domain={[0, domainMax]}
          tick={{ fontSize: compact ? 9 : 11, fill: '#94a3b8' }}
          width={48}
          tickLine={false}
          axisLine={false}
          unit=""
        />
        <Tooltip content={<ChartTooltip />} />
        {worst && (
          <ReferenceArea
            x1={worst.window_start}
            x2={windowEnd(worst.window_start)}
            fill="#f87171"
            fillOpacity={0.12}
            stroke="#f87171"
            strokeOpacity={0.4}
            strokeDasharray="4 4"
          />
        )}
        <Area
          type="monotone"
          dataKey="download"
          name="Download"
          stroke="#22d3ee"
          strokeWidth={2}
          fill="url(#dlFill)"
          dot={false}
          activeDot={{ r: 4 }}
          isAnimationActive={!compact}
        />
        <Area
          type="monotone"
          dataKey="upload"
          name="Upload"
          stroke="#a78bfa"
          strokeWidth={2}
          fill="url(#ulFill)"
          dot={false}
          activeDot={{ r: 4 }}
          isAnimationActive={!compact}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
