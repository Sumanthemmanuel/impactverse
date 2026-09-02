import React from 'react'

/**
 * Badge — status / domain / category chip
 *
 * Props:
 *   variant: 'status' | 'domain' | 'default'
 *   status:  'new' | 'in-progress' | 'resolved' | 'duplicate'   (when variant='status')
 *   size:    'sm' | 'md'
 */

const statusStyles = {
  'new':         'bg-primary-50 text-primary-700 border-primary-200',
  'in-progress': 'bg-amber-50 text-amber-700 border-amber-200',
  'resolved':    'bg-emerald-50 text-emerald-700 border-emerald-200',
  'duplicate':   'bg-gray-100 text-gray-600 border-gray-200',
}

const statusDots = {
  'new':         'bg-primary-500',
  'in-progress': 'bg-amber-500',
  'resolved':    'bg-emerald-500',
  'duplicate':   'bg-gray-400',
}

const statusLabels = {
  'new':         'New',
  'in-progress': 'In Progress',
  'resolved':    'Resolved',
  'duplicate':   'Duplicate',
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
          statusStyles[status] ?? statusStyles['new'],
          sizes[size],
          className,
        ].join(' ')}
      >
        <span
          className={[
            'w-1.5 h-1.5 rounded-full shrink-0',
            statusDots[status] ?? statusDots['new'],
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
