import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ChevronLeft,
  Loader2,
  Edit,
  Play,
  XCircle,
  Target,
  CheckCircle2,
  Circle,
  AlertTriangle,
  Calendar,
  User,
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { paisApi } from '@/api/pais'
import { beneficiariesApi } from '@/api/beneficiaries'

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
    case 'active':
      return <Badge variant="success">Actif</Badge>
    case 'draft':
      return <Badge variant="outline">Brouillon</Badge>
    case 'closed':
      return <Badge variant="secondary">Cloture</Badge>
    default:
      return <Badge>{status}</Badge>
  }
}

function getObjectiveStatusBadge(status: string) {
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

function getObjectiveTypeLabel(type: string) {
  switch (type) {
    case 'pai':
      return 'PAI'
    case 'behavioral':
      return 'Comportemental'
    case 'operational':
      return 'Operationnel'
    default:
      return type
  }
}

function getObjectiveTypeBadge(type: string) {
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

export function PAIDetailPage() {
  const { beneficiaryId, paiId } = useParams<{ beneficiaryId: string; paiId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const numBeneficiaryId = Number(beneficiaryId)
  const numPaiId = Number(paiId)

  const {
    data: pai,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['pai', numBeneficiaryId, numPaiId],
    queryFn: () => paisApi.get(numBeneficiaryId, numPaiId),
    enabled: !!numBeneficiaryId && !!numPaiId,
  })

  const { data: beneficiary } = useQuery({
    queryKey: ['beneficiary', numBeneficiaryId],
    queryFn: () => beneficiariesApi.get(numBeneficiaryId),
    enabled: !!numBeneficiaryId,
  })

  const activateMutation = useMutation({
    mutationFn: () => paisApi.activate(numBeneficiaryId, numPaiId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pai', numBeneficiaryId, numPaiId] })
      queryClient.invalidateQueries({ queryKey: ['beneficiary', numBeneficiaryId] })
    },
    onError: (err) => console.error('Erreur activation PAI:', err),
  })

  const closeMutation = useMutation({
    mutationFn: () => paisApi.close(numBeneficiaryId, numPaiId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pai', numBeneficiaryId, numPaiId] })
      queryClient.invalidateQueries({ queryKey: ['beneficiary', numBeneficiaryId] })
    },
    onError: (err) => console.error('Erreur cloture PAI:', err),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-3 text-lg">Chargement du PAI...</span>
      </div>
    )
  }

  if (error || !pai) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <h2 className="text-xl font-bold mb-2">PAI introuvable</h2>
        <p className="text-muted-foreground mb-4">
          Le PAI demande n'existe pas ou vous n'avez pas les droits d'acces.
        </p>
        <Button variant="outline" onClick={() => navigate(`/beneficiaries/${numBeneficiaryId}`)}>
          <ChevronLeft className="mr-2 h-4 w-4" />
          Retour au profil
        </Button>
      </div>
    )
  }

  // Group objectives by type
  const objectivesByType: Record<string, typeof pai.objectives> = {}
  for (const obj of pai.objectives || []) {
    const type = obj.objective_type || 'other'
    if (!objectivesByType[type]) objectivesByType[type] = []
    objectivesByType[type].push(obj)
  }

  const typeOrder = ['pai', 'behavioral', 'operational']
  const sortedTypes = Object.keys(objectivesByType).sort(
    (a, b) => typeOrder.indexOf(a) - typeOrder.indexOf(b)
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate(`/beneficiaries/${numBeneficiaryId}`)}
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold">Plan d'Accompagnement Individualise</h1>
            {getStatusBadge(pai.status)}
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            {beneficiary && (
              <Link
                to={`/beneficiaries/${numBeneficiaryId}`}
                className="flex items-center gap-1 hover:text-foreground"
              >
                <User className="h-4 w-4" />
                {beneficiary.first_name} {beneficiary.last_name}
              </Link>
            )}
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              Du {formatDateFr(pai.valid_from)}
              {pai.valid_to ? ` au ${formatDateFr(pai.valid_to)}` : ''}
            </span>
            {pai.created_by_name && (
              <span>Cree par {pai.created_by_name}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {pai.status === 'draft' && (
            <Button
              onClick={() => {
                if (confirm('Activer ce PAI ?')) activateMutation.mutate()
              }}
              disabled={activateMutation.isPending}
            >
              {activateMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Activer
            </Button>
          )}
          {pai.status === 'active' && (
            <Button
              variant="secondary"
              onClick={() => {
                if (confirm('Cloturer ce PAI ?')) closeMutation.mutate()
              }}
              disabled={closeMutation.isPending}
            >
              {closeMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <XCircle className="mr-2 h-4 w-4" />
              )}
              Cloturer
            </Button>
          )}
          {pai.status !== 'closed' && (
            <Button variant="outline" asChild>
              <Link to={`/beneficiaries/${numBeneficiaryId}/pais/${numPaiId}/edit`}>
                <Edit className="mr-2 h-4 w-4" />
                Modifier
              </Link>
            </Button>
          )}
        </div>
      </div>

      {/* Bilan initial */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-green-700">Points forts</CardTitle>
            <CardDescription>Forces et ressources du beneficiaire</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm">
              {pai.strengths || 'Non renseigne'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-orange-700">Difficultes</CardTitle>
            <CardDescription>Points a travailler</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm">
              {pai.difficulties || 'Non renseigne'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-blue-700">Souhaits</CardTitle>
            <CardDescription>Aspirations du beneficiaire</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm">
              {pai.beneficiary_wishes || 'Non renseigne'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Objectives grouped by type */}
      {sortedTypes.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <Target className="h-10 w-10 text-muted-foreground mb-2" />
            <p className="text-muted-foreground">Aucun objectif defini dans ce PAI</p>
          </CardContent>
        </Card>
      ) : (
        sortedTypes.map((type) => (
          <div key={type} className="space-y-3">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              {getObjectiveTypeBadge(type)}
              <span>Objectifs {getObjectiveTypeLabel(type).toLowerCase()}</span>
              <span className="text-sm font-normal text-muted-foreground">
                ({objectivesByType[type].length})
              </span>
            </h2>

            {objectivesByType[type].map((obj) => (
              <Card key={obj.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <Link
                      to={`/objectives/${obj.id}`}
                      className="font-medium hover:text-primary hover:underline"
                    >
                      {obj.title}
                    </Link>
                    <div className="flex items-center gap-2">
                      {getObjectiveStatusBadge(obj.status)}
                      {obj.due_date && (
                        <span className="text-sm text-muted-foreground">
                          Echeance: {formatDateFr(obj.due_date)}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Progress */}
                  <div className="flex items-center gap-3 mb-3">
                    <Progress value={obj.progress} className="flex-1 h-2" />
                    <span className="text-sm font-medium w-12 text-right">{obj.progress}%</span>
                  </div>

                  {/* Indicators */}
                  {'indicators' in obj && Array.isArray((obj as unknown as { indicators: { id: number; description: string; is_achieved: boolean }[] }).indicators) && (
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-muted-foreground uppercase">Indicateurs</p>
                      {((obj as unknown as { indicators: { id: number; description: string; is_achieved: boolean }[] }).indicators).map(
                        (ind: { id: number; description: string; is_achieved: boolean }) => (
                          <div key={ind.id} className="flex items-center gap-2 text-sm">
                            {ind.is_achieved ? (
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                            ) : (
                              <Circle className="h-4 w-4 text-muted-foreground" />
                            )}
                            <span className={ind.is_achieved ? 'line-through text-muted-foreground' : ''}>
                              {ind.description}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  )}

                  {/* Actions */}
                  {'actions' in obj && Array.isArray((obj as unknown as { actions: { id: number; description: string; status: string; responsible_name?: string | null }[] }).actions) && (
                    <div className="mt-3 space-y-1">
                      <p className="text-xs font-medium text-muted-foreground uppercase">Actions</p>
                      {((obj as unknown as { actions: { id: number; description: string; status: string; responsible_name?: string | null }[] }).actions).map(
                        (action: { id: number; description: string; status: string; responsible_name?: string | null }) => (
                          <div key={action.id} className="flex items-center gap-2 text-sm">
                            {action.status === 'done' ? (
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                            ) : (
                              <Circle className="h-4 w-4 text-muted-foreground" />
                            )}
                            <span>{action.description}</span>
                            {action.responsible_name && (
                              <span className="text-muted-foreground">({action.responsible_name})</span>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        ))
      )}
    </div>
  )
}
