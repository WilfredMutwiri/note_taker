const tones = {
  neutral: 'bg-surface-muted text-ink-muted border-border',
  primary: 'bg-primary-50 text-primary-700 border-primary-200',
  health: 'bg-health-50 text-health-700 border-health-200',
}

export default function Badge({ tone = 'neutral', className = '', children }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${tones[tone]} ${className}`}
    >
      {children}
    </span>
  )
}
