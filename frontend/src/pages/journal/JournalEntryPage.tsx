import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ChevronLeft,
  Loader2,
  AlertTriangle,
  Edit,
  Trash2,
  Calendar,
  User,
  Eye,
  Tag,
  Paperclip,
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { journalApi } from '@/api/journal'

// ---- Helpers ----

function formatDateFr(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  try {
    return format(parseISO(dateStr), 'dd MMMM yyyy', { locale: fr })
  } catch {
    return dateStr
  }
}

function formatDateTimeFr(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  try {
    return format(parseISO(dateStr), "dd MMMM yyyy 'a' HH:mm", { locale: fr })
  } catch {
    return dateStr
  }
}

function getVisibilityLabel(visibility: string) {
  switch (visibility) {
    case 'team':
      return 'Equipe'
    case 'unit':
      return 'Unite'
    case 'inter_unit':
      return 'Inter-unites'
    default:
      return visibility
  }
}

function getVisibilityVariant(visibility: string) {
  switch (visibility) {
    case 'team':
      return 'outline' as const
    case 'unit':
      return 'secondary' as const
    case 'inter_unit':
      return 'default' as const
    default:
      return 'outline' as const
  }
}

// ---- Component ----

export function JournalEntryPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const entryId = Number(id)

  const {
    data: entry,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['journal-entry', entryId],
    queryFn: () => journalApi.get(entryId),
    enabled: !!entryId && !isNaN(entryId),
  })

  const deleteMutation = useMutation({
    mutationFn: () => journalApi.delete(entryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal'] })
      navigate('/journal')
    },
    onError: (err) => console.error('Erreur suppression:', err),
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
        <Skeleton className="h-[300px] w-full" />
      </div>
    )
  }

  if (error || !entry) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <h2 className="text-xl font-bold mb-2">Entree introuvable</h2>
        <p className="text-muted-foreground mb-4">
          L'entree de journal demandee n'existe pas ou vous n'avez pas les droits d'acces.
        </p>
        <Button variant="outline" onClick={() => navigate('/journal')}>
          <ChevronLeft className="mr-2 h-4 w-4" />
          Retour au journal
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{entry.title}</h1>
          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
            {entry.beneficiary_name && (
              <Link
                to={`/beneficiaries/${entry.beneficiary_id}`}
                className="flex items-center gap-1 hover:text-foreground"
              >
                <User className="h-4 w-4" />
                {entry.beneficiary_name}
              </Link>
            )}
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {formatDateFr(entry.entry_date)}
            </span>
            {entry.author_name && (
              <span className="flex items-center gap-1">
                <User className="h-4 w-4" />
                Redige par {entry.author_name}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Eye className="h-4 w-4" />
              <Badge variant={getVisibilityVariant(entry.visibility)}>
                {getVisibilityLabel(entry.visibility)}
              </Badge>
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to={`/journal/${entryId}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Modifier
            </Link>
          </Button>
          <Button
            variant="destructive"
            size="icon"
            onClick={() => {
              if (confirm('Supprimer cette entree de journal ?')) {
                deleteMutation.mutate()
              }
            }}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Content */}
      <Card>
        <CardContent className="p-6">
          <div
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: entry.content }}
          />
        </CardContent>
      </Card>

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Categories */}
          {entry.categories.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2 flex items-center gap-2">
                <Tag className="h-4 w-4" />
                Categories
              </p>
              <div className="flex items-center gap-2 flex-wrap">
                {entry.categories.map((cat) => (
                  <Badge
                    key={cat.id}
                    variant="outline"
                    style={cat.color ? { borderColor: cat.color, color: cat.color } : undefined}
                  >
                    {cat.label}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          {entry.tags.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">Tags</p>
              <div className="flex items-center gap-2 flex-wrap">
                {entry.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <Separator />

          {/* Timestamps */}
          <div className="grid gap-4 md:grid-cols-2 text-sm">
            <div>
              <p className="text-muted-foreground">Date de l'entree</p>
              <p className="font-medium">{formatDateFr(entry.entry_date)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Creee le</p>
              <p className="font-medium">{formatDateTimeFr(entry.created_at)}</p>
            </div>
            {entry.updated_at !== entry.created_at && (
              <div>
                <p className="text-muted-foreground">Derniere modification</p>
                <p className="font-medium">{formatDateTimeFr(entry.updated_at)}</p>
              </div>
            )}
            {entry.attachments_count > 0 && (
              <div>
                <p className="text-muted-foreground flex items-center gap-1">
                  <Paperclip className="h-4 w-4" />
                  Pieces jointes
                </p>
                <p className="font-medium">{entry.attachments_count} fichier(s)</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
