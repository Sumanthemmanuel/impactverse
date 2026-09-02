/**
 * i18n.js — ImpactVerse bilingual system (English + Hindi)
 *
 * Usage:
 *   import { useTranslation } from '../i18n.js'
 *   const { t, lang, setLang } = useTranslation()
 *   <p>{t('nav.citizen')}</p>
 */

import React, { createContext, useContext, useState } from 'react'

export const translations = {
  en: {
    // ── Nav ────────────────────────────────────────────────────────
    'nav.brand':       'ImpactVerse',
    'nav.tagline':     'Citizen · University · Government',
    'nav.citizen':     'Citizen Portal',
    'nav.university':  'University',
    'nav.admin':       'Admin',

    // ── Home / Landing ─────────────────────────────────────────────
    'home.hero.title':   'Bridging Citizens & Government',
    'home.hero.sub':     'Report local problems. Track resolutions. Build a better Jharkhand — together.',
    'home.hero.cta1':    'Report a Problem',
    'home.hero.cta2':    'View Public Tracker',
    'home.stat1.label':  'Problems Reported',
    'home.stat2.label':  'Districts Covered',
    'home.stat3.label':  'Universities Engaged',
    'home.stat4.label':  'Resolved',

    // ── Submission Form ────────────────────────────────────────────
    'submit.hero.badge':    'Citizen Report',
    'submit.hero.title':    'Report a Community Problem',
    'submit.hero.sub':      'Your report reaches the right authorities, universities, and industries who can act. Every submission matters.',
    'submit.card1.title':   'Problem Details',
    'submit.card1.sub':     'Be specific — judges and authorities read every word.',
    'submit.title.label':   'Title',
    'submit.title.ph':      'e.g. Contaminated borewell water near Laxmi Nagar',
    'submit.desc.label':    'Description',
    'submit.desc.ph':       'Describe the problem — when it started, who is affected, what has been tried so far…',
    'submit.cat.label':     'Category',
    'submit.cat.ph':        'Select a domain…',
    'submit.cat.note':      'The AI classifier will confirm or refine this after submission.',
    'submit.loc.title':     'Location',
    'submit.loc.sub':       'Click anywhere on the map to drop a pin. Your district will be filled in automatically.',
    'submit.lat.label':     'Latitude',
    'submit.lng.label':     'Longitude',
    'submit.map.ph':        'Click map',
    'submit.map.err':       'Click on the map to drop a location pin',
    'submit.district.label':'District',
    'submit.district.ph':   'Auto-filled or type manually',
    'submit.detecting':     'Detecting district…',
    'submit.photo.title':   'Photo & Contact',
    'submit.photo.sub':     'Optional photo helps authorities verify the issue faster.',
    'submit.photo.label':   'Photo (optional)',
    'submit.photo.hint':    'Click to upload or drag and drop',
    'submit.photo.types':   'PNG, JPG, WEBP up to 10MB',
    'submit.name.label':    'Your Name',
    'submit.name.ph':       'Full name',
    'submit.disclaimer':    'All reports are public and reviewed by verified stakeholders.',
    'submit.btn':           'Submit Report',
    'submit.success.title': 'Problem Reported!',
    'submit.success.sub':   'Your report has been submitted and will be reviewed by the relevant authorities.',
    'submit.success.id':    'Report ID',
    'submit.success.domain':'Assigned Domain',
    'submit.success.status':'Status',
    'submit.success.score': 'Priority Score',
    'submit.success.dist':  'District',
    'submit.success.more':  'Submit Another',
    'submit.success.track': 'View Tracker',

    // ── Tracker ────────────────────────────────────────────────────
    'tracker.title':         'Problem Tracker',
    'tracker.sub':           'problems found',
    'tracker.sub1':          'problem found',
    'tracker.loading':       'Loading…',
    'tracker.filter.domain': 'All Domains',
    'tracker.filter.dist':   'All Districts',
    'tracker.filter.status': 'All Statuses',
    'tracker.clear':         'Clear filters',
    'tracker.empty.title':   'No problems match your filters.',
    'tracker.empty.sub':     'Try clearing some filters.',
    'tracker.others':        'others',
    'tracker.report.btn':    'Report a Problem',
    'tracker.priority':      'Priority',

    // ── Status labels ──────────────────────────────────────────────
    'status.new':          'New',
    'status.in-progress':  'In Progress',
    'status.resolved':     'Resolved',
    'status.duplicate':    'Duplicate',

    // ── Admin ──────────────────────────────────────────────────────
    'admin.title':           'Admin Dashboard',
    'admin.sub':             'Real-time overview of all reported problems across Jharkhand.',
    'admin.stat.total':      'Total Problems',
    'admin.stat.total.sub':  'Across all domains',
    'admin.stat.uni':        'Universities Engaged',
    'admin.stat.uni.sub':    'Working on problems',
    'admin.stat.ind':        'Industries Engaged',
    'admin.stat.ind.sub':    'Registered interest',
    'admin.stat.res':        'Resolved',
    'admin.chart.domain':    'Problems by Domain',
    'admin.chart.domain.sub':'Distribution across 10 thematic areas',
    'admin.chart.dist':      'Problems by District',
    'admin.chart.dist.sub':  'Top districts by reported volume',
    'admin.chart.status':    'Problems by Status',
    'admin.chart.status.sub':'Pipeline health at a glance',
    'admin.industry.title':  'Industry Interest',
    'admin.industry.sub':    "Register an industry's interest in a specific problem.",
    'admin.industry.prob':   'Problem',
    'admin.industry.prob.ph':'Select a problem…',
    'admin.industry.name':   'Industry / Company Name',
    'admin.industry.name.ph':'e.g. Tata Steel, SAIL, Infosys',
    'admin.industry.btn':    'Register Interest',
    'admin.table.title':     'Recent Reports',
    'admin.table.sub':       'Latest submissions from citizens',
    'admin.table.id':        'ID',
    'admin.table.title2':    'Title',
    'admin.table.domain':    'Domain',
    'admin.table.dist':      'District',
    'admin.table.priority':  'Priority',
    'admin.table.status':    'Status',
    'admin.loading':         'Loading dashboard…',

    // ── University ─────────────────────────────────────────────────
    'uni.title':             'University Dashboard',
    'uni.sub':               'Problems assigned to your institution based on your domain expertise.',
    'uni.profile.title':     'Institution Profile',
    'uni.profile.name':      'IIT (ISM) Dhanbad',
    'uni.profile.domains':   'Active Domains',
    'uni.profile.assigned':  'Assigned Problems',
    'uni.filter.status':     'Filter by Status',
    'uni.all':               'All',
    'uni.card.priority':     'Priority',
    'uni.card.district':     'District',
    'uni.card.duplicates':   'duplicates',
    'uni.card.team.label':   'Team Members',
    'uni.card.team.ph':      'Enter comma-separated names…',
    'uni.card.team.saved':   'Team saved locally',
    'uni.card.team.btn':     'Save Team',
    'uni.card.start.btn':    'Form Team & Start',
    'uni.card.inprogress':   'In Progress',
    'uni.suggested.title':   'Suggested for your domain',
    'uni.suggest.assign':    'Assign to Us',
    'uni.loading':           'Loading problems…',
    'uni.empty.title':       'No assigned problems yet.',
    'uni.empty.sub':         'Check back soon or explore suggested problems below.',
  },

  hi: {
    // ── Nav ────────────────────────────────────────────────────────
    'nav.brand':       'इम्पैक्टवर्स',
    'nav.tagline':     'नागरिक · विश्वविद्यालय · सरकार',
    'nav.citizen':     'नागरिक पोर्टल',
    'nav.university':  'विश्वविद्यालय',
    'nav.admin':       'प्रशासन',

    // ── Home / Landing ─────────────────────────────────────────────
    'home.hero.title':   'नागरिकों और सरकार के बीच सेतु',
    'home.hero.sub':     'स्थानीय समस्याएँ रिपोर्ट करें। समाधान ट्रैक करें। मिलकर बेहतर झारखंड बनाएं।',
    'home.hero.cta1':    'समस्या रिपोर्ट करें',
    'home.hero.cta2':    'सार्वजनिक ट्रैकर देखें',
    'home.stat1.label':  'समस्याएँ रिपोर्ट हुईं',
    'home.stat2.label':  'जिले कवर हुए',
    'home.stat3.label':  'विश्वविद्यालय जुड़े',
    'home.stat4.label':  'हल हुईं',

    // ── Submission Form ────────────────────────────────────────────
    'submit.hero.badge':    'नागरिक रिपोर्ट',
    'submit.hero.title':    'सामुदायिक समस्या रिपोर्ट करें',
    'submit.hero.sub':      'आपकी रिपोर्ट सही अधिकारियों, विश्वविद्यालयों और उद्योगों तक पहुँचती है। हर रिपोर्ट मायने रखती है।',
    'submit.card1.title':   'समस्या विवरण',
    'submit.card1.sub':     'विशिष्ट रहें — न्यायाधीश और अधिकारी हर शब्द पढ़ते हैं।',
    'submit.title.label':   'शीर्षक',
    'submit.title.ph':      'जैसे: लक्ष्मी नगर के पास बोरवेल का पानी दूषित',
    'submit.desc.label':    'विवरण',
    'submit.desc.ph':       'समस्या का वर्णन करें — कब शुरू हुई, कौन प्रभावित है, अब तक क्या प्रयास हुए…',
    'submit.cat.label':     'श्रेणी',
    'submit.cat.ph':        'एक क्षेत्र चुनें…',
    'submit.cat.note':      'AI वर्गीकरणकर्ता सबमिशन के बाद इसे पुष्ट या परिष्कृत करेगा।',
    'submit.loc.title':     'स्थान',
    'submit.loc.sub':       'पिन डालने के लिए मानचित्र पर कहीं भी क्लिक करें। आपका जिला स्वतः भर जाएगा।',
    'submit.lat.label':     'अक्षांश',
    'submit.lng.label':     'देशांतर',
    'submit.map.ph':        'मानचित्र पर क्लिक करें',
    'submit.map.err':       'स्थान पिन लगाने के लिए मानचित्र पर क्लिक करें',
    'submit.district.label':'जिला',
    'submit.district.ph':   'स्वतः भरेगा या मैन्युअल टाइप करें',
    'submit.detecting':     'जिला पहचाना जा रहा है…',
    'submit.photo.title':   'फ़ोटो और संपर्क',
    'submit.photo.sub':     'वैकल्पिक फ़ोटो अधिकारियों को समस्या तेज़ी से सत्यापित करने में मदद करती है।',
    'submit.photo.label':   'फ़ोटो (वैकल्पिक)',
    'submit.photo.hint':    'अपलोड करने के लिए क्लिक करें या खींचें और छोड़ें',
    'submit.photo.types':   'PNG, JPG, WEBP — अधिकतम 10MB',
    'submit.name.label':    'आपका नाम',
    'submit.name.ph':       'पूरा नाम',
    'submit.disclaimer':    'सभी रिपोर्ट सार्वजनिक हैं और सत्यापित हितधारकों द्वारा समीक्षा की जाती हैं।',
    'submit.btn':           'रिपोर्ट सबमिट करें',
    'submit.success.title': 'समस्या रिपोर्ट हुई!',
    'submit.success.sub':   'आपकी रिपोर्ट सबमिट हो गई है और संबंधित अधिकारियों द्वारा समीक्षा की जाएगी।',
    'submit.success.id':    'रिपोर्ट ID',
    'submit.success.domain':'असाइन किया डोमेन',
    'submit.success.status':'स्थिति',
    'submit.success.score': 'प्राथमिकता स्कोर',
    'submit.success.dist':  'जिला',
    'submit.success.more':  'एक और सबमिट करें',
    'submit.success.track': 'ट्रैकर देखें',

    // ── Tracker ────────────────────────────────────────────────────
    'tracker.title':         'समस्या ट्रैकर',
    'tracker.sub':           'रिपोर्ट मिलीं',
    'tracker.sub1':          'रिपोर्ट मिली',
    'tracker.loading':       'लोड हो रहा है…',
    'tracker.filter.domain': 'सभी क्षेत्र',
    'tracker.filter.dist':   'सभी जिले',
    'tracker.filter.status': 'सभी स्थितियाँ',
    'tracker.clear':         'फ़िल्टर हटाएँ',
    'tracker.empty.title':   'कोई समस्या आपके फ़िल्टर से मेल नहीं खाती।',
    'tracker.empty.sub':     'कुछ फ़िल्टर हटाने का प्रयास करें।',
    'tracker.others':        'अन्य',
    'tracker.report.btn':    'समस्या रिपोर्ट करें',
    'tracker.priority':      'प्राथमिकता',

    // ── Status labels ──────────────────────────────────────────────
    'status.new':          'नया',
    'status.in-progress':  'प्रगति में',
    'status.resolved':     'हल हुआ',
    'status.duplicate':    'डुप्लीकेट',

    // ── Admin ──────────────────────────────────────────────────────
    'admin.title':           'प्रशासन डैशबोर्ड',
    'admin.sub':             'झारखंड भर में सभी रिपोर्ट की गई समस्याओं का रियल-टाइम अवलोकन।',
    'admin.stat.total':      'कुल समस्याएँ',
    'admin.stat.total.sub':  'सभी क्षेत्रों में',
    'admin.stat.uni':        'जुड़े विश्वविद्यालय',
    'admin.stat.uni.sub':    'समस्याओं पर काम कर रहे हैं',
    'admin.stat.ind':        'जुड़े उद्योग',
    'admin.stat.ind.sub':    'रुचि दर्ज की',
    'admin.stat.res':        'हल हुईं',
    'admin.chart.domain':    'डोमेन के अनुसार समस्याएँ',
    'admin.chart.domain.sub':'10 विषयगत क्षेत्रों में वितरण',
    'admin.chart.dist':      'जिले के अनुसार समस्याएँ',
    'admin.chart.dist.sub':  'रिपोर्ट मात्रा के अनुसार शीर्ष जिले',
    'admin.chart.status':    'स्थिति के अनुसार समस्याएँ',
    'admin.chart.status.sub':'पाइपलाइन स्वास्थ्य एक नज़र में',
    'admin.industry.title':  'उद्योग रुचि',
    'admin.industry.sub':    'किसी विशेष समस्या में उद्योग की रुचि दर्ज करें।',
    'admin.industry.prob':   'समस्या',
    'admin.industry.prob.ph':'एक समस्या चुनें…',
    'admin.industry.name':   'उद्योग / कंपनी का नाम',
    'admin.industry.name.ph':'जैसे: टाटा स्टील, SAIL, इन्फोसिस',
    'admin.industry.btn':    'रुचि दर्ज करें',
    'admin.table.title':     'हाल की रिपोर्ट',
    'admin.table.sub':       'नागरिकों के नवीनतम सबमिशन',
    'admin.table.id':        'ID',
    'admin.table.title2':    'शीर्षक',
    'admin.table.domain':    'डोमेन',
    'admin.table.dist':      'जिला',
    'admin.table.priority':  'प्राथमिकता',
    'admin.table.status':    'स्थिति',
    'admin.loading':         'डैशबोर्ड लोड हो रहा है…',

    // ── University ─────────────────────────────────────────────────
    'uni.title':             'विश्वविद्यालय डैशबोर्ड',
    'uni.sub':               'आपके डोमेन विशेषज्ञता के आधार पर असाइन की गई समस्याएँ।',
    'uni.profile.title':     'संस्था प्रोफ़ाइल',
    'uni.profile.name':      'IIT (ISM) धनबाद',
    'uni.profile.domains':   'सक्रिय डोमेन',
    'uni.profile.assigned':  'असाइन की गई समस्याएँ',
    'uni.filter.status':     'स्थिति के अनुसार फ़िल्टर',
    'uni.all':               'सभी',
    'uni.card.priority':     'प्राथमिकता',
    'uni.card.district':     'जिला',
    'uni.card.duplicates':   'डुप्लीकेट',
    'uni.card.team.label':   'टीम के सदस्य',
    'uni.card.team.ph':      'अल्पविराम से अलग नाम दर्ज करें…',
    'uni.card.team.saved':   'टीम स्थानीय रूप से सहेजी गई',
    'uni.card.team.btn':     'टीम सहेजें',
    'uni.card.start.btn':    'टीम बनाएं और शुरू करें',
    'uni.card.inprogress':   'प्रगति में',
    'uni.suggested.title':   'आपके डोमेन के लिए सुझाई गई',
    'uni.suggest.assign':    'हमें असाइन करें',
    'uni.loading':           'समस्याएँ लोड हो रही हैं…',
    'uni.empty.title':       'अभी तक कोई असाइन की गई समस्या नहीं।',
    'uni.empty.sub':         'जल्द वापस देखें या नीचे सुझाई गई समस्याएँ देखें।',
  },
}

// ── Context ───────────────────────────────────────────────────────────────────
const I18nContext = createContext(null)

export function I18nProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem('iv_lang') || 'en')

  const switchLang = (l) => {
    setLang(l)
    localStorage.setItem('iv_lang', l)
  }

  const t = (key) => translations[lang]?.[key] ?? translations['en']?.[key] ?? key

  return (
    <I18nContext.Provider value={{ lang, setLang: switchLang, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useTranslation() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useTranslation must be used inside <I18nProvider>')
  return ctx
}
