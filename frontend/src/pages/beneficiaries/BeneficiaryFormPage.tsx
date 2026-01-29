import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ChevronLeft, Loader2, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { beneficiariesApi } from '@/api/beneficiaries'

// ---- Zod Schema ----

const beneficiarySchema = z.object({
  // Personal info
  first_name: z.string().min(1, 'Le prenom est requis'),
  last_name: z.string().min(1, 'Le nom est requis'),
  date_of_birth: z.string().min(1, 'La date de naissance est requise'),
  address: z.string().optional().or(z.literal('')),
  postal_code: z.string().optional().or(z.literal('')),
  city: z.string().optional().or(z.literal('')),
  phone: z.string().optional().or(z.literal('')),
  email: z.string().email('Email invalide').optional().or(z.literal('')),
  language: z.string().optional().or(z.literal('')),
  // Admin info
  ai_number: z.string().optional().or(z.literal('')),
  pension_type: z.string().optional().or(z.literal('')),
  guardianship_status: z.string().optional().or(z.literal('')),
  entry_date: z.string().min(1, "La date d'entree est requise"),
  // Contract info
  contract_type: z.string().optional().or(z.literal('')),
  occupation_rate: z.coerce.number().min(0).max(100).optional().or(z.literal('')),
  unit_id: z.coerce.number().min(1, "L'unite est requise"),
  referent_id: z.coerce.number().min(1, 'Le referent est requis'),
})

type BeneficiaryFormData = z.infer<typeof beneficiarySchema>

// ---- Component ----

export function BeneficiaryFormPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const isEdit = Boolean(id)
  const beneficiaryId = id ? Number(id) : undefined

  // Fetch existing beneficiary for edit mode
  const { data: beneficiary, isLoading: isLoadingBeneficiary } = useQuery({
    queryKey: ['beneficiary', beneficiaryId],
    queryFn: () => beneficiariesApi.get(beneficiaryId!),
    enabled: isEdit && !!beneficiaryId,
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BeneficiaryFormData>({
    resolver: zodResolver(beneficiarySchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      date_of_birth: '',
      address: '',
      postal_code: '',
      city: '',
      phone: '',
      email: '',
      language: 'fr',
      ai_number: '',
      pension_type: '',
      guardianship_status: '',
      entry_date: '',
      contract_type: '',
      occupation_rate: '',
      unit_id: '' as unknown as number,
      referent_id: '' as unknown as number,
    },
  })

  // Populate form when beneficiary data is loaded
  useEffect(() => {
    if (beneficiary) {
      reset({
        first_name: beneficiary.first_name,
        last_name: beneficiary.last_name,
        date_of_birth: beneficiary.date_of_birth?.split('T')[0] || '',
        address: beneficiary.address || '',
        postal_code: beneficiary.postal_code || '',
        city: beneficiary.city || '',
        phone: beneficiary.phone || '',
        email: beneficiary.email || '',
        language: beneficiary.language || 'fr',
        ai_number: beneficiary.ai_number || '',
        pension_type: beneficiary.pension_type || '',
        guardianship_status: beneficiary.guardianship_status || '',
        entry_date: beneficiary.entry_date?.split('T')[0] || '',
        contract_type: beneficiary.contract_type || '',
        occupation_rate: beneficiary.occupation_rate ?? ('' as unknown as number),
        unit_id: beneficiary.unit_id ?? ('' as unknown as number),
        referent_id: beneficiary.referent_id ?? ('' as unknown as number),
      })
    }
  }, [beneficiary, reset])

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: Partial<BeneficiaryFormData>) => beneficiariesApi.create(data as never),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['beneficiaries'] })
      navigate(`/beneficiaries/${result.id}`)
    },
    onError: (err) => {
      console.error('Erreur lors de la creation:', err)
    },
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: Partial<BeneficiaryFormData>) =>
      beneficiariesApi.update(beneficiaryId!, data as never),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beneficiary', beneficiaryId] })
      queryClient.invalidateQueries({ queryKey: ['beneficiaries'] })
      navigate(`/beneficiaries/${beneficiaryId}`)
    },
    onError: (err) => {
      console.error('Erreur lors de la mise a jour:', err)
    },
  })

  const onSubmit = (data: BeneficiaryFormData) => {
    // Clean data: convert empty strings to null
    const cleanedData: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(data)) {
      cleanedData[key] = value === '' ? null : value
    }

    if (isEdit) {
      updateMutation.mutate(cleanedData as Partial<BeneficiaryFormData>)
    } else {
      createMutation.mutate(cleanedData as Partial<BeneficiaryFormData>)
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending
  const mutationError = createMutation.error || updateMutation.error

  if (isEdit && isLoadingBeneficiary) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-3 text-lg">Chargement des donnees...</span>
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
            {isEdit ? 'Modifier le beneficiaire' : 'Nouveau beneficiaire'}
          </h1>
          <p className="text-muted-foreground">
            {isEdit
              ? `Modification de ${beneficiary?.first_name} ${beneficiary?.last_name}`
              : 'Remplissez les informations du nouveau beneficiaire'}
          </p>
        </div>
      </div>

      {mutationError && (
        <div className="rounded-md bg-destructive/10 p-4 text-sm text-destructive">
          Une erreur est survenue. Veuillez reessayer.
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Section 1: Personal Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Informations personnelles</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="first_name">Prenom *</Label>
                <Input id="first_name" {...register('first_name')} />
                {errors.first_name && (
                  <p className="text-sm text-destructive">{errors.first_name.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Nom *</Label>
                <Input id="last_name" {...register('last_name')} />
                {errors.last_name && (
                  <p className="text-sm text-destructive">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="date_of_birth">Date de naissance *</Label>
                <Input id="date_of_birth" type="date" {...register('date_of_birth')} />
                {errors.date_of_birth && (
                  <p className="text-sm text-destructive">{errors.date_of_birth.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="language">Langue</Label>
                <select
                  id="language"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register('language')}
                >
                  <option value="fr">Francais</option>
                  <option value="de">Allemand</option>
                  <option value="it">Italien</option>
                  <option value="en">Anglais</option>
                  <option value="other">Autre</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Adresse</Label>
              <Input id="address" {...register('address')} />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="postal_code">Code postal</Label>
                <Input id="postal_code" {...register('postal_code')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="city">Ville</Label>
                <Input id="city" {...register('city')} />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="phone">Telephone</Label>
                <Input id="phone" type="tel" {...register('phone')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" {...register('email')} />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Section 2: Admin Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Informations administratives</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="ai_number">Numero AI</Label>
                <Input id="ai_number" {...register('ai_number')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="pension_type">Type de rente</Label>
                <select
                  id="pension_type"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register('pension_type')}
                >
                  <option value="">-- Selectionner --</option>
                  <option value="quarter">Quart de rente</option>
                  <option value="half">Demi-rente</option>
                  <option value="three_quarter">Trois-quarts de rente</option>
                  <option value="full">Rente entiere</option>
                </select>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="guardianship_status">Curatelle</Label>
                <select
                  id="guardianship_status"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register('guardianship_status')}
                >
                  <option value="">Aucune</option>
                  <option value="conseil_legal">Conseil legal</option>
                  <option value="curatelle_representation">Curatelle de representation</option>
                  <option value="curatelle_cooperation">Curatelle de cooperation</option>
                  <option value="curatelle_portee_generale">Curatelle de portee generale</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="entry_date">Date d'entree *</Label>
                <Input id="entry_date" type="date" {...register('entry_date')} />
                {errors.entry_date && (
                  <p className="text-sm text-destructive">{errors.entry_date.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Section 3: Contract Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Contrat</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="contract_type">Type de contrat</Label>
                <select
                  id="contract_type"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register('contract_type')}
                >
                  <option value="">-- Selectionner --</option>
                  <option value="formation">Formation</option>
                  <option value="occupation">Occupation</option>
                  <option value="evaluation">Evaluation</option>
                  <option value="integration">Integration</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="occupation_rate">Taux d'occupation (%)</Label>
                <Input
                  id="occupation_rate"
                  type="number"
                  min={0}
                  max={100}
                  {...register('occupation_rate')}
                />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="unit_id">Unite *</Label>
                <Input
                  id="unit_id"
                  type="number"
                  placeholder="ID de l'unite"
                  {...register('unit_id')}
                />
                {errors.unit_id && (
                  <p className="text-sm text-destructive">{errors.unit_id.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="referent_id">MSP referent *</Label>
                <Input
                  id="referent_id"
                  type="number"
                  placeholder="ID du referent"
                  {...register('referent_id')}
                />
                {errors.referent_id && (
                  <p className="text-sm text-destructive">{errors.referent_id.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex items-center justify-end gap-4">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Annuler
          </Button>
          <Button type="submit" disabled={isPending || isSubmitting}>
            {(isPending || isSubmitting) && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            <Save className="mr-2 h-4 w-4" />
            {isEdit ? 'Enregistrer les modifications' : 'Creer le beneficiaire'}
          </Button>
        </div>
      </form>
    </div>
  )
}
