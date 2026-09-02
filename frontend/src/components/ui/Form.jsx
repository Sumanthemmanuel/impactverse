import React from 'react'

/**
 * Select — shared styled dropdown
 */
export default function Select({ label, className = '', ...props }) {
  return (
    <select
      className={[
        'w-full rounded-xl border border-surface-border bg-white px-3 py-2 text-sm text-ink',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className,
      ].join(' ')}
      {...props}
    />
  )
}

/**
 * Input — shared styled text input / textarea base
 */
export function Input({ className = '', ...props }) {
  return (
    <input
      className={[
        'w-full rounded-xl border border-surface-border bg-white px-3 py-2 text-sm text-ink',
        'placeholder:text-ink-subtle',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className,
      ].join(' ')}
      {...props}
    />
  )
}

/**
 * Textarea — shared styled textarea
 */
export function Textarea({ className = '', ...props }) {
  return (
    <textarea
      className={[
        'w-full rounded-xl border border-surface-border bg-white px-3 py-2 text-sm text-ink',
        'placeholder:text-ink-subtle resize-none',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className,
      ].join(' ')}
      {...props}
    />
  )
}

/**
 * Label — shared form label
 */
export function Label({ children, required, className = '', ...props }) {
  return (
    <label
      className={['block text-sm font-medium text-ink mb-1.5', className].join(' ')}
      {...props}
    >
      {children}
      {required && <span className="text-red-500 ml-0.5">*</span>}
    </label>
  )
}

/**
 * FormField — label + input wrapper with optional error
 */
export function FormField({ label, required, error, children, className = '' }) {
  return (
    <div className={['space-y-1', className].join(' ')}>
      {label && <Label required={required}>{label}</Label>}
      {children}
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  )
}
