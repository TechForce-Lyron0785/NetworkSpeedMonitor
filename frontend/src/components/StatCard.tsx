import type { ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: ReactNode;
  unit?: string;
  hint?: string;
  tone?: 'download' | 'upload' | 'warn' | 'neutral';
  icon?: ReactNode;
}

export function StatCard({ label, value, unit, hint, tone = 'neutral', icon }: StatCardProps) {
  return (
    <div className={`stat-card stat-card--${tone}`}>
      <div className="stat-card__head">
        <span className="stat-card__label">{label}</span>
        {icon && <span className="stat-card__icon">{icon}</span>}
      </div>
      <div className="stat-card__value">
        {value}
        {unit && <span className="stat-card__unit">{unit}</span>}
      </div>
      {hint && <div className="stat-card__hint">{hint}</div>}
    </div>
  );
}
