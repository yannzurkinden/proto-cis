import { useState } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  BookOpen,
  Search,
  Filter,
  Plus,
  Calendar,
  User,
  ChevronLeft,
  ChevronRight,
  Eye,
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
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

// ---- Component ----

export function JournalListPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const initialBeneficiaryId = searchParams.get('beneficiary_id') || ''

  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [beneficiaryId] = useState(initialBeneficiaryId)
  const [showFilters, setShowFilters] = useState(false)

  const { data: categories } = useQuery({
    queryKey: ['journal-categories'],
    queryFn: () => journalApi.getCategories(),
  })

  const { data, isLoading } = useQuery({
    queryKey: ['journal', { page, search, category: categoryFilter, dateFrom, dateTo, beneficiaryId }],
    queryFn: () =>
      journalApi.list({
        page,
        size: 10,
        search: search || undefined,
        category: categoryFilter || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        beneficiary_id: beneficiaryId ? Number(beneficiaryId) : undefined,
      }),
  })

  const stripHtml = (html: string) => {
    return html.replace(/<[^>]*>/g, '')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Journal</h1>
          <p className="text-muted-foreground">
            Notes et observations de suivi des beneficiaires
          </p>
        </div>
        <Button asChild>
          <Link to="/journal/new">
            <Plus className="mr-2 h-4 w-4" />
            Nouvelle entree
          </Link>
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Rechercher dans le journal..."
                className="pl-9"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="mr-2 h-4 w-4" />
              Filtres
            </Button>
          </div>
        </CardHeader>
        {showFilters && (
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label>Categorie</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={categoryFilter}
                  onChange={(e) => {
                    setCategoryFilter(e.target.value)
                    setPage(1)
                  }}
                >
                  <option value="">Toutes</option>
                  {categories?.map((cat) => (
                    <option key={cat.id} value={cat.name}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Date du</Label>
                <Input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => {
                    setDateFrom(e.target.value)
                    setPage(1)
                  }}
                />
              </div>
              <div className="space-y-2">
                <Label>Date au</Label>
                <Input
                  type="date"
                  value={dateTo}
                  onChange={(e) => {
                    setDateTo(e.target.value)
                    setPage(1)
                  }}
                />
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Results */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-6 w-48 mb-2" />
                <Skeleton className="h-4 w-full mb-1" />
                <Skeleton className="h-4 w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : !data?.items.length ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">Aucune entree de journal</p>
            <p className="text-muted-foreground">
              {search || categoryFilter || dateFrom || dateTo
                ? 'Modifiez les filtres pour voir plus de resultats.'
                : 'Commencez par creer une nouvelle entree.'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Timeline cards */}
          {data.items.map((entry) => (
            <Card
              key={entry.id}
              className="transition-colors hover:bg-accent/50 cursor-pointer"
              onClick={() => navigate(`/journal/${entry.id}`)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-semibold text-base">{entry.title}</h3>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground mt-1">
                      {entry.beneficiary_name && (
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          {entry.beneficiary_name}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDateFr(entry.entry_date)}
                      </span>
                      {entry.author_name && (
                        <span>par {entry.author_name}</span>
                      )}
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {getVisibilityLabel(entry.visibility)}
                      </span>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                  {stripHtml(entry.content).substring(0, 200)}
                  {stripHtml(entry.content).length > 200 ? '...' : ''}
                </p>

                <div className="flex items-center gap-2 flex-wrap">
                  {entry.categories.map((cat) => (
                    <Badge
                      key={cat.id}
                      variant="outline"
                      className="text-xs"
                      style={cat.color ? { borderColor: cat.color, color: cat.color } : undefined}
                    >
                      {cat.label}
                    </Badge>
                  ))}
                  {entry.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {entry.attachments_count > 0 && (
                    <Badge variant="outline" className="text-xs">
                      {entry.attachments_count} piece(s) jointe(s)
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Pagination */}
          {data.pages > 1 && (
            <div className="flex items-center justify-between pt-2">
              <p className="text-sm text-muted-foreground">
                Page {page} sur {data.pages} ({data.total} resultats)
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  <ChevronLeft className="mr-1 h-4 w-4" />
                  Precedent
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= data.pages}
                  onClick={() => setPage(page + 1)}
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
