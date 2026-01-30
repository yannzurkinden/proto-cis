import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { beneficiariesApi } from '@/api/beneficiaries'
import { formatDate } from '@/lib/utils'

export function BeneficiaryListPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['beneficiaries', { page, search, status: statusFilter }],
    queryFn: () => beneficiariesApi.list({
      page,
      size: 20,
      search: search || undefined,
      status: statusFilter || undefined,
    }),
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="success">Actif</Badge>
      case 'paused':
        return <Badge variant="warning">En pause</Badge>
      case 'exited':
        return <Badge variant="secondary">Sorti</Badge>
      default:
        return <Badge>{status}</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bénéficiaires</h1>
          <p className="text-muted-foreground">
            Gestion des bénéficiaires et de leur accompagnement
          </p>
        </div>
        <Button asChild>
          <Link to="/beneficiaries/new">
            <Plus className="mr-2 h-4 w-4" />
            Nouveau bénéficiaire
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Rechercher par nom..."
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Button
              variant={showFilters ? "default" : "outline"}
              size="icon"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="h-4 w-4" />
            </Button>
          </div>
          {showFilters && (
            <div className="flex items-center gap-4 pt-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Statut:</span>
                <select
                  className="h-9 rounded-md border border-input bg-background px-3 text-sm"
                  value={statusFilter}
                  onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
                >
                  <option value="">Tous</option>
                  <option value="active">Actif</option>
                  <option value="paused">En pause</option>
                  <option value="exited">Sorti</option>
                </select>
              </div>
              {statusFilter && (
                <Button variant="ghost" size="sm" onClick={() => { setStatusFilter(''); setPage(1) }}>
                  Réinitialiser
                </Button>
              )}
            </div>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center p-8">Chargement...</div>
          ) : !data?.items.length ? (
            <div className="flex flex-col items-center justify-center p-8 text-center">
              <p className="text-muted-foreground">Aucun bénéficiaire trouvé</p>
            </div>
          ) : (
            <div className="space-y-4">
              {data.items.map((beneficiary) => (
                <Link
                  key={beneficiary.id}
                  to={`/beneficiaries/${beneficiary.id}`}
                  className="flex items-center gap-4 rounded-lg border p-4 transition-colors hover:bg-accent"
                >
                  <Avatar className="h-12 w-12">
                    <AvatarFallback>
                      {beneficiary.first_name[0]}{beneficiary.last_name[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">
                        {beneficiary.first_name} {beneficiary.last_name}
                      </span>
                      {getStatusBadge(beneficiary.status)}
                    </div>
                    <div className="mt-1 flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Né le {formatDate(beneficiary.date_of_birth)}</span>
                      {beneficiary.unit_name && <span>Unité: {beneficiary.unit_name}</span>}
                      {beneficiary.referent_name && <span>Réf: {beneficiary.referent_name}</span>}
                    </div>
                  </div>
                  <div className="text-right">
                    {beneficiary.objectives_overdue > 0 ? (
                      <Badge variant="destructive">
                        {beneficiary.objectives_overdue} en retard
                      </Badge>
                    ) : beneficiary.objectives_in_progress > 0 ? (
                      <Badge variant="outline">
                        {beneficiary.objectives_in_progress} en cours
                      </Badge>
                    ) : null}
                  </div>
                </Link>
              ))}

              {data.pages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <p className="text-sm text-muted-foreground">
                    Page {page} sur {data.pages} ({data.total} résultats)
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page === 1}
                      onClick={() => setPage(page - 1)}
                    >
                      Précédent
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page === data.pages}
                      onClick={() => setPage(page + 1)}
                    >
                      Suivant
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
