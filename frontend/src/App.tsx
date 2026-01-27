import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from '@/components/layout/MainLayout'
import { LoginPage } from '@/pages/auth/LoginPage'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { BeneficiaryListPage } from '@/pages/beneficiaries/BeneficiaryListPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/beneficiaries" element={<BeneficiaryListPage />} />
          <Route path="/beneficiaries/:id" element={<div>Beneficiary Detail</div>} />
          <Route path="/beneficiaries/new" element={<div>New Beneficiary</div>} />
          <Route path="/objectives" element={<div>Objectives List</div>} />
          <Route path="/objectives/:id" element={<div>Objective Detail</div>} />
          <Route path="/journal" element={<div>Journal List</div>} />
          <Route path="/journal/:id" element={<div>Journal Entry Detail</div>} />
          <Route path="/documents" element={<div>Documents List</div>} />
          <Route path="/settings" element={<div>Settings</div>} />
        </Route>

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
