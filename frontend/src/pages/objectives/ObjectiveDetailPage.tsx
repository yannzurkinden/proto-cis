import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ChevronLeft,
  Loader2,
  AlertTriangle,
  Target,
  CheckCircle2,
  Circle,
  Calendar,
  User,
  Flag,
  Clock,
  TrendingUp,
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { objectivesApi } from '@/api/objectives'

// ---- Helpers ----

function formatDateFr(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  try {
    return format(parseISO(dateStr), 'dd MMMM yyyy', { locale: fr })
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
      return 'Court terme'
    case 'medium':
      return 'Moyen terme'
    case 'long':
      return 'Long terme'
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

// ---- Component ----

export function ObjectiveDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const objectiveId = Number(id)

  const [progressValue, setProgressValue] = useState<string>('')
  const [progressNote, setProgressNote] = useState('')
  const [showProgressForm, setShowProgressForm] = useState(false)

  const {
    data: objective,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['objective', objectiveId],
    queryFn: () => objectivesApi.get(objectiveId),
    enabled: !!objectiveId && !isNaN(objectiveId),
  })

  // Progress mutation
  const progressMutation = useMutation({
    mutationFn: () =>
      objectivesApi.updateProgress(objectiveId, Number(progressValue), progressNote || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objective', objectiveId] })
      queryClient.invalidateQueries({ queryKey: ['objectives'] })
      setShowProgressForm(false)
      setProgressValue('')
      setProgressNote('')
    },
    onError: (err) => console.error('Erreur mise a jour progression:', err),
  })

  // Status mutation
  const statusMutation = useMutation({
    mutationFn: (newStatus: string) =>
      objectivesApi.updateStatus(objectiveId, newStatus),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objective', objectiveId] })
      queryClient.invalidateQueries({ queryKey: ['objectives'] })
    },
    onError: (err) => console.error('Erreur mise a jour statut:', err),
  })

  // Indicator toggle mutation
  const indicatorMutation = useMutation({
    mutationFn: (indicatorId: number) =>
      objectivesApi.achieveIndicator(objectiveId, indicatorId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objective', objectiveId] })
    },
    onError: (err) => console.error('Erreur mise a jour indicateur:', err),
  })

  // Action status toggle mutation
  const actionMutation = useMutation({
    mutationFn: ({ actionId, status }: { actionId: number; status: string }) =>
      objectivesApi.updateAction(objectiveId, actionId, { status: status as 'pending' | 'done' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objective', objectiveId] })
    },
    onError: (err) => console.error('Erreur mise a jour action:', err),
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-48" />
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (error || !objective) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <h2 className="text-xl font-bold mb-2">Objectif introuvable</h2>
        <p className="text-muted-foreground mb-4">
          L'objectif demande n'existe pas ou vous n'avez pas les droits d'acces.
        </p>
        <Button variant="outline" onClick={() => navigate('/objectives')}>
          <ChevronLeft className="mr-2 h-4 w-4" />
          Retour a la liste
        </Button>
      </div>
    )
  }

  const isOverdue =
    objective.due_date &&
    new Date(objective.due_date) < new Date() &&
    objective.status !== 'achieved' &&
    objective.status !== 'abandoned'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold">{objective.title}</h1>
            {getTypeBadge(objective.objective_type)}
            {getStatusBadge(objective.status)}
            {isOverdue && <Badge variant="destructive">En retard</Badge>}
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            {objective.beneficiary_name && (
              <Link
                to={`/beneficiaries/${objective.beneficiary_id}`}
                className="flex items-center gap-1 hover:text-foreground"
              >
                <User className="h-4 w-4" />
                {objective.beneficiary_name}
              </Link>
            )}
            {objective.due_date && (
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Echeance: {formatDateFr(objective.due_date)}
              </span>
            )}
            {objective.created_by_name && (
              <span>Cree par {objective.created_by_name}</span>
            )}
          </div>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Progression
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{objective.progress}%</div>
            <Progress value={objective.progress} className="mt-2 h-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Target className="h-4 w-4" />
              Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            {getTypeBadge(objective.objective_type)}
            <p className="text-sm text-muted-foreground mt-1">
              {getTermLabel(objective.term)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Flag className="h-4 w-4" />
              Priorite
            </CardTitle>
          </CardHeader>
          <CardContent>
            {getPriorityBadge(objective.priority)}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Echeance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-sm font-medium ${isOverdue ? 'text-destructive' : ''}`}>
              {objective.due_date ? formatDateFr(objective.due_date) : 'Non definie'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      {objective.description && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm">{objective.description}</p>
          </CardContent>
        </Card>
      )}

      {/* Progress Control */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Progression et statut</CardTitle>
            <div className="flex gap-2">
              {!showProgressForm && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setProgressValue(String(objective.progress))
                    setShowProgressForm(true)
                  }}
                >
                  Mettre a jour la progression
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress update form */}
          {showProgressForm && (
            <div className="rounded-lg border p-4 space-y-3">
              <div className="flex items-center gap-4">
                <div className="space-y-1 flex-1">
                  <Label>Progression (%)</Label>
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    value={progressValue}
                    onChange={(e) => setProgressValue(e.target.value)}
                  />
                </div>
                <div className="space-y-1 flex-[2]">
                  <Label>Note (optionnelle)</Label>
                  <Input
                    value={progressNote}
                    onChange={(e) => setProgressNote(e.target.value)}
                    placeholder="Commentaire sur la progression..."
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={() => progressMutation.mutate()}
                  disabled={
                    progressMutation.isPending ||
                    !progressValue ||
                    Number(progressValue) < 0 ||
                    Number(progressValue) > 100
                  }
                >
                  {progressMutation.isPending && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Enregistrer
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowProgressForm(false)}
                >
                  Annuler
                </Button>
              </div>
            </div>
          )}

          {/* Status buttons */}
          <div>
            <p className="text-sm font-medium mb-2">Changer le statut:</p>
            <div className="flex gap-2 flex-wrap">
              {objective.status !== 'pending' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => statusMutation.mutate('pending')}
                  disabled={statusMutation.isPending}
                >
                  En attente
                </Button>
              )}
              {objective.status !== 'in_progress' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => statusMutation.mutate('in_progress')}
                  disabled={statusMutation.isPending}
                >
                  En cours
                </Button>
              )}
              {objective.status !== 'achieved' && (
                <Button
                  variant="default"
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                  onClick={() => {
                    if (confirm('Marquer cet objectif comme atteint ?')) {
                      statusMutation.mutate('achieved')
                    }
                  }}
                  disabled={statusMutation.isPending}
                >
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Atteint
                </Button>
              )}
              {objective.status !== 'abandoned' && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    if (confirm('Abandonner cet objectif ?')) {
                      statusMutation.mutate('abandoned')
                    }
                  }}
                  disabled={statusMutation.isPending}
                >
                  Abandonner
                </Button>
              )}
              {statusMutation.isPending && (
                <Loader2 className="h-4 w-4 animate-spin" />
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Indicators */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Indicateurs de reussite</CardTitle>
          <CardDescription>
            {objective.indicators?.length
              ? `${objective.indicators.filter((i) => i.is_achieved).length} / ${objective.indicators.length} atteints`
              : 'Aucun indicateur defini'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {objective.indicators && objective.indicators.length > 0 ? (
            <div className="space-y-2">
              {objective.indicators.map((indicator) => (
                <div
                  key={indicator.id}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-accent cursor-pointer"
                  onClick={() => {
                    if (!indicator.is_achieved) {
                      indicatorMutation.mutate(indicator.id)
                    }
                  }}
                >
                  {indicator.is_achieved ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                  ) : (
                    <Circle className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                  )}
                  <span
                    className={`text-sm ${
                      indicator.is_achieved ? 'line-through text-muted-foreground' : ''
                    }`}
                  >
                    {indicator.description}
                  </span>
                  {indicator.achieved_at && (
                    <span className="text-xs text-muted-foreground ml-auto">
                      {formatDateFr(indicator.achieved_at)}
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6">
              <Target className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                Aucun indicateur de reussite defini pour cet objectif.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Actions</CardTitle>
          <CardDescription>
            {objective.actions?.length
              ? `${objective.actions.filter((a) => a.status === 'done').length} / ${objective.actions.length} terminees`
              : 'Aucune action definie'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {objective.actions && objective.actions.length > 0 ? (
            <div className="space-y-2">
              {objective.actions.map((action) => (
                <div
                  key={action.id}
                  className="flex items-center gap-3 p-3 rounded-lg border"
                >
                  <button
                    onClick={() =>
                      actionMutation.mutate({
                        actionId: action.id,
                        status: action.status === 'done' ? 'pending' : 'done',
                      })
                    }
                    disabled={actionMutation.isPending}
                    className="flex-shrink-0"
                  >
                    {action.status === 'done' ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <Circle className="h-5 w-5 text-muted-foreground" />
                    )}
                  </button>
                  <div className="flex-1">
                    <span
                      className={`text-sm ${
                        action.status === 'done' ? 'line-through text-muted-foreground' : ''
                      }`}
                    >
                      {action.description}
                    </span>
                    <div className="flex items-center gap-2 mt-1">
                      {action.responsible_name && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <User className="h-3 w-3" />
                          {action.responsible_name}
                        </span>
                      )}
                      {action.due_date && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDateFr(action.due_date)}
                        </span>
                      )}
                    </div>
                  </div>
                  <Badge variant={action.status === 'done' ? 'success' : 'outline'}>
                    {action.status === 'done' ? 'Termine' : 'En cours'}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6">
              <Circle className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                Aucune action definie pour cet objectif.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
