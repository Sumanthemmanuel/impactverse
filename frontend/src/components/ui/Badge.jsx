import React from 'react'

/**
 * Badge — status / domain / category chip
 *
 * Props:
 *   variant: 'status' | 'domain' | 'default'
 *   status:  'Submitted' | 'Assigned to University' | 'In Progress' | 'Resolved'
 *   size:    'sm' | 'md'
 */

const statusStyles = {
  'Submitted':              'bg-primary-50 text-primary-700 border-primary-200',
  'Assigned to University': 'bg-blue-50 text-blue-700 border-blue-200',
  'In Progress':            'bg-amber-50 text-amber-700 border-amber-200',
  'Resolved':               'bg-emerald-50 text-emerald-700 border-emerald-200',
}

const statusDots = {
  'Submitted':              'bg-primary-500',
  'Assigned to University': 'bg-blue-500',
  'In Progress':            'bg-amber-500',
  'Resolved':               'bg-emerald-500',
}

const statusLabels = {
  'Submitted':              'Submitted',
  'Assigned to University': 'Assigned to University',
  'In Progress':            'In Progress',
  'Resolved':               'Resolved',
}

const sizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
}

export default function Badge({
  variant = 'default',
  status,
  size = 'md',
  children,
  className = '',
}) {
  if (variant === 'status' && status) {
    return (
      <span
        className={[
          'inline-flex items-center gap-1.5 font-medium rounded-full border',
          statusStyles[status] ?? statusStyles['Submitted'],
          sizes[size],
          className,
        ].join(' ')}
      >
        <span
          className={[
            'w-1.5 h-1.5 rounded-full shrink-0',
            statusDots[status] ?? statusDots['Submitted'],
          ].join(' ')}
        />
        {statusLabels[status] ?? status}
      </span>
    )
  }

  return (
    <span
      className={[
        'inline-flex items-center font-medium rounded-full border',
        'bg-surface-muted text-ink-muted border-surface-border',
        sizes[size],
        className,
      ].join(' ')}
    >
      {children}
    </span>
  )
}
