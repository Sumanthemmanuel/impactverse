import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { I18nProvider } from './i18n.jsx'
import Nav from './components/Nav.jsx'
import LandingPage from './pages/Landing.jsx'
import SubmissionForm from './pages/citizen/SubmissionForm.jsx'
import PublicTracker from './pages/citizen/PublicTracker.jsx'
import AdminDashboard from './pages/admin/AdminDashboard.jsx'
import UniversityDashboard from './pages/university/UniversityDashboard.jsx'

function PageWrapper({ children }) {
  const location = useLocation()
  const isHome = location.pathname === '/'
  
  return (
    <div className={`flex-1 ${!isHome ? 'pt-[90px]' : ''}`}>
      {children}
    </div>
  )
}

export default function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Nav />
          <PageWrapper>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/citizen" element={<SubmissionForm />} />
              <Route path="/citizen/tracker" element={<PublicTracker />} />
              <Route path="/university" element={<UniversityDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </PageWrapper>
        </div>
      </BrowserRouter>
    </I18nProvider>
  )
}
