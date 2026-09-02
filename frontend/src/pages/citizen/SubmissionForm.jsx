import React, { useState, useCallback } from 'react'
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import { Link } from 'react-router-dom'
import { submitProblem, reverseGeocode, DOMAINS } from '../../api.js'
import { Button, Card, CardHeader, Badge } from '../../components/ui/index.js'
import { Input, Textarea, FormField } from '../../components/ui/Form.jsx'
import { useTranslation } from '../../i18n.jsx'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

function MapClickHandler({ onPin }) {
  useMapEvents({ click(e) { onPin(e.latlng.lat, e.latlng.lng) } })
  return null
}

// ── Domains translated ────────────────────────────────────────────────────────
const DOMAIN_HI = {
  'Education': 'शिक्षा', 'Agriculture': 'कृषि', 'Healthcare': 'स्वास्थ्य',
  'Water Resources': 'जल संसाधन', 'Environment': 'पर्यावरण', 'Energy': 'ऊर्जा',
  'Urban Development': 'शहरी विकास', 'Accessibility': 'पहुँच',
  'Public Administration': 'लोक प्रशासन', 'Rural Livelihoods': 'ग्रामीण आजीविका',
}

// ── Success State ─────────────────────────────────────────────────────────────
function SuccessState({ problem, onReset, t }) {
  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4">
      <div className="max-w-lg w-full">
        {/* Confetti-like top bar */}
        <div className="h-2 rounded-t-2xl bg-gradient-to-r from-primary-500 via-accent-500 to-emerald-500" />
        <Card className="rounded-t-none" padding="lg">
          <div className="text-center">
            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-5 border-4 border-emerald-200">
              <svg className="w-10 h-10 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-ink mb-2">{t('submit.success.title')}</h2>
            <p className="text-ink-muted mb-7">{t('submit.success.sub')}</p>

            <div className="bg-surface-muted rounded-xl divide-y divide-surface-border mb-7">
              {[
                [t('submit.success.id'),     <span className="font-mono text-sm font-semibold text-primary-700">{problem.id}</span>],
                [t('submit.success.domain'), <Badge>{problem.domain}</Badge>],
                [t('submit.success.status'), <Badge variant="status" status={problem.status} />],
                [t('submit.success.score'),  <span className="font-bold text-primary-700">{problem.priority_score}</span>],
                [t('submit.success.dist'),   <span className="text-sm text-ink">{problem.district}</span>],
              ].map(([label, val], i) => (
                <div key={i} className="flex items-center justify-between px-4 py-3">
                  <span className="text-sm text-ink-muted">{label}</span>
                  {val}
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <Button variant="secondary" className="flex-1" onClick={onReset}>
                {t('submit.success.more')}
              </Button>
              <Link to="/citizen/tracker" className="flex-1">
                <Button variant="primary" className="w-full">
                  {t('submit.success.track')}
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

// ── Main Form ─────────────────────────────────────────────────────────────────
export default function SubmissionForm() {
  const { t, lang } = useTranslation()
  const [fields, setFields] = useState({
    title: '', description: '', category: '',
    photo_url: '', lat: null, lng: null, district: '', submitted_by: '',
  })
  const [photoName, setPhotoName]   = useState('')
  const [geocoding, setGeocoding]   = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors]         = useState({})
  const [submitted, setSubmitted]   = useState(null)

  const set = (key, value) => setFields(f => ({ ...f, [key]: value }))

  const handlePhoto = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setPhotoName(file.name)
    const reader = new FileReader()
    reader.onload = () => set('photo_url', reader.result)
    reader.readAsDataURL(file)
  }

  const handlePin = useCallback(async (lat, lng) => {
    set('lat', lat); set('lng', lng)
    setGeocoding(true)
    try {
      const district = await reverseGeocode(lat, lng)
      set('district', district)
    } catch { /* user can type manually */ } finally { setGeocoding(false) }
  }, [])

  const validate = () => {
    const e = {}
    if (!fields.title.trim())        e.title       = lang === 'hi' ? 'शीर्षक आवश्यक है' : 'Title is required'
    if (!fields.description.trim())  e.description = lang === 'hi' ? 'विवरण आवश्यक है' : 'Description is required'
    if (!fields.category)            e.category    = lang === 'hi' ? 'कृपया एक श्रेणी चुनें' : 'Please select a category'
    if (!fields.lat || !fields.lng)  e.map         = t('submit.map.err')
    if (!fields.submitted_by.trim()) e.submitted_by = lang === 'hi' ? 'आपका नाम आवश्यक है' : 'Your name is required'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      const result = await submitProblem({
        title: fields.title.trim(), description: fields.description.trim(),
        photo_url: fields.photo_url, lat: fields.lat, lng: fields.lng,
        submitted_by: fields.submitted_by.trim(), district: fields.district,
      })
      setSubmitted(result)
    } catch (err) {
      setErrors({ submit: err.message ?? (lang === 'hi' ? 'सबमिशन विफल, पुनः प्रयास करें' : 'Submission failed, please try again.') })
    } finally { setSubmitting(false) }
  }

  const resetForm = () => {
    setSubmitted(null)
    setFields({ title:'', description:'', category:'', photo_url:'', lat:null, lng:null, district:'', submitted_by:'' })
    setPhotoName(''); setErrors({})
  }

  if (submitted) return <SuccessState problem={submitted} onReset={resetForm} t={t} />

  return (
    <div className="min-h-screen bg-surface">
      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 text-white">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23fff' fill-opacity='1' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E")`,
        }} />
        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 py-12">
          <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur-sm border border-white/20 rounded-full px-3.5 py-1.5 text-sm mb-5">
            <span className="w-2 h-2 bg-accent-400 rounded-full animate-pulse" />
            {t('submit.hero.badge')}
          </div>
          <h1 className="text-4xl font-extrabold mb-3 leading-tight">{t('submit.hero.title')}</h1>
          <p className="text-primary-200 text-lg leading-relaxed max-w-xl">{t('submit.hero.sub')}</p>
        </div>
      </div>

      {/* Form body */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <form onSubmit={handleSubmit} noValidate className="space-y-6">

          {/* Problem details */}
          <Card>
            <CardHeader title={t('submit.card1.title')} subtitle={t('submit.card1.sub')} />
            <div className="space-y-5">
              <FormField label={t('submit.title.label')} required error={errors.title}>
                <Input placeholder={t('submit.title.ph')} value={fields.title} onChange={e => set('title', e.target.value)} />
              </FormField>
              <FormField label={t('submit.desc.label')} required error={errors.description}>
                <Textarea rows={4} placeholder={t('submit.desc.ph')} value={fields.description} onChange={e => set('description', e.target.value)} />
              </FormField>
              <FormField label={t('submit.cat.label')} required error={errors.category}>
                <select
                  value={fields.category}
                  onChange={e => set('category', e.target.value)}
                  className="w-full rounded-xl border border-surface-border bg-white px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">{t('submit.cat.ph')}</option>
                  {DOMAINS.map(d => (
                    <option key={d} value={d}>{lang === 'hi' ? `${DOMAIN_HI[d]} (${d})` : d}</option>
                  ))}
                </select>
                <p className="text-xs text-ink-subtle mt-1">{t('submit.cat.note')}</p>
              </FormField>
            </div>
          </Card>

          {/* Location */}
          <Card>
            <CardHeader title={t('submit.loc.title')} subtitle={t('submit.loc.sub')} />
            <div className="rounded-xl overflow-hidden border border-surface-border mb-4" style={{ height: 340 }}>
              <MapContainer center={[23.3441, 85.3096]} zoom={7} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                />
                <MapClickHandler onPin={handlePin} />
                {fields.lat && fields.lng && <Marker position={[fields.lat, fields.lng]} />}
              </MapContainer>
            </div>
            {errors.map && <p className="text-xs text-red-600 mb-3">{errors.map}</p>}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <FormField label={t('submit.lat.label')}>
                <Input value={fields.lat ? fields.lat.toFixed(5) : ''} readOnly placeholder={t('submit.map.ph')} className="bg-surface-muted" />
              </FormField>
              <FormField label={t('submit.lng.label')}>
                <Input value={fields.lng ? fields.lng.toFixed(5) : ''} readOnly placeholder={t('submit.map.ph')} className="bg-surface-muted" />
              </FormField>
            </div>
            <FormField label={t('submit.district.label')}>
              <div className="relative">
                <Input
                  value={fields.district}
                  onChange={e => set('district', e.target.value)}
                  placeholder={geocoding ? t('submit.detecting') : t('submit.district.ph')}
                />
                {geocoding && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <svg className="animate-spin h-4 w-4 text-primary-500" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                    </svg>
                  </div>
                )}
              </div>
            </FormField>
          </Card>

          {/* Photo + contact */}
          <Card>
            <CardHeader title={t('submit.photo.title')} subtitle={t('submit.photo.sub')} />
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-ink mb-1.5">{t('submit.photo.label')}</label>
                <label className="flex flex-col items-center justify-center w-full h-36 border-2 border-dashed border-surface-border rounded-xl cursor-pointer hover:border-primary-400 hover:bg-primary-50 transition-colors group">
                  <div className="flex flex-col items-center gap-1.5 text-ink-muted group-hover:text-primary-600">
                    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                    </svg>
                    {photoName
                      ? <span className="text-sm text-primary-700 font-medium">{photoName}</span>
                      : <span className="text-sm font-medium">{t('submit.photo.hint')}</span>}
                    <span className="text-xs">{t('submit.photo.types')}</span>
                  </div>
                  <input type="file" accept="image/*" className="hidden" onChange={handlePhoto} />
                </label>
                {fields.photo_url && (
                  <img src={fields.photo_url} alt="Preview" className="mt-3 w-full max-h-48 object-cover rounded-xl border border-surface-border" />
                )}
              </div>
              <FormField label={t('submit.name.label')} required error={errors.submitted_by}>
                <Input placeholder={t('submit.name.ph')} value={fields.submitted_by} onChange={e => set('submitted_by', e.target.value)} />
              </FormField>
            </div>
          </Card>

          {errors.submit && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{errors.submit}</div>
          )}

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-2">
            <p className="text-sm text-ink-muted">{t('submit.disclaimer')}</p>
            <Button type="submit" size="lg" loading={submitting} className="w-full sm:w-auto min-w-[180px]">
              {t('submit.btn')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
