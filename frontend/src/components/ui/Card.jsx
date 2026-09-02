import React from 'react'

/**
 * Card — shared surface container
 *
 * Props:
 *   hover: bool — enables lift-on-hover shadow
 *   padding: 'sm' | 'md' | 'lg' | 'none'
 *   + all native <div> props
 */

const paddings = {
  none: '',
  sm:   'p-4',
  md:   'p-6',
  lg:   'p-8',
}

export default function Card({
  hover = false,
  padding = 'md',
  children,
  className = '',
  ...props
}) {
  return (
    <div
      className={[
        'bg-surface-card rounded-2xl shadow-card border border-surface-border',
        hover ? 'transition-shadow duration-200 hover:shadow-card-hover cursor-pointer' : '',
        paddings[padding],
        className,
      ].join(' ')}
      {...props}
    >
      {children}
    </div>
  )
}

/**
 * CardHeader — optional sub-component for consistent title rows
 */
export function CardHeader({ title, subtitle, action, className = '' }) {
  return (
    <div className={['flex items-start justify-between gap-4 mb-4', className].join(' ')}>
      <div>
        {title && <h3 className="text-ink font-semibold">{title}</h3>}
        {subtitle && <p className="text-ink-muted text-sm mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  )
}
