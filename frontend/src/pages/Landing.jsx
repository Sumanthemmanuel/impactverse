import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from '../../i18n.js'
import { Button } from '../ui/index.js'

const DOMAINS = [
  { icon: '🎓', label: 'Education',          labelHi: 'शिक्षा' },
  { icon: '🌾', label: 'Agriculture',         labelHi: 'कृषि' },
  { icon: '🏥', label: 'Healthcare',          labelHi: 'स्वास्थ्य' },
  { icon: '💧', label: 'Water Resources',     labelHi: 'जल संसाधन' },
  { icon: '🌿', label: 'Environment',         labelHi: 'पर्यावरण' },
  { icon: '⚡', label: 'Energy',              labelHi: 'ऊर्जा' },
  { icon: '🏙️', label: 'Urban Development',  labelHi: 'शहरी विकास' },
  { icon: '♿', label: 'Accessibility',       labelHi: 'पहुँच' },
  { icon: '🏛️', label: 'Public Admin',       labelHi: 'लोक प्रशासन' },
  { icon: '🌱', label: 'Rural Livelihoods',   labelHi: 'ग्रामीण आजीविका' },
]

const HOW_IT_WORKS = [
  {
    step: '01',
    en: 'Citizen Reports',
    hi: 'नागरिक रिपोर्ट करता है',
    desc_en: 'Drop a pin on the map, describe the problem, upload a photo.',
    desc_hi: 'मानचित्र पर पिन लगाएं, समस्या बताएं, फ़ोटो अपलोड करें।',
    color: 'bg-primary-600',
  },
  {
    step: '02',
    en: 'AI Classifies',
    hi: 'AI वर्गीकरण करता है',
    desc_en: 'Zero-shot ML assigns the right domain and priority score.',
    desc_hi: 'जीरो-शॉट ML सही डोमेन और प्राथमिकता स्कोर असाइन करता है।',
    color: 'bg-accent-600',
  },
  {
    step: '03',
    en: 'University Acts',
    hi: 'विश्वविद्यालय कार्यवाही करता है',
    desc_en: 'Matched universities form teams and track progress.',
    desc_hi: 'मिलान किए गए विश्वविद्यालय टीम बनाते हैं और प्रगति ट्रैक करते हैं।',
    color: 'bg-amber-500',
  },
  {
    step: '04',
    en: 'Problem Resolved',
    hi: 'समस्या हल होती है',
    desc_en: 'Citizens see real-time status updates on the public tracker.',
    desc_hi: 'नागरिक सार्वजनिक ट्रैकर पर रियल-टाइम स्थिति अपडेट देखते हैं।',
    color: 'bg-emerald-500',
  },
]

export default function LandingPage() {
  const { t, lang } = useTranslation()

  return (
    <div className="min-h-screen bg-white">
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-800 via-primary-700 to-primary-900">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-20 lg:py-28">
          <div className="max-w-3xl">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur-sm border border-white/20 rounded-full px-4 py-1.5 text-sm text-white/90 mb-6">
              <span className="w-2 h-2 bg-accent-400 rounded-full animate-pulse" />
              Smart India Hackathon 2026
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-tight mb-5">
              {t('home.hero.title')}
            </h1>
            <p className="text-lg sm:text-xl text-primary-200 leading-relaxed mb-8 max-w-2xl">
              {t('home.hero.sub')}
            </p>

            <div className="flex flex-wrap gap-3">
              <Link to="/citizen">
                <Button size="lg" className="bg-white text-primary-800 hover:bg-primary-50 border-0 shadow-lg">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  {t('home.hero.cta1')}
                </Button>
              </Link>
              <Link to="/citizen/tracker">
                <Button size="lg" variant="ghost" className="text-white border border-white/30 hover:bg-white/15">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  {t('home.hero.cta2')}
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Stats strip */}
        <div className="relative border-t border-white/10 bg-primary-900/60 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5 grid grid-cols-2 sm:grid-cols-4 gap-6">
            {[
              { label: t('home.stat1.label'), value: '127', icon: '📋' },
              { label: t('home.stat2.label'), value: '24',  icon: '📍' },
              { label: t('home.stat3.label'), value: '8',   icon: '🎓' },
              { label: t('home.stat4.label'), value: '21',  icon: '✅' },
            ].map((s, i) => (
              <div key={i} className="text-center">
                <div className="text-2xl mb-0.5">{s.icon}</div>
                <div className="text-2xl font-extrabold text-white">{s.value}</div>
                <div className="text-xs text-primary-300 mt-0.5">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────── */}
      <section className="py-16 bg-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-ink mb-3">
              {lang === 'hi' ? 'यह कैसे काम करता है' : 'How It Works'}
            </h2>
            <p className="text-ink-muted max-w-xl mx-auto">
              {lang === 'hi'
                ? 'रिपोर्टिंग से लेकर समाधान तक — पारदर्शी और जवाबदेह'
                : 'From reporting to resolution — transparent and accountable'}
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {HOW_IT_WORKS.map((step, i) => (
              <div key={i} className="relative">
                {/* Connector line */}
                {i < HOW_IT_WORKS.length - 1 && (
                  <div className="hidden lg:block absolute top-6 left-[calc(100%-0px)] w-full h-0.5 bg-surface-border z-0" style={{ left: '50%', width: '100%' }} />
                )}
                <div className="bg-white rounded-2xl border border-surface-border shadow-card p-6 text-center hover:shadow-card-hover transition-shadow relative z-10">
                  <div className={`w-12 h-12 ${step.color} rounded-full flex items-center justify-center text-white text-sm font-bold mx-auto mb-4 shadow-sm`}>
                    {step.step}
                  </div>
                  <h3 className="font-semibold text-ink mb-2">{lang === 'hi' ? step.hi : step.en}</h3>
                  <p className="text-sm text-ink-muted">{lang === 'hi' ? step.desc_hi : step.desc_en}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Domain cards ──────────────────────────────────────────────── */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-ink mb-3">
              {lang === 'hi' ? '10 सक्रिय क्षेत्र' : '10 Active Domains'}
            </h2>
            <p className="text-ink-muted">
              {lang === 'hi'
                ? 'हर नागरिक समस्या इनमें से किसी एक क्षेत्र में आती है'
                : 'Every civic problem falls under one of these domains'}
            </p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {DOMAINS.map((d, i) => (
              <Link
                key={i}
                to={`/citizen/tracker`}
                className="group bg-surface-muted hover:bg-primary-50 border border-surface-border hover:border-primary-300 rounded-2xl p-4 text-center transition-all duration-200 hover:shadow-card-hover"
              >
                <div className="text-3xl mb-2">{d.icon}</div>
                <div className="text-sm font-medium text-ink group-hover:text-primary-700">
                  {lang === 'hi' ? d.labelHi : d.label}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="bg-primary-900 text-primary-300 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <div className="text-white font-bold text-lg mb-1">
                {lang === 'hi' ? 'इम्पैक्टवर्स' : 'ImpactVerse'}
              </div>
              <div className="text-sm">
                {lang === 'hi'
                  ? 'झारखंड सरकार की पहल · SIH 2026'
                  : 'Government of Jharkhand Initiative · SIH 2026'}
              </div>
            </div>
            <div className="flex gap-6 text-sm">
              <Link to="/citizen" className="hover:text-white transition-colors">{t('nav.citizen')}</Link>
              <Link to="/citizen/tracker" className="hover:text-white transition-colors">{lang === 'hi' ? 'ट्रैकर' : 'Tracker'}</Link>
              <Link to="/admin" className="hover:text-white transition-colors">{t('nav.admin')}</Link>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-primary-800 text-xs text-primary-500 text-center">
            © 2026 ImpactVerse. Built for Smart India Hackathon.
          </div>
        </div>
      </footer>
    </div>
  )
}
