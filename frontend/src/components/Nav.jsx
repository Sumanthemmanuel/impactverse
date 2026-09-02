import React, { useEffect, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { useTranslation } from '../i18n.jsx'

const HOME_LINKS = [
  { hash: '#main-content', label: 'Home' },
  { hash: '#explore', label: 'Explore' },
  { hash: '#how-it-works', label: 'How It Works' },
  { hash: '#impact', label: 'Impact' },
  { hash: '#about', label: 'About Us' },
]

export default function Nav() {
  const { lang, setLang } = useTranslation()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [highContrast, setHighContrast] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('high-contrast', highContrast)
    return () => document.documentElement.classList.remove('high-contrast')
  }, [highContrast])

  const closeMenu = () => setMobileOpen(false)
  const scrollTo = (hash) => {
    closeMenu()
    if (location.pathname === '/') document.querySelector(hash)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <>
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-xl border-b border-white shadow-[0_10px_34px_-30px_rgba(9,51,30,.45)]">
        <div className="max-w-[1540px] mx-auto px-4 sm:px-6">
          <div className="h-[4.3rem] flex items-center justify-between gap-4">
            <NavLink to="/" onClick={closeMenu} className="blend-logo flex items-center gap-2 shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-lg">
              <img src="/sicp-jharkhand-logo.jpeg" alt="Government of Jharkhand and SICP" className="w-28 sm:w-36 h-11 object-contain" />
            </NavLink>

            <nav className="hidden lg:flex items-center gap-5" aria-label="Main navigation">
              {HOME_LINKS.map(({ hash, label }) => <Link key={hash} to={`/${hash}`} onClick={() => scrollTo(hash)} className="relative py-2 text-[12px] font-bold text-ink hover:text-primary-700 transition-colors first:text-primary-700 first:after:absolute first:after:inset-x-0 first:after:-bottom-0.5 first:after:h-0.5 first:after:bg-primary-700">{label}</Link>)}
            </nav>

            <div className="hidden sm:flex items-center gap-2">
              <button onClick={() => setHighContrast(value => !value)} aria-pressed={highContrast} title="Toggle high contrast" className="p-2 rounded-lg text-primary-700 hover:bg-primary-50 focus-visible:ring-2 focus-visible:ring-primary-500"><span aria-hidden="true" className="text-sm font-black">A</span><span className="sr-only">Toggle high contrast</span></button>
              <button onClick={() => setLang(lang === 'en' ? 'hi' : 'en')} className="rounded-md border border-surface-border bg-white px-3 py-2 text-[11px] font-bold text-ink hover:border-primary-300 focus-visible:ring-2 focus-visible:ring-primary-500">{lang === 'en' ? 'हिंदी' : 'EN'}</button>
              <Link to="/university" className="rounded-md border border-surface-border bg-white px-3 py-2 text-[11px] font-bold text-ink hover:border-primary-300">Login</Link>
              <Link to="/citizen" className="rounded-md bg-primary-700 px-3.5 py-2 text-[11px] font-bold text-white shadow-sm hover:bg-primary-800">Sign Up</Link>
            </div>

            <button className="lg:hidden p-2 rounded-lg text-primary-800 hover:bg-primary-50 focus-visible:ring-2 focus-visible:ring-primary-500" onClick={() => setMobileOpen(value => !value)} aria-expanded={mobileOpen} aria-label="Toggle navigation menu">
              {mobileOpen ? <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" d="M6 18 18 6M6 6l12 12" /></svg> : <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" /></svg>}
            </button>
          </div>

          {mobileOpen && <div className="lg:hidden border-t border-surface-border py-3 grid gap-1">
            {HOME_LINKS.map(({ hash, label }) => <Link key={hash} to={`/${hash}`} onClick={() => scrollTo(hash)} className="rounded-lg px-3 py-2.5 text-sm font-bold text-ink hover:bg-primary-50">{label}</Link>)}
            <div className="mt-2 flex gap-2"><Link to="/university" onClick={closeMenu} className="flex-1 text-center rounded-lg border border-surface-border px-3 py-2 text-sm font-bold">Login</Link><Link to="/citizen" onClick={closeMenu} className="flex-1 text-center rounded-lg bg-primary-700 text-white px-3 py-2 text-sm font-bold">Sign Up</Link></div>
          </div>}
        </div>
      </header>
    </>
  )
}
