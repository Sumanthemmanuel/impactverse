import React, { useState, useEffect } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts'
import {
  getDashboardStats, getProblems, postIndustryInterest,
} from '../../api.js'
import { Card, CardHeader, Badge, Button } from '../ui/index.js'
import { Input, FormField } from '../ui/Form.jsx'
import { useTranslation } from '../../i18n.js'

const DOMAIN_COLORS = [
  '#6366f1','#14b8a6','#f59e0b','#10b981','#3b82f6',
  '#ec4899','#8b5cf6','#ef4444','#06b6d4','#84cc16',
]
const STATUS_COLORS_MAP = {
  'new': '#6366f1', 'in-progress': '#f59e0b', 'resolved': '#10b981', 'duplicate': '#6b7280',
}

function StatCard({ label, value, icon, color = 'primary', sub }) {
  const colorMap = {
    primary: 'bg-primary-50 text-primary-700',
    teal:    'bg-teal-50 text-teal-700',
    amber:   'bg-amber-50 text-amber-700',
    emerald: 'bg-emerald-50 text-emerald-700',
  }
  return (
    <Card padding="md" className="flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${colorMap[color]}`}>{icon}</div>
      <div>
        <p className="text-ink-muted text-sm">{label}</p>
        <p className="text-3xl font-extrabold text-ink tabular-nums">{value ?? '—'}</p>
        {sub && <p className="text-xs text-ink-subtle mt-0.5">{sub}</p>}
      </div>
    </Card>
  )
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-surface-border rounded-xl shadow-card-hover px-3 py-2 text-sm">
      {label && <p className="text-ink-muted text-xs mb-1">{label}</p>}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: p.fill ?? p.color }} />
          <span className="text-ink font-semibold">{p.value}</span>
          <span className="text-ink-muted">{p.name}</span>
        </div>
      ))}
    </div>
  )
}

function IndustryInterestPanel({ problems, t }) {
  const [problemId, setProblemId]     = useState('')
  const [industryName, setIndustryName] = useState('')
  const [status, setStatus]           = useState(null)
  const [msg, setMsg]                 = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!problemId || !industryName.trim()) { setMsg('Both fields are required.'); setStatus('error'); return }
    setStatus('loading')
    try {
      await postIndustryInterest(problemId, industryName.trim())
      setStatus('success')
      setMsg(`${industryName} registered interest in ${problemId}.`)
      setIndustryName('')
    } catch (err) { setStatus('error'); setMsg(err.message ?? 'Something went wrong.') }
  }

  return (
    <Card>
      <CardHeader title={t('admin.industry.title')} subtitle={t('admin.industry.sub')} />
      <form onSubmit={handleSubmit} className="space-y-4">
        <FormField label={t('admin.industry.prob')}>
          <select
            value={problemId}
            onChange={e => setProblemId(e.target.value)}
            className="w-full rounded-xl border border-surface-border bg-white px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">{t('admin.industry.prob.ph')}</option>
            {problems.map(p => <option key={p.id} value={p.id}>[{p.id}] {p.title}</option>)}
          </select>
        </FormField>
        <FormField label={t('admin.industry.name')}>
          <Input placeholder={t('admin.industry.name.ph')} value={industryName} onChange={e => setIndustryName(e.target.value)} />
        </FormField>
        {status === 'success' && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3 text-sm text-emerald-800">✓ {msg}</div>
        )}
        {status === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">{msg}</div>
        )}
        <Button type="submit" loading={status === 'loading'} className="w-full">{t('admin.industry.btn')}</Button>
      </form>
    </Card>
  )
}

export default function AdminDashboard() {
  const { t } = useTranslation()
  const [stats, setStats]       = useState(null)
  const [problems, setProblems] = useState([])
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([getDashboardStats(), getProblems()])
      .then(([s, p]) => { setStats(s); setProblems(p) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <svg className="animate-spin h-10 w-10 text-primary-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
          </svg>
          <p className="text-ink-muted text-sm">{t('admin.loading')}</p>
        </div>
      </div>
    )
  }

  const domainData   = Object.entries(stats.by_domain).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)
  const districtData = Object.entries(stats.by_district).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)
  const statusOrder  = ['new', 'in-progress', 'resolved', 'duplicate']
  const statusData   = statusOrder.map(s => ({ name: s.replace('-', ' '), value: stats.by_status[s] ?? 0, status: s }))

  return (
    <div className="min-h-screen bg-surface">
      {/* Page header */}
      <div className="bg-white border-b border-surface-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          <h1 className="text-2xl font-bold text-ink">{t('admin.title')}</h1>
          <p className="text-ink-muted text-sm mt-0.5">{t('admin.sub')}</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* ── Stat cards ── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              label: t('admin.stat.total'), value: stats.total_problems,
              sub: t('admin.stat.total.sub'), color: 'primary',
              icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>,
            },
            {
              label: t('admin.stat.uni'), value: stats.universities_engaged,
              sub: t('admin.stat.uni.sub'), color: 'teal',
              icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 14l9-5-9-5-9 5 9 5z"/><path strokeLinecap="round" strokeLinejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/></svg>,
            },
            {
              label: t('admin.stat.ind'), value: stats.industries_engaged,
              sub: t('admin.stat.ind.sub'), color: 'amber',
              icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>,
            },
            {
              label: t('admin.stat.res'), value: stats.by_status.resolved ?? 0,
              sub: `of ${stats.total_problems} total`, color: 'emerald',
              icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
            },
          ].map((c, i) => <StatCard key={i} {...c} />)}
        </div>

        {/* ── Charts row 1 ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader title={t('admin.chart.domain')} subtitle={t('admin.chart.domain.sub')} />
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={domainData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} innerRadius={50} paddingAngle={2}>
                  {domainData.map((_, i) => <Cell key={i} fill={DOMAIN_COLORS[i % DOMAIN_COLORS.length]} />)}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
                <Legend formatter={v => <span style={{ fontSize: 11, color: '#64748b' }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <CardHeader title={t('admin.chart.dist')} subtitle={t('admin.chart.dist.sub')} />
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={districtData} margin={{ top: 4, right: 16, left: -8, bottom: 28 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} angle={-35} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="value" name="Problems" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* ── Charts row 2 ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader title={t('admin.chart.status')} subtitle={t('admin.chart.status.sub')} />
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={statusData} layout="vertical" margin={{ left: 16, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 12, fill: '#0f172a', textTransform: 'capitalize' }} width={92} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {statusData.map((d, i) => <Cell key={i} fill={STATUS_COLORS_MAP[d.status] ?? '#6366f1'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="grid grid-cols-2 gap-3 mt-5">
              {Object.entries(stats.by_status).map(([s, v]) => (
                <div key={s} className="flex items-center justify-between bg-surface-muted rounded-lg px-3 py-2">
                  <Badge variant="status" status={s} size="sm" />
                  <span className="font-bold text-ink tabular-nums">{v}</span>
                </div>
              ))}
            </div>
          </Card>

          <IndustryInterestPanel problems={problems} t={t} />
        </div>

        {/* ── Recent table ── */}
        <Card>
          <CardHeader title={t('admin.table.title')} subtitle={t('admin.table.sub')} />
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border">
                  {[t('admin.table.id'), t('admin.table.title2'), t('admin.table.domain'), t('admin.table.dist'), t('admin.table.priority'), t('admin.table.status')].map(h => (
                    <th key={h} className="text-left py-2 px-3 text-ink-muted font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {problems.slice(0, 8).map((p, i) => (
                  <tr key={p.id} className={`border-b border-surface-border/60 hover:bg-surface-muted transition-colors ${i % 2 === 0 ? '' : 'bg-surface-muted/40'}`}>
                    <td className="py-2.5 px-3 font-mono text-xs text-ink-muted">{p.id}</td>
                    <td className="py-2.5 px-3 text-ink max-w-xs"><span className="line-clamp-1">{p.title}</span></td>
                    <td className="py-2.5 px-3"><Badge size="sm">{p.domain}</Badge></td>
                    <td className="py-2.5 px-3 text-ink-muted">{p.district}</td>
                    <td className="py-2.5 px-3">
                      <span className={`font-semibold tabular-nums ${p.priority_score >= 8 ? 'text-red-600' : p.priority_score >= 5 ? 'text-amber-600' : 'text-emerald-600'}`}>
                        {p.priority_score}
                      </span>
                    </td>
                    <td className="py-2.5 px-3"><Badge variant="status" status={p.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

      </div>
    </div>
  )
}
