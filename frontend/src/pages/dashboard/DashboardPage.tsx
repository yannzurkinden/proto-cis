import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Users, Target, AlertTriangle, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useAuthStore } from '@/stores/authStore'
import { dashboardApi } from '@/api/dashboard'
import { formatDate } from '@/lib/utils'

export function DashboardPage() {
  const { user } = useAuthStore()
  const isManagement = user?.role === 'ADMIN' || user?.role === 'RUA' || user?.role === 'RES'

  const { data: mspData, isLoading: mspLoading } = useQuery({
    queryKey: ['dashboard', 'msp'],
    queryFn: () => dashboardApi.getMSPDashboard(),
    enabled: !isManagement,
  })

  const { data: managementData, isLoading: managementLoading } = useQuery({
    queryKey: ['dashboard', 'management'],
    queryFn: () => dashboardApi.getManagementDashboard(),
    enabled: isManagement,
  })

  if (mspLoading || managementLoading) {
    return <div className="flex items-center justify-center p-8">Chargement...</div>
  }

  if (isManagement && managementData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Tableau de bord</h1>
          <p className="text-muted-foreground">Vue d'ensemble de l'activité</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Bénéficiaires actifs</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{managementData.summary.active_beneficiaries}</div>
              <p className="text-xs text-muted-foreground">
                sur {managementData.summary.total_beneficiaries} total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Objectifs total</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{managementData.objectives_overview.total}</div>
              <p className="text-xs text-muted-foreground">
                {managementData.objectives_overview.overdue} en retard
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Taux de réussite</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {managementData.objectives_overview.achievement_rate.toFixed(1)}%
              </div>
              <Progress value={managementData.objectives_overview.achievement_rate} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Alertes</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{managementData.alerts.length}</div>
              <p className="text-xs text-muted-foreground">à traiter</p>
            </CardContent>
          </Card>
        </div>

        {managementData.alerts.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Alertes récentes</CardTitle>
              <CardDescription>Actions nécessitant votre attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {managementData.alerts.map((alert, index) => (
                  <div key={index} className="flex items-center gap-4">
                    <AlertTriangle className="h-5 w-5 text-destructive" />
                    <div className="flex-1">
                      <p className="font-medium">{alert.beneficiary_name}</p>
                      <p className="text-sm text-muted-foreground">{alert.message}</p>
                    </div>
                    <Link to={`/beneficiaries/${alert.beneficiary_id}`}>
                      <Badge variant="outline">Voir</Badge>
                    </Link>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  if (mspData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Bonjour, {user?.first_name}</h1>
          <p className="text-muted-foreground">Voici votre activité du jour</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Mes bénéficiaires</CardTitle>
              <CardDescription>{mspData.my_beneficiaries.length} bénéficiaires suivis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mspData.my_beneficiaries.map((beneficiary) => (
                  <Link
                    key={beneficiary.id}
                    to={`/beneficiaries/${beneficiary.id}`}
                    className="flex items-center gap-4 rounded-lg border p-3 transition-colors hover:bg-accent"
                  >
                    <Avatar>
                      <AvatarFallback>
                        {beneficiary.name.split(' ').map((n) => n[0]).join('').toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <p className="font-medium">{beneficiary.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {beneficiary.objectives_overdue > 0 ? (
                          <span className="text-destructive">
                            {beneficiary.objectives_overdue} objectifs en retard
                          </span>
                        ) : (
                          'Aucun retard'
                        )}
                      </p>
                    </div>
                    <Badge variant={beneficiary.status === 'active' ? 'success' : 'secondary'}>
                      {beneficiary.status === 'active' ? 'Actif' : beneficiary.status}
                    </Badge>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Rappels du jour</CardTitle>
              <CardDescription>Actions à effectuer</CardDescription>
            </CardHeader>
            <CardContent>
              {mspData.today_reminders.length === 0 ? (
                <p className="text-muted-foreground">Aucun rappel pour aujourd'hui</p>
              ) : (
                <div className="space-y-4">
                  {mspData.today_reminders.map((reminder, index) => (
                    <div key={index} className="flex items-center gap-4 rounded-lg border p-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-500" />
                      <div className="flex-1">
                        <p className="font-medium">{reminder.beneficiary_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {reminder.objective_title || reminder.message}
                        </p>
                        {reminder.due_date && (
                          <p className="text-xs text-destructive">
                            Échéance: {formatDate(reminder.due_date)}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Journal récent</CardTitle>
            <CardDescription>Dernières entrées du journal</CardDescription>
          </CardHeader>
          <CardContent>
            {mspData.recent_journal_entries.length === 0 ? (
              <p className="text-muted-foreground">Aucune entrée récente</p>
            ) : (
              <div className="space-y-4">
                {mspData.recent_journal_entries.map((entry) => (
                  <Link
                    key={entry.id}
                    to={`/journal/${entry.id}`}
                    className="block rounded-lg border p-3 transition-colors hover:bg-accent"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{entry.beneficiary_name}</span>
                      <span className="text-sm text-muted-foreground">
                        {formatDate(entry.entry_date)}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{entry.title}</p>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return null
}
