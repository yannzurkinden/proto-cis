import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MainLayout } from '@/components/layout/MainLayout'
import { useAuthStore } from '@/stores/authStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30000 },
  },
})

// Lazy-load pages
const LoginPage = lazy(() =>
  import('@/pages/auth/LoginPage').then((m) => ({ default: m.LoginPage }))
)
const DashboardPage = lazy(() =>
  import('@/pages/dashboard/DashboardPage').then((m) => ({ default: m.DashboardPage }))
)
const BeneficiaryListPage = lazy(() =>
  import('@/pages/beneficiaries/BeneficiaryListPage').then((m) => ({
    default: m.BeneficiaryListPage,
  }))
)
const BeneficiaryDetailPage = lazy(() =>
  import('@/pages/beneficiaries/BeneficiaryDetailPage').then((m) => ({
    default: m.BeneficiaryDetailPage,
  }))
)
const BeneficiaryFormPage = lazy(() =>
  import('@/pages/beneficiaries/BeneficiaryFormPage').then((m) => ({
    default: m.BeneficiaryFormPage,
  }))
)
const PAIDetailPage = lazy(() =>
  import('@/pages/pais/PAIDetailPage').then((m) => ({ default: m.PAIDetailPage }))
)
const PAIFormPage = lazy(() =>
  import('@/pages/pais/PAIFormPage').then((m) => ({ default: m.PAIFormPage }))
)
const ObjectiveListPage = lazy(() =>
  import('@/pages/objectives/ObjectiveListPage').then((m) => ({
    default: m.ObjectiveListPage,
  }))
)
const ObjectiveDetailPage = lazy(() =>
  import('@/pages/objectives/ObjectiveDetailPage').then((m) => ({
    default: m.ObjectiveDetailPage,
  }))
)
const JournalListPage = lazy(() =>
  import('@/pages/journal/JournalListPage').then((m) => ({
    default: m.JournalListPage,
  }))
)
const JournalEntryPage = lazy(() =>
  import('@/pages/journal/JournalEntryPage').then((m) => ({
    default: m.JournalEntryPage,
  }))
)
const JournalFormPage = lazy(() =>
  import('@/pages/journal/JournalFormPage').then((m) => ({
    default: m.JournalFormPage,
  }))
)
const DocumentListPage = lazy(() =>
  import('@/pages/documents/DocumentListPage').then((m) => ({
    default: m.DocumentListPage,
  }))
)
const TimeTrackingPage = lazy(() =>
  import('@/pages/time/TimeTrackingPage').then((m) => ({
    default: m.TimeTrackingPage,
  }))
)
const SkillsPage = lazy(() =>
  import('@/pages/skills/SkillsPage').then((m) => ({ default: m.SkillsPage }))
)
const AdminPage = lazy(() =>
  import('@/pages/admin/AdminPage').then((m) => ({ default: m.AdminPage }))
)
const ReportsPage = lazy(() =>
  import('@/pages/reports/ReportsPage').then((m) => ({ default: m.ReportsPage }))
)
const NotificationsPage = lazy(() =>
  import('@/pages/notifications/NotificationsPage').then((m) => ({
    default: m.NotificationsPage,
  }))
)
const NotFoundPage = lazy(() =>
  import('@/pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage }))
)

function ProtectedRoute({
  children,
  roles,
}: {
  children: React.ReactNode
  roles?: string[]
}) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (roles && user && !roles.includes(user.role))
    return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

function LoadingFallback() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<DashboardPage />} />

              {/* Beneficiaries */}
              <Route path="/beneficiaries" element={<BeneficiaryListPage />} />
              <Route path="/beneficiaries/new" element={<BeneficiaryFormPage />} />
              <Route path="/beneficiaries/:id" element={<BeneficiaryDetailPage />} />
              <Route path="/beneficiaries/:id/edit" element={<BeneficiaryFormPage />} />

              {/* PAI */}
              <Route
                path="/beneficiaries/:beneficiaryId/pais/new"
                element={<PAIFormPage />}
              />
              <Route
                path="/beneficiaries/:beneficiaryId/pais/:paiId"
                element={<PAIDetailPage />}
              />
              <Route
                path="/beneficiaries/:beneficiaryId/pais/:paiId/edit"
                element={<PAIFormPage />}
              />

              {/* Time & Skills */}
              <Route path="/beneficiaries/:id/time" element={<TimeTrackingPage />} />
              <Route path="/beneficiaries/:id/skills" element={<SkillsPage />} />

              {/* Objectives */}
              <Route path="/objectives" element={<ObjectiveListPage />} />
              <Route path="/objectives/:id" element={<ObjectiveDetailPage />} />

              {/* Journal */}
              <Route path="/journal" element={<JournalListPage />} />
              <Route path="/journal/new" element={<JournalFormPage />} />
              <Route path="/journal/:id" element={<JournalEntryPage />} />
              <Route path="/journal/:id/edit" element={<JournalFormPage />} />

              {/* Documents */}
              <Route path="/documents" element={<DocumentListPage />} />

              {/* Notifications */}
              <Route path="/notifications" element={<NotificationsPage />} />

              {/* Reports (management) */}
              <Route
                path="/reports"
                element={
                  <ProtectedRoute roles={['ADMIN', 'RUA', 'RES']}>
                    <ReportsPage />
                  </ProtectedRoute>
                }
              />

              {/* Admin */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute roles={['ADMIN', 'RUA']}>
                    <AdminPage />
                  </ProtectedRoute>
                }
              />
            </Route>

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
