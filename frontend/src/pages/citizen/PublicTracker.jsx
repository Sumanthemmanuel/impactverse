import React, { useState, useEffect, useCallback } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { Link } from 'react-router-dom'
import { getProblems, DOMAINS, STATUSES, DISTRICTS } from '../../api.js'
import { Card, Badge, Button } from '../ui/index.js'
import { useTranslation } from '../../i18n.js'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const STATUS_COLORS = {
  'new':         '#6366f1',
  'in-progress': '#f59e0b',
  'resolved':    '#10b981',
  'duplicate':   '#6b7280',
}

function makeIcon(color, selected = false) {
  const size = selected ? 22 : 16
  return L.divIcon({
    html: `<div style="
      width:${size}px;height:${size}px;border-radius:50%;
      background:${color};border:${selected ? 4 : 3}px solid white;
      box-shadow:0 2px 6px rgba(0,0,0,${selected ? '.4' : '.25'});
      transition:all .2s"></div>`,
    className: '',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function MapFlyTo({ target }) {
  const map = useMap()
  useEffect(() => {
    if (target) map.flyTo([target.lat, target.lng], 13, { animate: true, duration: 1 })
  }, [target, map])
  return null
}

function PriorityBar({ score }) {
  const pct = Math.min(100, (score / 10) * 100)
  const color = score >= 8 ? 'bg-red-500' : score >= 5 ? 'bg-amber-500' : 'bg-emerald-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-surface-border rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-semibold text-ink-muted tabular-nums w-8">{score}</span>
    </div>
  )
}

function ProblemCard({ problem, selected, onClick, t }) {
  return (
    <div
      onClick={onClick}
      className={[
        'p-4 rounded-xl border cursor-pointer transition-all duration-200',
        selected
          ? 'border-primary-400 bg-primary-50 shadow-md ring-1 ring-primary-300'
          : 'border-surface-border bg-white hover:border-primary-200 hover:shadow-card-hover',
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="text-sm font-semibold text-ink leading-snug line-clamp-2 flex-1">{problem.title}</h3>
        <Badge variant="status" status={problem.status} />
      </div>
      <p className="text-xs text-ink-muted line-clamp-2 mb-3">{problem.description}</p>
      <div className="mb-2">
        <p className="text-xs text-ink-subtle mb-1">{t('tracker.priority')}</p>
        <PriorityBar score={problem.priority_score} />
      </div>
      <div className="flex items-center justify-between mt-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          <Badge size="sm">{problem.domain}</Badge>
          <span className="text-xs text-ink-subtle">{problem.district}</span>
        </div>
        {problem.duplicate_count > 1 && (
          <span className="text-xs text-ink-subtle">+{problem.duplicate_count - 1} {t('tracker.others')}</span>
        )}
      </div>
    </div>
  )
}

export default function PublicTracker() {
  const { t } = useTranslation()
  const [problems, setProblems] = useState([])
  const [loading, setLoading]   = useState(true)
  const [selected, setSelected] = useState(null)
  const [filters, setFilters]   = useState({ domain: '', district: '', status: '' })

  const load = useCallback(async () => {
    setLoading(true)
    try { setProblems(await getProblems(filters)) }
    catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [filters])

  useEffect(() => { load() }, [load])

  const setFilter = (key, value) => { setFilters(f => ({ ...f, [key]: value })); setSelected(null) }
  const selectedProblem = problems.find(p => p.id === selected) ?? null

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <div className="bg-white border-b border-surface-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-ink">{t('tracker.title')}</h1>
              <p className="text-ink-muted text-sm mt-0.5">
                {loading
                  ? t('tracker.loading')
                  : `${problems.length} ${problems.length === 1 ? t('tracker.sub1') : t('tracker.sub')}`}
              </p>
            </div>
            <Link to="/citizen">
              <Button variant="primary" size="sm">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                {t('tracker.report.btn')}
              </Button>
            </Link>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-3 mt-5">
            {[
              { key: 'domain',   opts: DOMAINS,   all: t('tracker.filter.domain') },
              { key: 'district', opts: DISTRICTS, all: t('tracker.filter.dist')   },
              { key: 'status',   opts: STATUSES,  all: t('tracker.filter.status') },
            ].map(({ key, opts, all }) => (
              <select
                key={key}
                value={filters[key]}
                onChange={e => setFilter(key, e.target.value)}
                className="rounded-lg border border-surface-border bg-white px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm"
              >
                <option value="">{all}</option>
                {opts.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            ))}
            {(filters.domain || filters.district || filters.status) && (
              <button
                onClick={() => { setFilters({ domain:'', district:'', status:'' }); setSelected(null) }}
                className="text-sm text-primary-600 hover:underline px-2"
              >
                {t('tracker.clear')}
              </button>
            )}
          </div>

          {/* Status legend */}
          <div className="flex flex-wrap gap-4 mt-3">
            {Object.entries(STATUS_COLORS).map(([status, color]) => (
              <div key={status} className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full border-2 border-white shadow-sm" style={{ background: color }} />
                <span className="text-xs text-ink-muted capitalize">{t(`status.${status}`)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Split pane */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        <div className="flex flex-col lg:flex-row gap-6">

          {/* List */}
          <div className="lg:w-96 shrink-0 space-y-3 overflow-y-auto" style={{ maxHeight: 700 }}>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-28 bg-surface-muted animate-pulse rounded-xl" />
              ))
            ) : problems.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-14 h-14 bg-surface-muted rounded-full flex items-center justify-center mb-4">
                  <svg className="w-7 h-7 text-ink-subtle" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                  </svg>
                </div>
                <p className="font-medium text-ink-muted">{t('tracker.empty.title')}</p>
                <p className="text-sm text-ink-subtle mt-1">{t('tracker.empty.sub')}</p>
              </div>
            ) : (
              problems.map(p => (
                <ProblemCard
                  key={p.id} problem={p} t={t}
                  selected={selected === p.id}
                  onClick={() => setSelected(selected === p.id ? null : p.id)}
                />
              ))
            )}
          </div>

          {/* Map */}
          <div className="flex-1 rounded-2xl overflow-hidden border border-surface-border shadow-card" style={{ minHeight: 520 }}>
            <MapContainer center={[23.3441, 85.3096]} zoom={7} style={{ height: '100%', width: '100%', minHeight: 520 }}>
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              />
              <MapFlyTo target={selectedProblem} />
              {problems.map(p => (
                <Marker
                  key={p.id}
                  position={[p.lat, p.lng]}
                  icon={makeIcon(STATUS_COLORS[p.status] ?? STATUS_COLORS['new'], selected === p.id)}
                  eventHandlers={{ click: () => setSelected(p.id) }}
                >
                  <Popup>
                    <div className="text-sm min-w-[200px]">
                      <p className="font-semibold text-ink mb-1">{p.title}</p>
                      <p className="text-ink-muted text-xs mb-2 line-clamp-2">{p.description}</p>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="status" status={p.status} size="sm" />
                        <Badge size="sm">{p.domain}</Badge>
                      </div>
                      <p className="text-xs text-ink-subtle mt-2">{t('tracker.priority')}: {p.priority_score} · {p.district}</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
