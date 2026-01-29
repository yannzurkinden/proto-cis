import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Clock,
  Plus,
  CalendarDays,
  TrendingDown,
  Timer,
  AlertCircle,
  ArrowLeft,
  CheckCircle,
  Palmtree,
} from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { useAuthStore } from '@/stores/authStore'
import { timeTrackingApi } from '@/api/timeTracking'
import { beneficiariesApi } from '@/api/beneficiaries'

// Schemas
const timeEntrySchema = z.object({
  date: z.string().min(1, 'Date requise'),
  time_in: z.string().min(1, "Heure d'arrivée requise"),
  time_out: z.string().optional(),
  entry_type: z.string().min(1, 'Type requis'),
  notes: z.string().optional(),
})

type TimeEntryForm = z.infer<typeof timeEntrySchema>

const absenceSchema = z.object({
  start_date: z.string().min(1, 'Date de début requise'),
  end_date: z.string().min(1, 'Date de fin requise'),
  absence_type: z.string().min(1, 'Type requis'),
  reason: z.string().optional(),
  justified: z.boolean().optional(),
})

type AbsenceForm = z.infer<typeof absenceSchema>

const entryTypeLabels: Record<string, string> = {
  present: 'Présent',
  half_day: 'Demi-journée',
  training: 'Formation',
  external: 'Externe',
}

const absenceTypeLabels: Record<string, string> = {
  sick: 'Maladie',
  vacation: 'Vacances',
  personal: 'Personnel',
  accident: 'Accident',
  unjustified: 'Injustifiée',
  other: 'Autre',
}

export function TimeTrackingPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const beneficiaryId = Number(id)

  const [activeTab, setActiveTab] = useState('pointages')
  const [entryDialogOpen, setEntryDialogOpen] = useState(false)
  const [absenceDialogOpen, setAbsenceDialogOpen] = useState(false)

  const isManagement = user?.role === 'ADMIN' || user?.role === 'RUA' || user?.role === 'RES'

  // Queries
  const { data: beneficiary } = useQuery({
    queryKey: ['beneficiary', beneficiaryId],
    queryFn: () => beneficiariesApi.get(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  const { data: entries, isLoading: entriesLoading } = useQuery({
    queryKey: ['time-entries', beneficiaryId],
    queryFn: () => timeTrackingApi.getEntries(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  const { data: absences, isLoading: absencesLoading } = useQuery({
    queryKey: ['absences', beneficiaryId],
    queryFn: () => timeTrackingApi.getAbsences(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  const { data: vacationBalance, isLoading: vacationLoading } = useQuery({
    queryKey: ['vacation-balance', beneficiaryId],
    queryFn: () => timeTrackingApi.getVacationBalance(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['time-stats', beneficiaryId],
    queryFn: () => timeTrackingApi.getStats(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  // Mutations
  const createEntryMutation = useMutation({
    mutationFn: (data: TimeEntryForm) =>
      timeTrackingApi.createEntry(beneficiaryId, {
        date: data.date,
        time_in: data.time_in,
        time_out: data.time_out || undefined,
        entry_type: data.entry_type as 'present' | 'half_day' | 'training' | 'external',
        notes: data.notes || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-entries', beneficiaryId] })
      queryClient.invalidateQueries({ queryKey: ['time-stats', beneficiaryId] })
      setEntryDialogOpen(false)
      entryForm.reset()
    },
  })

  const createAbsenceMutation = useMutation({
    mutationFn: (data: AbsenceForm) =>
      timeTrackingApi.createAbsence(beneficiaryId, {
        start_date: data.start_date,
        end_date: data.end_date,
        absence_type: data.absence_type as 'sick' | 'vacation' | 'personal' | 'accident' | 'unjustified' | 'other',
        reason: data.reason || undefined,
        justified: data.justified ?? false,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['absences', beneficiaryId] })
      queryClient.invalidateQueries({ queryKey: ['time-stats', beneficiaryId] })
      setAbsenceDialogOpen(false)
      absenceForm.reset()
    },
  })

  const validateAbsenceMutation = useMutation({
    mutationFn: (absenceId: number) =>
      timeTrackingApi.validateAbsence(beneficiaryId, absenceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['absences', beneficiaryId] })
    },
  })

  // Forms
  const entryForm = useForm<TimeEntryForm>({
    resolver: zodResolver(timeEntrySchema),
    defaultValues: {
      date: format(new Date(), 'yyyy-MM-dd'),
      time_in: '08:00',
      time_out: '',
      entry_type: 'present',
      notes: '',
    },
  })

  const absenceForm = useForm<AbsenceForm>({
    resolver: zodResolver(absenceSchema),
    defaultValues: {
      start_date: format(new Date(), 'yyyy-MM-dd'),
      end_date: format(new Date(), 'yyyy-MM-dd'),
      absence_type: 'sick',
      reason: '',
      justified: false,
    },
  })

  const formatTime = (time: string | null) => {
    if (!time) return '-'
    return time.substring(0, 5)
  }

  const formatDateDisplay = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'dd MMM yyyy', { locale: fr })
    } catch {
      return dateStr
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/beneficiaries/' + id)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Suivi du temps</h1>
          <p className="text-muted-foreground">
            {beneficiary
              ? beneficiary.first_name + ' ' + beneficiary.last_name
              : 'Chargement...'}
          </p>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Taux d'absence</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {stats?.absence_rate != null ? stats.absence_rate.toFixed(1) : '0'}%
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Heures ce mois</CardTitle>
            <Timer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {stats?.hours_this_month != null ? stats.hours_this_month.toFixed(1) : '0'}h
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Absences ce mois</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {stats?.absences_this_month ?? 0}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="pointages">
            <Clock className="mr-2 h-4 w-4" />
            Pointages
          </TabsTrigger>
          <TabsTrigger value="absences">
            <CalendarDays className="mr-2 h-4 w-4" />
            Absences
          </TabsTrigger>
          <TabsTrigger value="vacances">
            <Palmtree className="mr-2 h-4 w-4" />
            Solde vacances
          </TabsTrigger>
        </TabsList>

        {/* Pointages tab */}
        <TabsContent value="pointages" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Pointages</h2>
            <Dialog open={entryDialogOpen} onOpenChange={setEntryDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Ajouter un pointage
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Nouveau pointage</DialogTitle>
                  <DialogDescription>
                    Ajouter une entrée de pointage pour ce bénéficiaire.
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={entryForm.handleSubmit((data) => createEntryMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="space-y-2">
                    <Label htmlFor="entry-date">Date</Label>
                    <Input id="entry-date" type="date" {...entryForm.register('date')} />
                    {entryForm.formState.errors.date && (
                      <p className="text-sm text-destructive">
                        {entryForm.formState.errors.date.message}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="time-in">Heure d'arrivée</Label>
                      <Input id="time-in" type="time" {...entryForm.register('time_in')} />
                      {entryForm.formState.errors.time_in && (
                        <p className="text-sm text-destructive">
                          {entryForm.formState.errors.time_in.message}
                        </p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="time-out">Heure de départ</Label>
                      <Input id="time-out" type="time" {...entryForm.register('time_out')} />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="entry-type">Type</Label>
                    <Select
                      value={entryForm.watch('entry_type')}
                      onValueChange={(value) => entryForm.setValue('entry_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner un type" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(entryTypeLabels).map(([value, label]) => (
                          <SelectItem key={value} value={value}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="entry-notes">Notes</Label>
                    <Textarea
                      id="entry-notes"
                      placeholder="Notes optionnelles..."
                      {...entryForm.register('notes')}
                    />
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setEntryDialogOpen(false)}>
                      Annuler
                    </Button>
                    <Button type="submit" disabled={createEntryMutation.isPending}>
                      {createEntryMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              {entriesLoading ? (
                <div className="space-y-4 p-6">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !entries?.length ? (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <Clock className="mb-4 h-12 w-12 text-muted-foreground" />
                  <p className="text-muted-foreground">Aucun pointage enregistré</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Arrivée</TableHead>
                      <TableHead>Départ</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Heures</TableHead>
                      <TableHead>Notes</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {entries.map((entry) => (
                      <TableRow key={entry.id}>
                        <TableCell className="font-medium">
                          {formatDateDisplay(entry.date)}
                        </TableCell>
                        <TableCell>{formatTime(entry.time_in)}</TableCell>
                        <TableCell>{formatTime(entry.time_out)}</TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {entryTypeLabels[entry.entry_type] || entry.entry_type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {entry.hours != null ? String(entry.hours.toFixed(1)) + 'h' : '-'}
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate text-muted-foreground">
                          {entry.notes || '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Absences tab */}
        <TabsContent value="absences" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Absences</h2>
            <Dialog open={absenceDialogOpen} onOpenChange={setAbsenceDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Ajouter une absence
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Nouvelle absence</DialogTitle>
                  <DialogDescription>
                    Enregistrer une absence pour ce bénéficiaire.
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={absenceForm.handleSubmit((data) => createAbsenceMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="absence-start">Date de début</Label>
                      <Input id="absence-start" type="date" {...absenceForm.register('start_date')} />
                      {absenceForm.formState.errors.start_date && (
                        <p className="text-sm text-destructive">
                          {absenceForm.formState.errors.start_date.message}
                        </p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="absence-end">Date de fin</Label>
                      <Input id="absence-end" type="date" {...absenceForm.register('end_date')} />
                      {absenceForm.formState.errors.end_date && (
                        <p className="text-sm text-destructive">
                          {absenceForm.formState.errors.end_date.message}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="absence-type">Type d'absence</Label>
                    <Select
                      value={absenceForm.watch('absence_type')}
                      onValueChange={(value) => absenceForm.setValue('absence_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner un type" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(absenceTypeLabels).map(([value, label]) => (
                          <SelectItem key={value} value={value}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="absence-reason">Motif</Label>
                    <Textarea
                      id="absence-reason"
                      placeholder="Motif de l'absence..."
                      {...absenceForm.register('reason')}
                    />
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setAbsenceDialogOpen(false)}>
                      Annuler
                    </Button>
                    <Button type="submit" disabled={createAbsenceMutation.isPending}>
                      {createAbsenceMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              {absencesLoading ? (
                <div className="space-y-4 p-6">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !absences?.length ? (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <CalendarDays className="mb-4 h-12 w-12 text-muted-foreground" />
                  <p className="text-muted-foreground">Aucune absence enregistrée</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date début</TableHead>
                      <TableHead>Date fin</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Durée (jours)</TableHead>
                      <TableHead>Statut</TableHead>
                      {isManagement && <TableHead>Actions</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {absences.map((absence) => (
                      <TableRow key={absence.id}>
                        <TableCell className="font-medium">
                          {formatDateDisplay(absence.start_date)}
                        </TableCell>
                        <TableCell>{formatDateDisplay(absence.end_date)}</TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {absenceTypeLabels[absence.absence_type] || absence.absence_type}
                          </Badge>
                        </TableCell>
                        <TableCell>{absence.duration_days}</TableCell>
                        <TableCell>
                          {absence.validated ? (
                            <Badge variant="default" className="bg-green-600">
                              <CheckCircle className="mr-1 h-3 w-3" />
                              Validée
                            </Badge>
                          ) : (
                            <Badge variant="secondary">En attente</Badge>
                          )}
                        </TableCell>
                        {isManagement && (
                          <TableCell>
                            {!absence.validated && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => validateAbsenceMutation.mutate(absence.id)}
                                disabled={validateAbsenceMutation.isPending}
                              >
                                <CheckCircle className="mr-1 h-3 w-3" />
                                Valider
                              </Button>
                            )}
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Vacation balance tab */}
        <TabsContent value="vacances" className="space-y-4">
          <h2 className="text-lg font-semibold">Solde de vacances</h2>

          {vacationLoading ? (
            <div className="grid gap-4 md:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))}
            </div>
          ) : vacationBalance ? (
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Jours acquis ({vacationBalance.year})</CardDescription>
                  <CardTitle className="text-3xl">{vacationBalance.entitled_days}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Jours de vacances annuels</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Jours pris</CardDescription>
                  <CardTitle className="text-3xl">{vacationBalance.taken_days}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {vacationBalance.planned_days > 0
                      ? String(vacationBalance.planned_days) + ' jours planifiés'
                      : 'Aucun jour planifié'}
                  </p>
                </CardContent>
              </Card>

              <Card className="border-primary">
                <CardHeader className="pb-2">
                  <CardDescription>Jours restants</CardDescription>
                  <CardTitle className="text-3xl text-primary">
                    {vacationBalance.remaining_days}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Solde disponible</p>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                <Palmtree className="mb-4 h-12 w-12 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Aucune donnée de solde vacances disponible
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
