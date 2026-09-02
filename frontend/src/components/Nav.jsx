import React, { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const NAV_LINKS = [
  { to: '/', hash: '#hero', label: 'Home' },
  { to: '/', hash: '#explore', label: 'Explore' },
  { to: '/', hash: '#how-it-works', label: 'How It Works' },
  { to: '/', hash: '#impact', label: 'Impact' },
  { to: '/', hash: '#partners', label: 'Partners' },
  { to: '/', hash: '#about', label: 'About Us' },
]

export default function Nav() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 30)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    setMobileOpen(false)
  }, [location])

  const scrollTo = (hash) => {
    setMobileOpen(false)
    const el = document.querySelector(hash)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <>
      <a href="#hero" className="skip-link">Skip to main content</a>
      <header
        className={`z-50 transition-all duration-500 fixed top-0 left-0 right-0 ${
          scrolled || location.pathname !== '/'
            ? 'glass-nav scrolled py-3'
            : 'py-5'
        }`}
        style={(!scrolled && location.pathname === '/') ? {
          background: 'transparent',
          backdropFilter: 'none',
          WebkitBackdropFilter: 'none',
        } : undefined}
      >
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6">
          {/* Pill container when scrolled */}
          <div className={`flex items-center justify-between gap-4 transition-all duration-500 ${
            scrolled || location.pathname !== '/'
              ? 'bg-white/70 backdrop-blur-xl border border-white/60 rounded-2xl px-5 py-1.5 shadow-glass-lg'
              : ''
          }`}>
            {/* Logo */}
            <Link to="/" className="blend-logo flex items-center gap-2.5 shrink-0">
              <div className={`flex items-center gap-2 transition-all duration-300 ${
                scrolled || location.pathname !== '/' 
                  ? '' 
                  : 'bg-white/80 backdrop-blur-md rounded-2xl px-3 py-1 shadow-glass border border-white/50'
              }`}>
                <img src="/logo.jpg" alt="SICP Logo" className="w-auto h-12 object-contain mix-blend-multiply" style={{ mixBlendMode: 'multiply' }} />
              </div>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden lg:flex items-center gap-1" aria-label="Main navigation">
              {NAV_LINKS.map(({ hash, label }) => (
                <button
                  key={hash}
                  onClick={() => scrollTo(hash)}
                  className="relative px-4 py-2 text-[13px] font-semibold text-ink/70 hover:text-primary-700 transition-colors rounded-lg hover:bg-primary-50/50"
                >
                  {label}
                </button>
              ))}
            </nav>

            {/* Right Actions */}
            <div className="hidden sm:flex items-center gap-2">
              <button className="px-3 py-1.5 text-xs font-bold rounded-lg border border-primary-200/50 text-primary-700 hover:bg-primary-50 transition-colors">हिंदी</button>
              <Link to="/university" className="px-4 py-2 text-xs font-bold rounded-lg text-primary-700 hover:bg-primary-50 border border-primary-200/40 transition-all">Login</Link>
              <Link to="/citizen" className="glass-btn glass-btn-primary !py-2 !px-5 !text-xs !rounded-lg">Sign Up</Link>
            </div>

            {/* Mobile Toggle */}
            <button
              className="lg:hidden p-2 rounded-xl text-primary-800 hover:bg-primary-50 transition-colors"
              onClick={() => setMobileOpen(v => !v)}
              aria-expanded={mobileOpen}
              aria-label="Toggle navigation"
            >
              {mobileOpen ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" d="M6 18 18 6M6 6l12 12" /></svg>
              ) : (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileOpen && (
            <div className="lg:hidden mt-2 p-4 rounded-2xl bg-white/80 backdrop-blur-xl border border-white/50 shadow-glass-lg animate-fade-in">
              <div className="grid gap-1">
                {NAV_LINKS.map(({ hash, label }) => (
                  <button
                    key={hash}
                    onClick={() => scrollTo(hash)}
                    className="text-left rounded-xl px-4 py-3 text-sm font-semibold text-ink/80 hover:bg-primary-50 transition-colors"
                  >
                    {label}
                  </button>
                ))}
              </div>
              <div className="mt-3 flex gap-2">
                <Link to="/university" className="flex-1 text-center rounded-xl border border-primary-200 px-3 py-2.5 text-sm font-bold text-primary-700 hover:bg-primary-50">Login</Link>
                <Link to="/citizen" className="flex-1 text-center rounded-xl bg-primary-700 text-white px-3 py-2.5 text-sm font-bold hover:bg-primary-800">Sign Up</Link>
              </div>
            </div>
          )}
        </div>
      </header>
    </>
  )
}
