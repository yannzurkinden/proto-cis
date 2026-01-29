import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ChevronLeft, Loader2, Save, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { paisApi } from '@/api/pais'
import { beneficiariesApi } from '@/api/beneficiaries'

// ---- Zod Schema ----

const objectiveSchema = z.object({
  title: z.string().min(1, "Le titre de l'objectif est requis"),
  description: z.string().optional().or(z.literal('')),
  objective_type: z.enum(['pai', 'behavioral', 'operational']),
  term: z.enum(['short', 'medium', 'long']),
  priority: z.enum(['high', 'medium', 'low']),
  due_date: z.string().optional().or(z.literal('')),
})

const paiSchema = z.object({
  valid_from: z.string().min(1, 'La date de debut est requise'),
  valid_to: z.string().optional().or(z.literal('')),
  strengths: z.string().optional().or(z.literal('')),
  difficulties: z.string().optional().or(z.literal('')),
  beneficiary_wishes: z.string().optional().or(z.literal('')),
  objectives: z.array(objectiveSchema),
})

type PAIFormData = z.infer<typeof paiSchema>

// ---- Component ----

export function PAIFormPage() {
  const { beneficiaryId, paiId } = useParams<{ beneficiaryId: string; paiId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const numBeneficiaryId = Number(beneficiaryId)
  const numPaiId = paiId ? Number(paiId) : undefined
  const isEdit = Boolean(numPaiId)

  // Fetch beneficiary name
  const { data: beneficiary } = useQuery({
    queryKey: ['beneficiary', numBeneficiaryId],
    queryFn: () => beneficiariesApi.get(numBeneficiaryId),
    enabled: !!numBeneficiaryId,
  })

  // Fetch existing PAI for edit
  const { data: existingPai, isLoading: isLoadingPai } = useQuery({
    queryKey: ['pai', numBeneficiaryId, numPaiId],
    queryFn: () => paisApi.get(numBeneficiaryId, numPaiId!),
    enabled: isEdit && !!numPaiId,
  })

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<PAIFormData>({
    resolver: zodResolver(paiSchema),
    defaultValues: {
      valid_from: '',
      valid_to: '',
      strengths: '',
      difficulties: '',
      beneficiary_wishes: '',
      objectives: [],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'objectives',
  })

  // Populate form when editing
  useEffect(() => {
    if (existingPai) {
      reset({
        valid_from: existingPai.valid_from?.split('T')[0] || '',
        valid_to: existingPai.valid_to?.split('T')[0] || '',
        strengths: existingPai.strengths || '',
        difficulties: existingPai.difficulties || '',
        beneficiary_wishes: existingPai.beneficiary_wishes || '',
        objectives: (existingPai.objectives || []).map((obj) => ({
          title: obj.title,
          description: '',
          objective_type: obj.objective_type as 'pai' | 'behavioral' | 'operational',
          term: obj.term as 'short' | 'medium' | 'long',
          priority: 'medium' as const,
          due_date: obj.due_date?.split('T')[0] || '',
        })),
      })
    }
  }, [existingPai, reset])

  const createMutation = useMutation({
    mutationFn: (data: PAIFormData) => {
      const payload = {
        ...data,
        valid_to: data.valid_to || null,
        strengths: data.strengths || null,
        difficulties: data.difficulties || null,
        beneficiary_wishes: data.beneficiary_wishes || null,
        objectives: data.objectives.map((obj) => ({
          ...obj,
          description: obj.description || undefined,
          due_date: obj.due_date || null,
        })),
      }
      return paisApi.create(numBeneficiaryId, payload)
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['beneficiary', numBeneficiaryId] })
      navigate(`/beneficiaries/${numBeneficiaryId}/pais/${result.id}`)
    },
    onError: (err) => console.error('Erreur creation PAI:', err),
  })

  const updateMutation = useMutation({
    mutationFn: (data: PAIFormData) => {
      const payload = {
        ...data,
        valid_to: data.valid_to || null,
        strengths: data.strengths || null,
        difficulties: data.difficulties || null,
        beneficiary_wishes: data.beneficiary_wishes || null,
        objectives: data.objectives.map((obj) => ({
          ...obj,
          description: obj.description || undefined,
          due_date: obj.due_date || null,
        })),
      }
      return paisApi.update(numBeneficiaryId, numPaiId!, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pai', numBeneficiaryId, numPaiId] })
      queryClient.invalidateQueries({ queryKey: ['beneficiary', numBeneficiaryId] })
      navigate(`/beneficiaries/${numBeneficiaryId}/pais/${numPaiId}`)
    },
    onError: (err) => console.error('Erreur mise a jour PAI:', err),
  })

  const onSubmit = (data: PAIFormData) => {
    if (isEdit) {
      updateMutation.mutate(data)
    } else {
      createMutation.mutate(data)
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending
  const mutationError = createMutation.error || updateMutation.error

  if (isEdit && isLoadingPai) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-3 text-lg">Chargement du PAI...</span>
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
        <div>
          <h1 className="text-2xl font-bold">
            {isEdit ? 'Modifier le PAI' : 'Nouveau PAI'}
          </h1>
          {beneficiary && (
            <p className="text-muted-foreground">
              Pour {beneficiary.first_name} {beneficiary.last_name}
            </p>
          )}
        </div>
      </div>

      {mutationError && (
        <div className="rounded-md bg-destructive/10 p-4 text-sm text-destructive">
          Une erreur est survenue. Veuillez reessayer.
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Dates */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Periode</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="valid_from">Date de debut *</Label>
                <Input id="valid_from" type="date" {...register('valid_from')} />
                {errors.valid_from && (
                  <p className="text-sm text-destructive">{errors.valid_from.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="valid_to">Date de fin</Label>
                <Input id="valid_to" type="date" {...register('valid_to')} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bilan initial */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Bilan initial</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="strengths">Points forts</Label>
              <textarea
                id="strengths"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Forces, ressources, competences du beneficiaire..."
                {...register('strengths')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="difficulties">Difficultes</Label>
              <textarea
                id="difficulties"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Points a travailler, obstacles identifies..."
                {...register('difficulties')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="beneficiary_wishes">Souhaits du beneficiaire</Label>
              <textarea
                id="beneficiary_wishes"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Aspirations, objectifs personnels du beneficiaire..."
                {...register('beneficiary_wishes')}
              />
            </div>
          </CardContent>
        </Card>

        {/* Objectives */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Objectifs</CardTitle>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() =>
                append({
                  title: '',
                  description: '',
                  objective_type: 'pai',
                  term: 'short',
                  priority: 'medium',
                  due_date: '',
                })
              }
            >
              <Plus className="mr-2 h-4 w-4" />
              Ajouter un objectif
            </Button>
          </CardHeader>
          <CardContent className="space-y-6">
            {fields.length === 0 && (
              <p className="text-center text-muted-foreground py-4">
                Aucun objectif. Cliquez sur "Ajouter un objectif" pour commencer.
              </p>
            )}

            {fields.map((field, index) => (
              <div
                key={field.id}
                className="rounded-lg border p-4 space-y-4 relative"
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Objectif {index + 1}</h4>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => remove(index)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>

                <div className="space-y-2">
                  <Label>Titre *</Label>
                  <Input {...register(`objectives.${index}.title`)} />
                  {errors.objectives?.[index]?.title && (
                    <p className="text-sm text-destructive">
                      {errors.objectives[index]?.title?.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Description</Label>
                  <textarea
                    className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    {...register(`objectives.${index}.description`)}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label>Type</Label>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      {...register(`objectives.${index}.objective_type`)}
                    >
                      <option value="pai">PAI</option>
                      <option value="behavioral">Comportemental</option>
                      <option value="operational">Operationnel</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label>Terme</Label>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      {...register(`objectives.${index}.term`)}
                    >
                      <option value="short">Court terme</option>
                      <option value="medium">Moyen terme</option>
                      <option value="long">Long terme</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label>Priorite</Label>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      {...register(`objectives.${index}.priority`)}
                    >
                      <option value="high">Haute</option>
                      <option value="medium">Moyenne</option>
                      <option value="low">Basse</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Date d'echeance</Label>
                  <Input type="date" {...register(`objectives.${index}.due_date`)} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex items-center justify-end gap-4">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Annuler
          </Button>
          <Button type="submit" disabled={isPending}>
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            <Save className="mr-2 h-4 w-4" />
            {isEdit ? 'Enregistrer les modifications' : 'Creer le PAI'}
          </Button>
        </div>
      </form>
    </div>
  )
}
