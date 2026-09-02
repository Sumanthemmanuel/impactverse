import React, { useState, useEffect } from 'react'
import {
  getProblems, getSuggestedUniversities, updateProblemStatus, assignProblemToUniversity,
} from '../../api.js'
import { Card, CardHeader, Badge, Button } from '../../components/ui/index.js'
import { Input, FormField } from '../../components/ui/Form.jsx'
import { useTranslation } from '../../i18n.jsx'

// Demo: hardcoded university profile — IIT (ISM) Dhanbad
const MY_UNIVERSITY = {
  id: 'U001',
  domains: ['Environment', 'Energy', 'Water Resources'],
}

// ── Problem card ──────────────────────────────────────────────────────────────
function ProblemCard({ problem, onStart, onSaveTeam, teamInput, setTeamInput, teamSaved, t }) {
  const isInProgress = problem.status === 'in-progress'

  return (
    <Card hover padding="md" className="flex flex-col gap-4">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <Badge size="sm">{problem.domain}</Badge>
            <span className="text-xs text-ink-subtle font-mono">{problem.id}</span>
          </div>
          <h3 className="font-semibold text-ink leading-snug">{problem.title}</h3>
        </div>
        <Badge variant="status" status={problem.status} />
      </div>

      <p className="text-sm text-ink-muted leading-relaxed">{problem.description}</p>

      {/* Meta row */}
      <div className="flex flex-wrap gap-4 text-sm">
        <span className="flex items-center gap-1 text-ink-muted">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
          {t('uni.card.priority')}: <span className={`font-bold ml-0.5 ${problem.priority_score >= 8 ? 'text-red-600' : problem.priority_score >= 5 ? 'text-amber-600' : 'text-emerald-600'}`}>{problem.priority_score}</span>
        </span>
        <span className="flex items-center gap-1 text-ink-muted">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          </svg>
          {t('uni.card.district')}: <span className="font-medium text-ink ml-0.5">{problem.district}</span>
        </span>
        {problem.duplicate_count > 1 && (
          <span className="flex items-center gap-1 text-ink-muted">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            +{problem.duplicate_count - 1} {t('uni.card.duplicates')}
          </span>
        )}
      </div>

      {/* Team section */}
      {isInProgress && (
        <div className="border-t border-surface-border pt-4">
          <FormField label={t('uni.card.team.label')}>
            <div className="flex gap-2">
              <Input
                placeholder={t('uni.card.team.ph')}
                value={teamInput}
                onChange={e => setTeamInput(e.target.value)}
                className="flex-1"
              />
              <Button variant="secondary" size="sm" onClick={() => onSaveTeam(problem.id, teamInput)}>
                {t('uni.card.team.btn')}
              </Button>
            </div>
          </FormField>
          {teamSaved && (
            <p className="text-xs text-emerald-700 mt-1.5 flex items-center gap-1">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              {t('uni.card.team.saved')}
            </p>
          )}
        </div>
      )}

      {/* Action */}
      {!isInProgress && (
        <Button
          variant="primary"
          size="sm"
          className="w-full sm:w-auto"
          onClick={() => onStart(problem.id)}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {t('uni.card.start.btn')}
        </Button>
      )}
      {isInProgress && !teamSaved && (
        <div className="flex items-center gap-1.5 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {t('uni.card.inprogress')}
        </div>
      )}
    </Card>
  )
}

// ── Suggested problem card ────────────────────────────────────────────────────
function SuggestedCard({ problem, onAssign, t }) {
  return (
    <Card hover padding="sm" className="flex items-center gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <Badge size="sm">{problem.domain}</Badge>
          <Badge variant="status" status={problem.status} size="sm" />
        </div>
        <p className="text-sm font-medium text-ink line-clamp-1">{problem.title}</p>
        <p className="text-xs text-ink-muted">{problem.district}</p>
      </div>
      <Button variant="secondary" size="sm" className="shrink-0" onClick={() => onAssign(problem.id)}>
        {t('uni.suggest.assign')}
      </Button>
    </Card>
  )
}

// ── Main University Dashboard ─────────────────────────────────────────────────
export default function UniversityDashboard() {
  const { t } = useTranslation()
  const [problems, setProblems]         = useState([])
  const [suggested, setSuggested]       = useState([])
  const [loading, setLoading]           = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  // local team state: { [problemId]: { input: string, saved: bool } }
  const [teams, setTeams] = useState({})

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        // Load all problems matching our domain profile
        const all = await getProblems()
        const mine = all.filter(p => MY_UNIVERSITY.domains.includes(p.domain))
        setProblems(mine)

        // Suggested = problems in our domains we haven't started yet
        const pending = mine.filter(p => p.status === 'new').slice(0, 4)
        setSuggested(pending)
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  const handleStart = async (id) => {
    await updateProblemStatus(id, 'in-progress')
    setProblems(prev => prev.map(p => p.id === id ? { ...p, status: 'in-progress' } : p))
  }

  const handleSaveTeam = (id, input) => {
    setTeams(prev => ({ ...prev, [id]: { input, saved: true } }))
  }

  const handleAssign = async (problemId) => {
    await assignProblemToUniversity(MY_UNIVERSITY.id, problemId)
    // Move from suggested to main list
    const problem = suggested.find(p => p.id === problemId)
    if (problem) {
      setSuggested(prev => prev.filter(p => p.id !== problemId))
      if (!problems.find(p => p.id === problemId)) {
        setProblems(prev => [...prev, { ...problem, status: 'in-progress' }])
      }
    }
  }

  const filtered = statusFilter
    ? problems.filter(p => p.status === statusFilter)
    : problems

  return (
    <div className="min-h-screen bg-surface">
      {/* Page header */}
      <div className="bg-white border-b border-surface-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          <h1 className="text-2xl font-bold text-ink">{t('uni.title')}</h1>
          <p className="text-ink-muted text-sm mt-0.5">{t('uni.sub')}</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex flex-col lg:flex-row gap-8">

          {/* ── Left: profile sidebar ── */}
          <aside className="lg:w-72 shrink-0 space-y-5">
            <Card padding="md">
              <div className="w-14 h-14 bg-primary-100 rounded-2xl flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-primary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l9-5-9-5-9 5 9 5z"/>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/>
                </svg>
              </div>
              <h3 className="font-bold text-ink text-lg mb-0.5">{t('uni.profile.name')}</h3>
              <p className="text-xs text-ink-subtle mb-4">Jharkhand, India</p>

              <div className="space-y-3">
                <div>
                  <p className="text-xs text-ink-muted mb-1.5 font-medium">{t('uni.profile.domains')}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {MY_UNIVERSITY.domains.map(d => (
                      <Badge key={d} size="sm">{d}</Badge>
                    ))}
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-surface-border">
                  <p className="text-sm text-ink-muted">{t('uni.profile.assigned')}</p>
                  <span className="text-2xl font-extrabold text-primary-700">{problems.length}</span>
                </div>
              </div>
            </Card>

            {/* Status filter */}
            <Card padding="sm">
              <p className="text-xs font-medium text-ink-muted px-2 py-1 mb-1">{t('uni.filter.status')}</p>
              {[
                { value: '',            label: t('uni.all') },
                { value: 'new',         label: t('status.new') },
                { value: 'in-progress', label: t('status.in-progress') },
                { value: 'resolved',    label: t('status.resolved') },
              ].map(({ value, label }) => (
                <button
                  key={value}
                  onClick={() => setStatusFilter(value)}
                  className={[
                    'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors',
                    statusFilter === value
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-ink-muted hover:bg-surface-muted',
                  ].join(' ')}
                >
                  {label}
                  {value && (
                    <span className="float-right text-xs font-bold tabular-nums text-ink">
                      {problems.filter(p => p.status === value).length}
                    </span>
                  )}
                </button>
              ))}
            </Card>
          </aside>

          {/* ── Right: problems ── */}
          <main className="flex-1 min-w-0 space-y-8">
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <div className="flex flex-col items-center gap-3">
                  <svg className="animate-spin h-8 w-8 text-primary-500" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                  </svg>
                  <p className="text-ink-muted text-sm">{t('uni.loading')}</p>
                </div>
              </div>
            ) : (
              <>
                {/* Assigned problems */}
                <section>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-ink">
                      {t('uni.title')}
                      <span className="ml-2 text-sm font-normal text-ink-muted">({filtered.length})</span>
                    </h2>
                  </div>

                  {filtered.length === 0 ? (
                    <Card padding="lg" className="text-center">
                      <div className="w-12 h-12 bg-surface-muted rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-6 h-6 text-ink-subtle" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                      </div>
                      <p className="font-medium text-ink-muted">{t('uni.empty.title')}</p>
                      <p className="text-sm text-ink-subtle mt-1">{t('uni.empty.sub')}</p>
                    </Card>
                  ) : (
                    <div className="space-y-4">
                      {filtered.map(p => (
                        <ProblemCard
                          key={p.id}
                          problem={p}
                          t={t}
                          onStart={handleStart}
                          onSaveTeam={handleSaveTeam}
                          teamInput={teams[p.id]?.input ?? ''}
                          setTeamInput={input => setTeams(prev => ({
                            ...prev,
                            [p.id]: { ...prev[p.id], input, saved: false }
                          }))}
                          teamSaved={teams[p.id]?.saved ?? false}
                        />
                      ))}
                    </div>
                  )}
                </section>

                {/* Suggested problems */}
                {suggested.length > 0 && (
                  <section>
                    <h2 className="text-lg font-semibold text-ink mb-4">{t('uni.suggested.title')}</h2>
                    <div className="space-y-3">
                      {suggested.map(p => (
                        <SuggestedCard key={p.id} problem={p} t={t} onAssign={handleAssign} />
                      ))}
                    </div>
                  </section>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
