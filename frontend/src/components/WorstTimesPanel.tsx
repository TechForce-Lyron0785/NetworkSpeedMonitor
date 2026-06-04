import type { WorstWindow } from '../api';

interface WorstTimesPanelProps {
  windows: WorstWindow[];
  loading: boolean;
}

function severity(avg: number, slowest: number): 'critical' | 'poor' | 'fair' {
  if (avg <= slowest * 1.1) return 'critical';
  if (avg <= slowest * 1.4) return 'poor';
  return 'fair';
}

export function WorstTimesPanel({ windows, loading }: WorstTimesPanelProps) {
  if (loading) {
    return (
      <div className="panel worst-panel">
        <h3 className="panel__title">Worst 15-minute windows</h3>
        <div className="skeleton-list">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton-row" />
          ))}
        </div>
      </div>
    );
  }

  if (!windows.length) {
    return (
      <div className="panel worst-panel">
        <h3 className="panel__title">Worst 15-minute windows</h3>
        <p className="panel__empty">No slow periods detected for this day.</p>
      </div>
    );
  }

  const slowest = windows[0]?.avg_download ?? 0;

  return (
    <div className="panel worst-panel">
      <h3 className="panel__title">
        Worst 15-minute windows
        <span className="panel__badge">{windows.length}</span>
      </h3>
      <ul className="worst-list">
        {windows.map((w, idx) => {
          const sev = severity(w.avg_download, slowest);
          return (
            <li key={w.window_start} className={`worst-item worst-item--${sev}`}>
              <span className="worst-item__rank">#{idx + 1}</span>
              <div className="worst-item__main">
                <span className="worst-item__time">
                  {w.window_start} – {addMinutes(w.window_start, 15)}
                </span>
                <span className="worst-item__meta">
                  min {w.min_download} Mbps · {w.samples} sample{w.samples === 1 ? '' : 's'}
                </span>
              </div>
              <span className="worst-item__avg">
                {w.avg_download}
                <small>Mbps avg</small>
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function addMinutes(start: string, minutes: number): string {
  const [h, m] = start.split(':').map(Number);
  const total = h * 60 + m + minutes;
  const eh = Math.floor((total % 1440) / 60);
  const em = total % 60;
  return `${String(eh).padStart(2, '0')}:${String(em).padStart(2, '0')}`;
}
