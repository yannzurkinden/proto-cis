import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Target,
  BookOpen,
  FileText,
  ChevronLeft,
  BarChart3,
  Shield,
  Bell,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Bénéficiaires', href: '/beneficiaries', icon: Users },
  { name: 'Objectifs', href: '/objectives', icon: Target },
  { name: 'Journal', href: '/journal', icon: BookOpen },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Notifications', href: '/notifications', icon: Bell },
]

const managementNavigation = [
  { name: 'Rapports', href: '/reports', icon: BarChart3 },
]

const adminNavigation = [
  { name: 'Administration', href: '/admin', icon: Shield },
]

export function Sidebar() {
  const location = useLocation()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { user } = useAuthStore()

  const isAdmin = user?.role === 'ADMIN' || user?.role === 'RUA'
  const isManagement =
    user?.role === 'ADMIN' || user?.role === 'RUA' || user?.role === 'RES'

  const renderNavItems = (items: typeof navigation) =>
    items.map((item) => {
      const isActive = location.pathname.startsWith(item.href)
      return (
        <Link
          key={item.name}
          to={item.href}
          className={cn(
            'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
            isActive
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
          )}
        >
          <item.icon className="h-5 w-5 flex-shrink-0" />
          {sidebarOpen && <span>{item.name}</span>}
        </Link>
      )
    })

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen border-r bg-background transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-16'
      )}
    >
      <div className="flex h-16 items-center justify-between border-b px-4">
        {sidebarOpen && (
          <Link to="/dashboard" className="flex items-center gap-2">
            <span className="text-xl font-bold text-primary">CIS</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className={cn(!sidebarOpen && 'mx-auto')}
        >
          <ChevronLeft
            className={cn(
              'h-5 w-5 transition-transform',
              !sidebarOpen && 'rotate-180'
            )}
          />
        </Button>
      </div>

      <nav className="space-y-1 p-2">
        {renderNavItems(navigation)}

        {isManagement && (
          <>
            <div className="my-4 border-t" />
            {renderNavItems(managementNavigation)}
          </>
        )}

        {isAdmin && (
          <>
            {!isManagement && <div className="my-4 border-t" />}
            {renderNavItems(adminNavigation)}
          </>
        )}
      </nav>
    </aside>
  )
}
