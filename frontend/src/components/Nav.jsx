import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useTranslation } from '../i18n.js'

export default function Nav() {
  const { t, lang, setLang } = useTranslation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const links = [
    { to: '/citizen',    label: t('nav.citizen') },
    { to: '/university', label: t('nav.university') },
    { to: '/admin',      label: t('nav.admin') },
  ]

  return (
    <>
      {/* Top utility bar — govt style */}
      <div className="bg-primary-900 text-primary-200 text-xs py-1.5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd"/>
              </svg>
              Government of Jharkhand Initiative
            </span>
            <span className="hidden sm:block text-primary-400">|</span>
            <span className="hidden sm:block">SIH 2026 — Problem Management Platform</span>
          </div>
          {/* Language toggle */}
          <div className="flex items-center gap-1 bg-primary-800 rounded-full px-1 py-0.5">
            <button
              onClick={() => setLang('en')}
              className={`px-2.5 py-0.5 rounded-full text-xs font-medium transition-colors ${lang === 'en' ? 'bg-white text-primary-900' : 'hover:text-white'}`}
            >
              EN
            </button>
            <button
              onClick={() => setLang('hi')}
              className={`px-2.5 py-0.5 rounded-full text-xs font-medium transition-colors ${lang === 'hi' ? 'bg-white text-primary-900' : 'hover:text-white'}`}
            >
              हिं
            </button>
          </div>
        </div>
      </div>

      {/* Main navbar */}
      <header className="sticky top-0 z-50 bg-white border-b border-surface-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex h-16 items-center justify-between">

            {/* Logo + brand */}
            <NavLink to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064" />
                </svg>
              </div>
              <div>
                <div className="text-base font-bold text-ink leading-none">{t('nav.brand')}</div>
                <div className="text-[10px] text-ink-subtle leading-none mt-0.5 hidden sm:block">{t('nav.tagline')}</div>
              </div>
            </NavLink>

            {/* Desktop nav */}
            <nav className="hidden md:flex items-center gap-1">
              {links.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    [
                      'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150',
                      isActive
                        ? 'bg-primary-600 text-white shadow-sm'
                        : 'text-ink-muted hover:text-ink hover:bg-surface-muted',
                    ].join(' ')
                  }
                >
                  {label}
                </NavLink>
              ))}
            </nav>

            {/* Mobile hamburger */}
            <button
              className="md:hidden p-2 rounded-lg text-ink-muted hover:bg-surface-muted"
              onClick={() => setMobileOpen(o => !o)}
              aria-label="Toggle menu"
            >
              {mobileOpen ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>

          {/* Mobile drawer */}
          {mobileOpen && (
            <div className="md:hidden border-t border-surface-border py-3 space-y-1 pb-4">
              {links.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    [
                      'block px-4 py-2.5 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary-600 text-white'
                        : 'text-ink-muted hover:text-ink hover:bg-surface-muted',
                    ].join(' ')
                  }
                >
                  {label}
                </NavLink>
              ))}
            </div>
          )}
        </div>
      </header>
    </>
  )
}
