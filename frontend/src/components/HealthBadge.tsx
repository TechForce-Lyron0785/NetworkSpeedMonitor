import type { HealthData } from '../api';

interface HealthBadgeProps {
  health: HealthData | null;
  unreachable: boolean;
}

function relativeTime(iso: string | null): string {
  if (!iso) return 'never';
  const then = new Date(iso.replace(' ', 'T')).getTime();
  if (Number.isNaN(then)) return iso;
  const diffMs = Date.now() - then;
  const min = Math.round(diffMs / 60000);
  if (min < 1) return 'just now';
  if (min < 60) return `${min} min ago`;
  const hrs = Math.round(min / 60);
  if (hrs < 24) return `${hrs} h ago`;
  return `${Math.round(hrs / 24)} d ago`;
}

export function HealthBadge({ health, unreachable }: HealthBadgeProps) {
  if (unreachable || !health) {
    return (
      <div className="health-badge health-badge--down">
        <span className="health-badge__dot" />
        <span className="health-badge__text">Poller unreachable</span>
      </div>
    );
  }
  return (
    <div className="health-badge health-badge--ok">
      <span className="health-badge__dot" />
      <div className="health-badge__text">
        <strong>Poller active</strong>
        <span className="health-badge__meta">
          {health.total_samples.toLocaleString()} samples · last {relativeTime(health.last_sample)}
        </span>
      </div>
    </div>
  );
}
