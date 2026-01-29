import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ChevronLeft, Loader2, Save, X, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { journalApi } from '@/api/journal'
import { beneficiariesApi } from '@/api/beneficiaries'

// ---- Zod Schema ----

const journalSchema = z.object({
  title: z.string().min(1, 'Le titre est requis'),
  content: z.string().min(1, 'Le contenu est requis'),
  beneficiary_id: z.coerce.number().min(1, 'Le beneficiaire est requis'),
  entry_date: z.string().min(1, 'La date est requise'),
  visibility: z.string().min(1, 'La visibilite est requise'),
})

type JournalFormData = z.infer<typeof journalSchema>

// ---- Component ----

export function JournalFormPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const isEdit = Boolean(id) && id !== 'new'
  const entryId = isEdit ? Number(id) : undefined

  const [selectedCategoryIds, setSelectedCategoryIds] = useState<number[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')

  // Fetch existing entry for edit mode
  const { data: existingEntry, isLoading: isLoadingEntry } = useQuery({
    queryKey: ['journal-entry', entryId],
    queryFn: () => journalApi.get(entryId!),
    enabled: isEdit && !!entryId,
  })

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['journal-categories'],
    queryFn: () => journalApi.getCategories(),
  })

  // Fetch beneficiaries for select
  const { data: beneficiariesData } = useQuery({
    queryKey: ['beneficiaries', { page: 1, size: 100 }],
    queryFn: () => beneficiariesApi.list({ page: 1, size: 100 }),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<JournalFormData>({
    resolver: zodResolver(journalSchema),
    defaultValues: {
      title: '',
      content: '',
      beneficiary_id: '' as unknown as number,
      entry_date: new Date().toISOString().split('T')[0],
      visibility: 'team',
    },
  })

  // Populate form when entry data is loaded
  useEffect(() => {
    if (existingEntry) {
      reset({
        title: existingEntry.title,
        content: existingEntry.content,
        beneficiary_id: existingEntry.beneficiary_id,
        entry_date: existingEntry.entry_date?.split('T')[0] || '',
        visibility: existingEntry.visibility,
      })
      setSelectedCategoryIds(existingEntry.categories.map((c) => c.id))
      setTags(existingEntry.tags || [])
    }
  }, [existingEntry, reset])

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: JournalFormData) =>
      journalApi.create({
        ...data,
        visibility: data.visibility as 'team' | 'unit' | 'inter_unit',
        category_ids: selectedCategoryIds,
        tags,
      } as never),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['journal'] })
      navigate(`/journal/${result.id}`)
    },
    onError: (err) => console.error('Erreur creation journal:', err),
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: JournalFormData) =>
      journalApi.update(entryId!, {
        ...data,
        visibility: data.visibility as 'team' | 'unit' | 'inter_unit',
        category_ids: selectedCategoryIds,
        tags,
      } as never),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal-entry', entryId] })
      queryClient.invalidateQueries({ queryKey: ['journal'] })
      navigate(`/journal/${entryId}`)
    },
    onError: (err) => console.error('Erreur mise a jour journal:', err),
  })

  const onSubmit = (data: JournalFormData) => {
    if (isEdit) {
      updateMutation.mutate(data)
    } else {
      createMutation.mutate(data)
    }
  }

  const toggleCategory = (categoryId: number) => {
    setSelectedCategoryIds((prev) =>
      prev.includes(categoryId)
        ? prev.filter((id) => id !== categoryId)
        : [...prev, categoryId]
    )
  }

  const addTag = () => {
    const trimmed = tagInput.trim()
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed])
      setTagInput('')
    }
  }

  const removeTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag))
  }

  const isPending = createMutation.isPending || updateMutation.isPending
  const mutationError = createMutation.error || updateMutation.error

  if (isEdit && isLoadingEntry) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-[200px] w-full" />
        <Skeleton className="h-[300px] w-full" />
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
            {isEdit ? 'Modifier l\'entree' : 'Nouvelle entree de journal'}
          </h1>
          <p className="text-muted-foreground">
            {isEdit
              ? 'Modification de l\'entree de journal'
              : 'Redigez une nouvelle note de suivi'}
          </p>
        </div>
      </div>

      {mutationError && (
        <div className="rounded-md bg-destructive/10 p-4 text-sm text-destructive">
          Une erreur est survenue. Veuillez reessayer.
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Main content */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Contenu</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Titre *</Label>
              <Input
                id="title"
                placeholder="Titre de l'entree..."
                {...register('title')}
              />
              {errors.title && (
                <p className="text-sm text-destructive">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="content">Contenu *</Label>
              <Textarea
                id="content"
                placeholder="Redigez votre observation, note de suivi..."
                rows={10}
                {...register('content')}
              />
              {errors.content && (
                <p className="text-sm text-destructive">{errors.content.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Parametres</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="beneficiary_id">Beneficiaire *</Label>
                <select
                  id="beneficiary_id"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register('beneficiary_id')}
                >
                  <option value="">-- Selectionner --</option>
                  {beneficiariesData?.items.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.first_name} {b.last_name}
                    </option>
                  ))}
                </select>
                {errors.beneficiary_id && (
                  <p className="text-sm text-destructive">{errors.beneficiary_id.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="entry_date">Date de l'entree *</Label>
                <Input id="entry_date" type="date" {...register('entry_date')} />
                {errors.entry_date && (
                  <p className="text-sm text-destructive">{errors.entry_date.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="visibility">Visibilite *</Label>
                <select
                  id="visibility"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register('visibility')}
                >
                  <option value="team">Equipe</option>
                  <option value="unit">Unite</option>
                  <option value="inter_unit">Inter-unites</option>
                </select>
                {errors.visibility && (
                  <p className="text-sm text-destructive">{errors.visibility.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Categories */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Categories</CardTitle>
          </CardHeader>
          <CardContent>
            {categories && categories.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {categories.map((cat) => {
                  const isSelected = selectedCategoryIds.includes(cat.id)
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => toggleCategory(cat.id)}
                      className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium transition-colors ${
                        isSelected
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground hover:bg-muted/80'
                      }`}
                      style={
                        isSelected && cat.color
                          ? { backgroundColor: cat.color, color: 'white' }
                          : undefined
                      }
                    >
                      {cat.label}
                    </button>
                  )
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Aucune categorie disponible</p>
            )}
          </CardContent>
        </Card>

        {/* Tags */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Tags</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <Input
                placeholder="Ajouter un tag..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addTag()
                  }
                }}
              />
              <Button type="button" variant="outline" size="sm" onClick={addTag}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
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
            {isEdit ? 'Enregistrer les modifications' : 'Publier l\'entree'}
          </Button>
        </div>
      </form>
    </div>
  )
}
