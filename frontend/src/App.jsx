import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { I18nProvider } from './i18n.js'
import Nav from './components/Nav.jsx'
import LandingPage from './pages/Landing.jsx'
import SubmissionForm from './pages/citizen/SubmissionForm.jsx'
import PublicTracker from './pages/citizen/PublicTracker.jsx'
import AdminDashboard from './pages/admin/AdminDashboard.jsx'
import UniversityDashboard from './pages/university/UniversityDashboard.jsx'

export default function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <div className="flex flex-col min-h-screen">
          <Nav />
          <div className="flex-1">
            <Routes>
              <Route path="/"                  element={<LandingPage />} />
              <Route path="/citizen"           element={<SubmissionForm />} />
              <Route path="/citizen/tracker"   element={<PublicTracker />} />
              <Route path="/university"        element={<UniversityDashboard />} />
              <Route path="/admin"             element={<AdminDashboard />} />
              {/* Catch-all */}
              <Route path="*"                  element={<Navigate to="/" replace />} />
            </Routes>
          </div>
          <footer className="bg-primary-900 text-primary-400 text-xs py-3 text-center">
            © 2026 ImpactVerse · Smart India Hackathon · Government of Jharkhand
          </footer>
        </div>
      </BrowserRouter>
    </I18nProvider>
  )
}
