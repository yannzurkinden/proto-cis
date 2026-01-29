import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  FileBarChart,
  FileText,
  Target,
  CalendarDays,
  Download,
  Loader2,
  User,
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { reportsApi } from '@/api/reports'
import { beneficiariesApi } from '@/api/beneficiaries'
import { adminApi } from '@/api/admin'
import { useAuthStore } from '@/stores/authStore'

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export function ReportsPage() {
  const { user } = useAuthStore()
  const isManagement = user?.role === 'ADMIN' || user?.role === 'RUA' || user?.role === 'RES'

  // Beneficiary summary state
  const [selectedBeneficiary, setSelectedBeneficiary] = useState('')

  // Activity report state
  const [activityDateFrom, setActivityDateFrom] = useState('')
  const [activityDateTo, setActivityDateTo] = useState('')

  // Objectives report state
  const [objStatus, setObjStatus] = useState('')
  const [objType, setObjType] = useState('')
  const [objUnit, setObjUnit] = useState('')

  // Absence stats state
  const [absenceUnit, setAbsenceUnit] = useState('')
  const [absenceDateFrom, setAbsenceDateFrom] = useState('')
  const [absenceDateTo, setAbsenceDateTo] = useState('')

  // Queries
  const { data: beneficiaries } = useQuery({
    queryKey: ['beneficiaries-list-short'],
    queryFn: () => beneficiariesApi.list({ size: 100 }),
  })

  const { data: units } = useQuery({
    queryKey: ['admin-units'],
    queryFn: () => adminApi.listUnits(),
    enabled: isManagement,
  })

  // Mutations for report generation
  const beneficiarySummaryMutation = useMutation({
    mutationFn: () => reportsApi.generateBeneficiarySummary(Number(selectedBeneficiary)),
    onSuccess: (blob) => {
      downloadBlob(blob, 'resume-beneficiaire.pdf')
    },
  })

  const activityReportMutation = useMutation({
    mutationFn: () =>
      reportsApi.generateActivityReport({
        date_from: activityDateFrom,
        date_to: activityDateTo,
      }),
    onSuccess: (blob) => {
      downloadBlob(blob, 'rapport-activite.pdf')
    },
  })

  const objectivesReportMutation = useMutation({
    mutationFn: () =>
      reportsApi.generateObjectivesReport({
        status: objStatus || undefined,
        objective_type: objType || undefined,
        unit_id: objUnit ? Number(objUnit) : undefined,
      }),
    onSuccess: (blob) => {
      downloadBlob(blob, 'bilan-objectifs.xlsx')
    },
  })

  const absenceStatsMutation = useMutation({
    mutationFn: () =>
      reportsApi.generateAbsenceStats({
        unit_id: absenceUnit ? Number(absenceUnit) : undefined,
        date_from: absenceDateFrom,
        date_to: absenceDateTo,
      }),
    onSuccess: (blob) => {
      downloadBlob(blob, 'statistiques-absences.xlsx')
    },
  })

  if (!isManagement) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <FileBarChart className="mb-4 h-16 w-16 text-muted-foreground" />
        <h1 className="text-2xl font-bold">Acces restreint</h1>
        <p className="text-muted-foreground">
          Les rapports sont accessibles uniquement aux responsables.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Rapports</h1>
        <p className="text-muted-foreground">
          Generer et exporter des rapports
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Beneficiary summary */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
                <User className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-base">Resume beneficiaire</CardTitle>
                <CardDescription>
                  Generer un PDF de synthese pour un beneficiaire
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Beneficiaire</Label>
              <Select value={selectedBeneficiary} onValueChange={setSelectedBeneficiary}>
                <SelectTrigger>
                  <SelectValue placeholder="Selectionner un beneficiaire" />
                </SelectTrigger>
                <SelectContent>
                  {beneficiaries?.items.map((b) => (
                    <SelectItem key={b.id} value={String(b.id)}>
                      {b.first_name} {b.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={() => beneficiarySummaryMutation.mutate()}
              disabled={!selectedBeneficiary || beneficiarySummaryMutation.isPending}
              className="w-full"
            >
              {beneficiarySummaryMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Generer PDF
            </Button>
            {beneficiarySummaryMutation.isError && (
              <p className="text-sm text-destructive">Erreur lors de la generation du rapport.</p>
            )}
          </CardContent>
        </Card>

        {/* Activity report */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100">
                <FileText className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <CardTitle className="text-base">Rapport d'activite</CardTitle>
                <CardDescription>
                  Rapport d'activite sur une periode donnee
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Date debut</Label>
                <Input
                  type="date"
                  value={activityDateFrom}
                  onChange={(e) => setActivityDateFrom(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Date fin</Label>
                <Input
                  type="date"
                  value={activityDateTo}
                  onChange={(e) => setActivityDateTo(e.target.value)}
                />
              </div>
            </div>
            <Button
              onClick={() => activityReportMutation.mutate()}
              disabled={!activityDateFrom || !activityDateTo || activityReportMutation.isPending}
              className="w-full"
            >
              {activityReportMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Generer PDF
            </Button>
            {activityReportMutation.isError && (
              <p className="text-sm text-destructive">Erreur lors de la generation du rapport.</p>
            )}
          </CardContent>
        </Card>

        {/* Objectives report */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100">
                <Target className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <CardTitle className="text-base">Bilan objectifs</CardTitle>
                <CardDescription>
                  Export Excel des objectifs avec filtres
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Statut</Label>
              <Select value={objStatus} onValueChange={setObjStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Tous les statuts" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les statuts</SelectItem>
                  <SelectItem value="pending">En attente</SelectItem>
                  <SelectItem value="in_progress">En cours</SelectItem>
                  <SelectItem value="achieved">Atteint</SelectItem>
                  <SelectItem value="abandoned">Abandonne</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <Select value={objType} onValueChange={setObjType}>
                <SelectTrigger>
                  <SelectValue placeholder="Tous les types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les types</SelectItem>
                  <SelectItem value="pai">PAI</SelectItem>
                  <SelectItem value="behavioral">Comportemental</SelectItem>
                  <SelectItem value="operational">Operationnel</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Unite</Label>
              <Select value={objUnit} onValueChange={setObjUnit}>
                <SelectTrigger>
                  <SelectValue placeholder="Toutes les unites" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes les unites</SelectItem>
                  {units?.map((unit) => (
                    <SelectItem key={unit.id} value={String(unit.id)}>
                      {unit.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={() => objectivesReportMutation.mutate()}
              disabled={objectivesReportMutation.isPending}
              className="w-full"
            >
              {objectivesReportMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Export Excel
            </Button>
            {objectivesReportMutation.isError && (
              <p className="text-sm text-destructive">Erreur lors de la generation du rapport.</p>
            )}
          </CardContent>
        </Card>

        {/* Absence statistics */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100">
                <CalendarDays className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <CardTitle className="text-base">Statistiques absences</CardTitle>
                <CardDescription>
                  Export Excel des statistiques d'absences
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Unite</Label>
              <Select value={absenceUnit} onValueChange={setAbsenceUnit}>
                <SelectTrigger>
                  <SelectValue placeholder="Toutes les unites" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes les unites</SelectItem>
                  {units?.map((unit) => (
                    <SelectItem key={unit.id} value={String(unit.id)}>
                      {unit.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Date debut</Label>
                <Input
                  type="date"
                  value={absenceDateFrom}
                  onChange={(e) => setAbsenceDateFrom(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Date fin</Label>
                <Input
                  type="date"
                  value={absenceDateTo}
                  onChange={(e) => setAbsenceDateTo(e.target.value)}
                />
              </div>
            </div>
            <Button
              onClick={() => absenceStatsMutation.mutate()}
              disabled={!absenceDateFrom || !absenceDateTo || absenceStatsMutation.isPending}
              className="w-full"
            >
              {absenceStatsMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Export Excel
            </Button>
            {absenceStatsMutation.isError && (
              <p className="text-sm text-destructive">Erreur lors de la generation du rapport.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
