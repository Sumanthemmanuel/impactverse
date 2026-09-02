/**
 * api.js — ImpactVerse API layer
 *
 * HOW TO SWITCH FROM MOCK → LIVE:
 *   Change the single line below from:
 *     const USE_MOCK = true
 *   to:
 *     const USE_MOCK = false
 *
 * That's it. Every function in this file reads that flag.
 */

const USE_MOCK = true  // ← flip this one line to go live

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// ─── Mock data ────────────────────────────────────────────────────────────────

const MOCK_PROBLEMS = [
  {
    id: 'P001',
    title: 'Contaminated drinking water near Laxmi Nagar',
    description: 'The borewell water has turned brownish and several families report stomach illness after drinking it.',
    domain: 'Water Resources',
    priority_score: 8.5,
    status: 'Submitted',
    duplicate_count: 4,
    lat: 23.3441,
    lng: 85.3096,
    district: 'Ranchi',
    submitted_by: 'Ramesh Kumar',
  },
  {
    id: 'P002',
    title: 'Primary school roof collapsed in Govindpur',
    description: 'Heavy rains caused partial roof collapse in 3 classrooms. Children attending classes in the open.',
    domain: 'Education',
    priority_score: 9.0,
    status: 'In Progress',
    duplicate_count: 1,
    lat: 23.6693,
    lng: 85.9924,
    district: 'Dhanbad',
    submitted_by: 'Sunita Devi',
  },
  {
    id: 'P003',
    title: 'No doctor posted at Itkhori PHC for 6 months',
    description: 'The Primary Health Centre at Itkhori has been without a resident doctor since January. Patients travel 40km for care.',
    domain: 'Healthcare',
    priority_score: 7.0,
    status: 'new',
    duplicate_count: 3,
    lat: 24.0753,
    lng: 85.4895,
    district: 'Chatra',
    submitted_by: 'Mohan Prasad',
  },
  {
    id: 'P004',
    title: 'Street lights non-functional for 3 months in Ward 12',
    description: 'Entire stretch of NH-33 bypass in Ward 12 is dark at night. Two accidents reported last month.',
    domain: 'Urban Development',
    priority_score: 5.0,
    status: 'Resolved',
    duplicate_count: 2,
    lat: 23.3560,
    lng: 85.3340,
    district: 'Ranchi',
    submitted_by: 'Priya Singh',
  },
  {
    id: 'P005',
    title: 'Illegal dumping of industrial waste near Subarnarekha river',
    description: 'A factory is reportedly dumping chemical waste near the river bank at night, killing fish and damaging crops.',
    domain: 'Environment',
    priority_score: 9.5,
    status: 'In Progress',
    duplicate_count: 6,
    lat: 22.7533,
    lng: 85.8074,
    district: 'Seraikela',
    submitted_by: 'Arjun Mahato',
  },
  {
    id: 'P006',
    title: 'Community sanitation facility needs urgent repair in Pakur block',
    description: 'The facility has no running water and broken drainage, affecting nearby homes and schoolchildren.',
    domain: 'Water Resources',
    priority_score: 6.5,
    status: 'Submitted',
    duplicate_count: 8,
    lat: 24.6361,
    lng: 87.8427,
    district: 'Pakur',
    submitted_by: 'Lalita Hansda',
  },
  {
    id: 'P007',
    title: 'Weaving cooperative struggling — no market linkage',
    description: 'A 40-member tribal weaving cooperative produces quality Tussar silk but has no platform to sell beyond local haats.',
    domain: 'Rural Livelihoods',
    priority_score: 4.5,
    status: 'Submitted',
    duplicate_count: 1,
    lat: 23.7580,
    lng: 84.9040,
    district: 'Lohardaga',
    submitted_by: 'Champa Oraon',
  },
  {
    id: 'P008',
    title: 'Government office delays — BPL card renewal pending 8 months',
    description: 'Multiple families report BPL cards not renewed despite repeated visits. Officials demand informal fees.',
    domain: 'Public Administration',
    priority_score: 5.5,
    status: 'Submitted',
    duplicate_count: 5,
    lat: 23.6650,
    lng: 85.4500,
    district: 'Hazaribagh',
    submitted_by: 'Vikram Yadav',
  },
]

const MOCK_STATS = {
  total_problems: 127,
  universities_engaged: 8,
  industries_engaged: 14,
  by_domain: {
    'Water Management': 28,
    'Education': 22,
    'Healthcare': 19,
    'Environment': 17,
    'Urban Infrastructure': 12,
    'Sanitation': 10,
    'Rural Livelihoods': 8,
    'Public Service Delivery': 5,
    'Agriculture': 4,
    'Accessibility': 2,
  },
  by_district: {
    'Ranchi': 34,
    'Dhanbad': 22,
    'Hazaribagh': 18,
    'Seraikela': 14,
    'Chatra': 12,
    'Pakur': 10,
    'Lohardaga': 9,
    'Other': 8,
  },
  by_status: {
    'new': 58,
    'in-progress': 42,
    'resolved': 21,
    'duplicate': 6,
  },
}

const MOCK_UNIVERSITIES = [
  { id: 'U001', name: 'IIT (ISM) Dhanbad', domains: ['Environment', 'Sanitation', 'Water Management'] },
  { id: 'U002', name: 'BIT Mesra', domains: ['Urban Infrastructure', 'Accessibility', 'Sanitation'] },
  { id: 'U003', name: 'Ranchi University', domains: ['Education', 'Public Service Delivery', 'Rural Livelihoods'] },
  { id: 'U004', name: 'Birsa Agricultural University', domains: ['Agriculture', 'Rural Livelihoods'] },
]

// ─── Real fetch helpers ────────────────────────────────────────────────────────

async function fetchJson(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  return res.json()
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * POST /problems
 * body: { title, description, photo_url, lat, lng, submitted_by }
 */
export async function submitProblem(body) {
  if (USE_MOCK) {
    await delay(900)
    const newProblem = {
      id: `P${String(MOCK_PROBLEMS.length + 1).padStart(3, '0')}`,
      ...body,
      domain: 'Public Administration', // classifier assigns real domain
      priority_score: 2.0,
      status: 'Submitted',
      duplicate_count: 1,
      district: body.district ?? 'Unknown',
    }
    MOCK_PROBLEMS.push(newProblem)
    return newProblem
  }
  return fetchJson('/problems', { method: 'POST', body: JSON.stringify(body) })
}

/**
 * GET /problems?domain=&district=&status=
 */
export async function getProblems({ domain = '', district = '', status = '' } = {}) {
  if (USE_MOCK) {
    await delay(400)
    return MOCK_PROBLEMS.filter(p => {
      if (domain   && p.domain   !== domain)   return false
      if (district && p.district !== district) return false
      if (status   && p.status   !== status)   return false
      return true
    })
  }
  const params = new URLSearchParams()
  if (domain)   params.set('domain', domain)
  if (district) params.set('district', district)
  if (status)   params.set('status', status)
  return fetchJson(`/problems?${params}`)
}

/**
 * GET /problems/:id
 */
export async function getProblem(id) {
  if (USE_MOCK) {
    await delay(200)
    return MOCK_PROBLEMS.find(p => p.id === id) ?? null
  }
  return fetchJson(`/problems/${id}`)
}

/**
 * GET /problems/:id/suggested-universities
 */
export async function getSuggestedUniversities(problemId) {
  if (USE_MOCK) {
    await delay(300)
    const problem = MOCK_PROBLEMS.find(p => p.id === problemId)
    if (!problem) return []
    return MOCK_UNIVERSITIES.filter(u => u.domains.includes(problem.domain))
  }
  return fetchJson(`/problems/${problemId}/suggested-universities`)
}

/**
 * PATCH /problems/:id/status
 * body: { status }
 */
export async function updateProblemStatus(id, status) {
  if (USE_MOCK) {
    await delay(300)
    const p = MOCK_PROBLEMS.find(p => p.id === id)
    if (p) p.status = status
    return p
  }
  return fetchJson(`/problems/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}

/**
 * POST /universities/:id/assign
 * body: { problem_id }
 */
export async function assignProblemToUniversity(universityId, problemId) {
  if (USE_MOCK) {
    await delay(300)
    return { success: true }
  }
  return fetchJson(`/universities/${universityId}/assign`, {
    method: 'POST',
    body: JSON.stringify({ problem_id: problemId }),
  })
}

/**
 * GET /dashboard/stats
 */
export async function getDashboardStats() {
  if (USE_MOCK) {
    await delay(500)
    return MOCK_STATS
  }
  return fetchJson('/dashboard/stats')
}

/**
 * POST /industry/interest
 * body: { problem_id, industry_name }
 */
export async function postIndustryInterest(problemId, industryName) {
  if (USE_MOCK) {
    await delay(400)
    return { success: true }
  }
  return fetchJson('/industry/interest', {
    method: 'POST',
    body: JSON.stringify({ problem_id: problemId, industry_name: industryName }),
  })
}

// ─── Nominatim reverse-geocode ────────────────────────────────────────────────

/**
 * Reverse-geocode a lat/lng → district name via free Nominatim API.
 * No API key required.
 */
export async function reverseGeocode(lat, lng) {
  const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10&addressdetails=1`
  const res = await fetch(url, {
    headers: { 'Accept-Language': 'en', 'User-Agent': 'ImpactVerse/1.0' },
  })
  if (!res.ok) throw new Error('Nominatim error')
  const data = await res.json()
  // Nominatim returns county / state_district / suburb depending on region
  return (
    data.address?.county       ??
    data.address?.state_district ??
    data.address?.suburb       ??
    data.address?.city         ??
    data.address?.town         ??
    'Unknown district'
  )
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export const DOMAINS = [
  'Education',
  'Agriculture',
  'Healthcare',
  'Water Resources',
  'Environment',
  'Energy',
  'Urban Development',
  'Accessibility',
  'Public Administration',
  'Rural Livelihoods',
]

export const STATUSES = ['Submitted', 'Assigned to University', 'In Progress', 'Resolved']

export const DISTRICTS = [
  'Ranchi', 'Dhanbad', 'Hazaribagh', 'Seraikela', 'Chatra',
  'Pakur', 'Lohardaga', 'Giridih', 'Bokaro', 'Dumka',
]
