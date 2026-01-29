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

  const { data, isLoading } = useQuery({
    queryKey: ['beneficiaries', { page, search }],
    queryFn: () => beneficiariesApi.list({ page, size: 20, search: search || undefined }),
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
          <h1 className="text-3xl font-bold">Beneficiaires</h1>
          <p className="text-muted-foreground">
            Gestion des beneficiaires et de leur accompagnement
          </p>
        </div>
        <Button asChild>
          <Link to="/beneficiaries/new">
            <Plus className="mr-2 h-4 w-4" />
            Nouveau beneficiaire
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
            <Button variant="outline" size="icon">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center p-8">Chargement...</div>
          ) : !data?.items.length ? (
            <div className="flex flex-col items-center justify-center p-8 text-center">
              <p className="text-muted-foreground">Aucun beneficiaire trouve</p>
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
                      <span>Ne le {formatDate(beneficiary.date_of_birth)}</span>
                      {beneficiary.unit_name && <span>Unite: {beneficiary.unit_name}</span>}
                      {beneficiary.referent_name && <span>Ref: {beneficiary.referent_name}</span>}
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
                    Page {page} sur {data.pages} ({data.total} resultats)
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page === 1}
                      onClick={() => setPage(page - 1)}
                    >
                      Precedent
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
