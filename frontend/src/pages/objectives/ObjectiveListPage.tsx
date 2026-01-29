import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Target,
  Filter,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { objectivesApi, type ObjectiveFilters } from '@/api/objectives'
import { usePagination } from '@/hooks/usePagination'

function formatDateFr(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  try {
    return format(parseISO(dateStr), 'dd.MM.yyyy', { locale: fr })
  } catch {
    return dateStr
  }
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'achieved':
      return <Badge variant="success">Atteint</Badge>
    case 'in_progress':
      return <Badge variant="default">En cours</Badge>
    case 'pending':
      return <Badge variant="outline">En attente</Badge>
    case 'abandoned':
      return <Badge variant="secondary">Abandonne</Badge>
    default:
      return <Badge>{status}</Badge>
  }
}

function getTypeBadge(type: string) {
  switch (type) {
    case 'pai':
      return <Badge variant="default">PAI</Badge>
    case 'behavioral':
      return <Badge variant="warning">Comportemental</Badge>
    case 'operational':
      return <Badge variant="secondary">Operationnel</Badge>
    default:
      return <Badge>{type}</Badge>
  }
}

function getTermLabel(term: string) {
  switch (term) {
    case 'short':
      return 'Court'
    case 'medium':
      return 'Moyen'
    case 'long':
      return 'Long'
    default:
      return term
  }
}

function getPriorityBadge(priority: string) {
  switch (priority) {
    case 'high':
      return <Badge variant="destructive">Haute</Badge>
    case 'medium':
      return <Badge variant="warning">Moyenne</Badge>
    case 'low':
      return <Badge variant="outline">Basse</Badge>
    default:
      return <Badge>{priority}</Badge>
  }
}

export function ObjectiveListPage() {
  const navigate = useNavigate()
  const { pagination, setPage, setTotal } = usePagination(1, 20)
  const [showFilters, setShowFilters] = useState(false)

  const [filters, setFilters] = useState<ObjectiveFilters>({
    status: '',
    objective_type: '',
    term: '',
    overdue: undefined,
  })

  const queryFilters: ObjectiveFilters = {
    page: pagination.page,
    size: pagination.size,
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.objective_type ? { objective_type: filters.objective_type } : {}),
    ...(filters.term ? { term: filters.term } : {}),
    ...(filters.overdue !== undefined ? { overdue: filters.overdue } : {}),
  }

  const { data, isLoading } = useQuery({
    queryKey: ['objectives', queryFilters],
    queryFn: () => objectivesApi.list(queryFilters),
  })

  useEffect(() => {
    if (data) {
      setTotal(data.total, data.pages)
    }
  }, [data, setTotal])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Objectifs</h1>
          <p className="text-muted-foreground">
            Suivi de tous les objectifs des beneficiaires
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Filtres</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="mr-2 h-4 w-4" />
              {showFilters ? 'Masquer' : 'Afficher'}
            </Button>
          </div>
        </CardHeader>
        {showFilters && (
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div className="space-y-2">
                <Label>Statut</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={filters.status || ''}
                  onChange={(e) => {
                    setFilters({ ...filters, status: e.target.value })
                    setPage(1)
                  }}
                >
                  <option value="">Tous</option>
                  <option value="pending">En attente</option>
                  <option value="in_progress">En cours</option>
                  <option value="achieved">Atteint</option>
                  <option value="abandoned">Abandonne</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={filters.objective_type || ''}
                  onChange={(e) => {
                    setFilters({ ...filters, objective_type: e.target.value })
                    setPage(1)
                  }}
                >
                  <option value="">Tous</option>
                  <option value="pai">PAI</option>
                  <option value="behavioral">Comportemental</option>
                  <option value="operational">Operationnel</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Terme</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={filters.term || ''}
                  onChange={(e) => {
                    setFilters({ ...filters, term: e.target.value })
                    setPage(1)
                  }}
                >
                  <option value="">Tous</option>
                  <option value="short">Court terme</option>
                  <option value="medium">Moyen terme</option>
                  <option value="long">Long terme</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>En retard</Label>
                <div className="flex items-center gap-2 h-10">
                  <input
                    type="checkbox"
                    id="overdue-filter"
                    checked={filters.overdue === true}
                    onChange={(e) => {
                      setFilters({
                        ...filters,
                        overdue: e.target.checked ? true : undefined,
                      })
                      setPage(1)
                    }}
                  />
                  <Label htmlFor="overdue-filter" className="font-normal">
                    Afficher uniquement les retards
                  </Label>
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Results */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="ml-2">Chargement des objectifs...</span>
        </div>
      ) : !data?.items.length ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Target className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">Aucun objectif trouve</p>
            <p className="text-muted-foreground">
              Modifiez les filtres ou creez un nouveau PAI avec des objectifs.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Table */}
          <div className="rounded-md border">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="p-3 text-left text-sm font-medium">Beneficiaire</th>
                  <th className="p-3 text-left text-sm font-medium">Titre</th>
                  <th className="p-3 text-left text-sm font-medium">Type</th>
                  <th className="p-3 text-left text-sm font-medium">Terme</th>
                  <th className="p-3 text-left text-sm font-medium">Priorite</th>
                  <th className="p-3 text-left text-sm font-medium">Statut</th>
                  <th className="p-3 text-left text-sm font-medium">Progression</th>
                  <th className="p-3 text-left text-sm font-medium">Echeance</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((objective) => (
                  <tr
                    key={objective.id}
                    className="border-b transition-colors hover:bg-accent cursor-pointer"
                    onClick={() => navigate(`/objectives/${objective.id}`)}
                  >
                    <td className="p-3 text-sm">
                      {objective.beneficiary_name || '-'}
                    </td>
                    <td className="p-3 text-sm font-medium">
                      {objective.title}
                    </td>
                    <td className="p-3">{getTypeBadge(objective.objective_type)}</td>
                    <td className="p-3 text-sm">{getTermLabel(objective.term)}</td>
                    <td className="p-3">{getPriorityBadge(objective.priority)}</td>
                    <td className="p-3">{getStatusBadge(objective.status)}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-2 min-w-[120px]">
                        <Progress value={objective.progress} className="flex-1 h-2" />
                        <span className="text-xs font-medium w-8">{objective.progress}%</span>
                      </div>
                    </td>
                    <td className="p-3 text-sm">
                      {objective.due_date ? (
                        <span
                          className={
                            new Date(objective.due_date) < new Date()
                              ? 'text-destructive font-medium'
                              : ''
                          }
                        >
                          {formatDateFr(objective.due_date)}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data.pages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Page {pagination.page} sur {data.pages} ({data.total} resultats)
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={pagination.page === 1}
                  onClick={() => setPage(pagination.page - 1)}
                >
                  <ChevronLeft className="mr-1 h-4 w-4" />
                  Precedent
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={pagination.page >= data.pages}
                  onClick={() => setPage(pagination.page + 1)}
                >
                  Suivant
                  <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
