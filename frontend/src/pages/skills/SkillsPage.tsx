import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Award,
  Plus,
  GraduationCap,
  ArrowLeft,
  Edit,
  Trash2,
  Star,
} from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

import { Card, CardContent } from '@/components/ui/card'
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
import { skillsApi, type SkillEvaluation } from '@/api/skills'
import { beneficiariesApi } from '@/api/beneficiaries'

// Schemas
const evaluationSchema = z.object({
  skill_id: z.string().min(1, 'Compétence requise'),
  level: z.string().min(1, 'Niveau requis'),
  notes: z.string().optional(),
})

type EvaluationForm = z.infer<typeof evaluationSchema>

const trainingSchema = z.object({
  title: z.string().min(1, 'Titre requis'),
  start_date: z.string().min(1, 'Date requise'),
  end_date: z.string().optional(),
  duration_hours: z.string().optional(),
  trainer: z.string().optional(),
  location: z.string().optional(),
  certificate: z.boolean().optional(),
  notes: z.string().optional(),
})

type TrainingForm = z.infer<typeof trainingSchema>

const levelLabels: Record<string, string> = {
  not_acquired: 'Non acquis',
  in_progress: 'En cours',
  acquired: 'Acquis',
  mastered: 'Maîtrisé',
}

const levelColors: Record<string, string> = {
  not_acquired: 'bg-gray-200 text-gray-800',
  in_progress: 'bg-yellow-200 text-yellow-800',
  acquired: 'bg-green-200 text-green-800',
  mastered: 'bg-blue-200 text-blue-800',
}

export function SkillsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const beneficiaryId = Number(id)

  const [activeTab, setActiveTab] = useState('competences')
  const [evalDialogOpen, setEvalDialogOpen] = useState(false)
  const [trainingDialogOpen, setTrainingDialogOpen] = useState(false)
  const [editingTraining, setEditingTraining] = useState<number | null>(null)

  // Queries
  const { data: beneficiary } = useQuery({
    queryKey: ['beneficiary', beneficiaryId],
    queryFn: () => beneficiariesApi.get(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  const { data: skills, isLoading: skillsLoading } = useQuery({
    queryKey: ['skills-reference'],
    queryFn: () => skillsApi.listSkills(),
  })

  const { data: evaluations, isLoading: evaluationsLoading } = useQuery({
    queryKey: ['skill-evaluations', beneficiaryId],
    queryFn: () => skillsApi.getEvaluations(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  const { data: trainings, isLoading: trainingsLoading } = useQuery({
    queryKey: ['trainings', beneficiaryId],
    queryFn: () => skillsApi.getTrainings(beneficiaryId),
    enabled: !!beneficiaryId,
  })

  // Mutations
  const createEvaluationMutation = useMutation({
    mutationFn: (data: EvaluationForm) =>
      skillsApi.createEvaluation(beneficiaryId, {
        skill_id: Number(data.skill_id),
        level: data.level,
        notes: data.notes || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['skill-evaluations', beneficiaryId] })
      setEvalDialogOpen(false)
      evalForm.reset()
    },
  })

  const createTrainingMutation = useMutation({
    mutationFn: (data: TrainingForm) =>
      skillsApi.createTraining(beneficiaryId, {
        title: data.title,
        start_date: data.start_date,
        end_date: data.end_date || undefined,
        duration_hours: data.duration_hours ? Number(data.duration_hours) : undefined,
        trainer: data.trainer || undefined,
        location: data.location || undefined,
        certificate: data.certificate ?? false,
        notes: data.notes || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trainings', beneficiaryId] })
      setTrainingDialogOpen(false)
      trainingForm.reset()
    },
  })

  const deleteTrainingMutation = useMutation({
    mutationFn: (trainingId: number) =>
      skillsApi.deleteTraining(beneficiaryId, trainingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trainings', beneficiaryId] })
    },
  })

  // Forms
  const evalForm = useForm<EvaluationForm>({
    resolver: zodResolver(evaluationSchema),
    defaultValues: {
      skill_id: '',
      level: '',
      notes: '',
    },
  })

  const trainingForm = useForm<TrainingForm>({
    resolver: zodResolver(trainingSchema),
    defaultValues: {
      title: '',
      start_date: format(new Date(), 'yyyy-MM-dd'),
      end_date: '',
      duration_hours: '',
      trainer: '',
      location: '',
      certificate: false,
      notes: '',
    },
  })

  const formatDateDisplay = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'dd MMM yyyy', { locale: fr })
    } catch {
      return dateStr
    }
  }

  // Build evaluation map: skill_id -> latest evaluation
  const evaluationMap = new Map<number, SkillEvaluation>()
  if (evaluations) {
    for (const ev of evaluations) {
      const existing = evaluationMap.get(ev.skill_id)
      if (!existing || new Date(ev.evaluated_at) > new Date(existing.evaluated_at)) {
        evaluationMap.set(ev.skill_id, ev)
      }
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
          <h1 className="text-3xl font-bold">Compétences et formations</h1>
          <p className="text-muted-foreground">
            {beneficiary
              ? beneficiary.first_name + ' ' + beneficiary.last_name
              : 'Chargement...'}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="competences">
            <Star className="mr-2 h-4 w-4" />
            Matrice de compétences
          </TabsTrigger>
          <TabsTrigger value="formations">
            <GraduationCap className="mr-2 h-4 w-4" />
            Formations
          </TabsTrigger>
        </TabsList>

        {/* Skills matrix tab */}
        <TabsContent value="competences" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Matrice de compétences</h2>
            <Dialog open={evalDialogOpen} onOpenChange={setEvalDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Évaluer
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Évaluer une competence</DialogTitle>
                  <DialogDescription>
                    Sélectionner une compétence et attribuer un niveau.
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={evalForm.handleSubmit((data) => createEvaluationMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="space-y-2">
                    <Label htmlFor="eval-skill">Compétence</Label>
                    <Select
                      value={evalForm.watch('skill_id')}
                      onValueChange={(value) => evalForm.setValue('skill_id', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner une compétence" />
                      </SelectTrigger>
                      <SelectContent>
                        {skills?.map((skill) => (
                          <SelectItem key={skill.id} value={String(skill.id)}>
                            {skill.name} ({skill.category})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {evalForm.formState.errors.skill_id && (
                      <p className="text-sm text-destructive">
                        {evalForm.formState.errors.skill_id.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="eval-level">Niveau</Label>
                    <Select
                      value={evalForm.watch('level')}
                      onValueChange={(value) => evalForm.setValue('level', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner un niveau" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(levelLabels).map(([value, label]) => (
                          <SelectItem key={value} value={value}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {evalForm.formState.errors.level && (
                      <p className="text-sm text-destructive">
                        {evalForm.formState.errors.level.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="eval-notes">Notes</Label>
                    <Textarea
                      id="eval-notes"
                      placeholder="Observations..."
                      {...evalForm.register('notes')}
                    />
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setEvalDialogOpen(false)}>
                      Annuler
                    </Button>
                    <Button type="submit" disabled={createEvaluationMutation.isPending}>
                      {createEvaluationMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              {skillsLoading || evaluationsLoading ? (
                <div className="space-y-4 p-6">
                  {[...Array(6)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !skills?.length ? (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <Award className="mb-4 h-12 w-12 text-muted-foreground" />
                  <p className="text-muted-foreground">Aucune compétence définie dans le référentiel</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Compétence</TableHead>
                      <TableHead>Catégorie</TableHead>
                      <TableHead>Niveau</TableHead>
                      <TableHead>Date évaluation</TableHead>
                      <TableHead>Évaluateur</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {skills.map((skill) => {
                      const evaluation = evaluationMap.get(skill.id)
                      const level = evaluation?.level || 'not_acquired'
                      return (
                        <TableRow key={skill.id}>
                          <TableCell className="font-medium">{skill.name}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{skill.category}</Badge>
                          </TableCell>
                          <TableCell>
                            <span className={'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ' + (levelColors[level] || 'bg-gray-200 text-gray-800')}>
                              {levelLabels[level] || level}
                            </span>
                          </TableCell>
                          <TableCell>
                            {evaluation ? formatDateDisplay(evaluation.evaluated_at) : '-'}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {evaluation?.evaluated_by_name || '-'}
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trainings tab */}
        <TabsContent value="formations" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Formations</h2>
            <Dialog open={trainingDialogOpen} onOpenChange={(open) => {
              setTrainingDialogOpen(open)
              if (!open) {
                setEditingTraining(null)
                trainingForm.reset()
              }
            }}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Ajouter une formation
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>
                    {editingTraining ? 'Modifier la formation' : 'Nouvelle formation'}
                  </DialogTitle>
                  <DialogDescription>
                    {editingTraining
                      ? 'Modifier les informations de la formation.'
                      : 'Enregistrer une nouvelle formation pour ce bénéficiaire.'}
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={trainingForm.handleSubmit((data) => createTrainingMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="space-y-2">
                    <Label htmlFor="training-title">Titre</Label>
                    <Input
                      id="training-title"
                      placeholder="Titre de la formation"
                      {...trainingForm.register('title')}
                    />
                    {trainingForm.formState.errors.title && (
                      <p className="text-sm text-destructive">
                        {trainingForm.formState.errors.title.message}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="training-start">Date de début</Label>
                      <Input
                        id="training-start"
                        type="date"
                        {...trainingForm.register('start_date')}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="training-end">Date de fin</Label>
                      <Input
                        id="training-end"
                        type="date"
                        {...trainingForm.register('end_date')}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="training-hours">Durée (heures)</Label>
                      <Input
                        id="training-hours"
                        type="number"
                        placeholder="ex: 16"
                        {...trainingForm.register('duration_hours')}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="training-trainer">Formateur</Label>
                      <Input
                        id="training-trainer"
                        placeholder="Nom du formateur"
                        {...trainingForm.register('trainer')}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="training-notes">Notes</Label>
                    <Textarea
                      id="training-notes"
                      placeholder="Remarques sur la formation..."
                      {...trainingForm.register('notes')}
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="training-certificate"
                      {...trainingForm.register('certificate')}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <Label htmlFor="training-certificate">Certificat obtenu</Label>
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setTrainingDialogOpen(false)}>
                      Annuler
                    </Button>
                    <Button type="submit" disabled={createTrainingMutation.isPending}>
                      {createTrainingMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              {trainingsLoading ? (
                <div className="space-y-4 p-6">
                  {[...Array(4)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !trainings?.length ? (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <GraduationCap className="mb-4 h-12 w-12 text-muted-foreground" />
                  <p className="text-muted-foreground">Aucune formation enregistrée</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Titre</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Durée</TableHead>
                      <TableHead>Formateur</TableHead>
                      <TableHead>Certificat</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {trainings.map((training) => (
                      <TableRow key={training.id}>
                        <TableCell className="font-medium">{training.title}</TableCell>
                        <TableCell>{formatDateDisplay(training.start_date)}</TableCell>
                        <TableCell>
                          {training.duration_hours ? String(training.duration_hours) + 'h' : '-'}
                        </TableCell>
                        <TableCell>{training.trainer || '-'}</TableCell>
                        <TableCell>
                          {training.certificate ? (
                            <Badge variant="default" className="bg-green-600">Oui</Badge>
                          ) : (
                            <Badge variant="secondary">Non</Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                setEditingTraining(training.id)
                                trainingForm.reset({
                                  title: training.title,
                                  start_date: training.start_date,
                                  end_date: training.end_date || '',
                                  duration_hours: training.duration_hours ? String(training.duration_hours) : '',
                                  trainer: training.trainer || '',
                                  certificate: training.certificate,
                                  notes: training.notes || '',
                                })
                                setTrainingDialogOpen(true)
                              }}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-destructive"
                              onClick={() => {
                                if (window.confirm('Supprimer cette formation ?')) {
                                  deleteTrainingMutation.mutate(training.id)
                                }
                              }}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
