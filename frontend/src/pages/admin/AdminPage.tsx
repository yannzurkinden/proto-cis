import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Shield,
  Users,
  Building,
  Tag,
  Star,
  ScrollText,
  Plus,
  Edit,
  UserX,
  Search,
  Trash2,
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
import { adminApi } from '@/api/admin'

// Schemas
const userSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(8, 'Minimum 8 caractères'),
  first_name: z.string().min(1, 'Prénom requis'),
  last_name: z.string().min(1, 'Nom requis'),
  role: z.string().min(1, 'Rôle requis'),
  unit_id: z.string().optional(),
})

type UserForm = z.infer<typeof userSchema>

const unitSchema = z.object({
  name: z.string().min(1, 'Nom requis'),
  description: z.string().optional(),
})

type UnitForm = z.infer<typeof unitSchema>

const categorySchema = z.object({
  name: z.string().min(1, 'Nom requis'),
  label: z.string().min(1, 'Label requis'),
  color: z.string().optional(),
  icon: z.string().optional(),
})

type CategoryForm = z.infer<typeof categorySchema>

const skillSchema = z.object({
  name: z.string().min(1, 'Nom requis'),
  category: z.string().min(1, 'Catégorie requise'),
  description: z.string().optional(),
})

type SkillForm = z.infer<typeof skillSchema>

const roleLabels: Record<string, string> = {
  ADMIN: 'Administrateur',
  RUA: 'Responsable (RUA)',
  RES: 'Responsable (RES)',
  MSP: 'MSP',
  CONSULT: 'Consultation',
}

export function AdminPage() {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()

  const [activeTab, setActiveTab] = useState('users')
  const [userDialogOpen, setUserDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<{ id: number; first_name: string; last_name: string; role: string; unit_id: number | null } | null>(null)
  const [unitDialogOpen, setUnitDialogOpen] = useState(false)
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false)
  const [skillDialogOpen, setSkillDialogOpen] = useState(false)
  const [editingUnit, setEditingUnit] = useState<number | null>(null)
  const [editingCategory, setEditingCategory] = useState<number | null>(null)
  const [editingSkill, setEditingSkill] = useState<number | null>(null)
  const [userSearch, setUserSearch] = useState('')
  const [auditDateFrom, setAuditDateFrom] = useState('')
  const [auditDateTo, setAuditDateTo] = useState('')
  const [auditAction, setAuditAction] = useState('')
  const [auditPage, setAuditPage] = useState(1)

  // Check access
  const isAdmin = user?.role === 'ADMIN' || user?.role === 'RUA'

  // Queries
  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users', { search: userSearch }],
    queryFn: () => adminApi.listUsers({ search: userSearch || undefined, size: 50 }),
  })

  const { data: units, isLoading: unitsLoading } = useQuery({
    queryKey: ['admin-units'],
    queryFn: () => adminApi.listUnits(),
  })

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: () => adminApi.listCategories(),
  })

  const { data: skills, isLoading: skillsLoading } = useQuery({
    queryKey: ['admin-skills'],
    queryFn: () => adminApi.listSkills(),
  })

  const { data: auditLogs, isLoading: auditLoading } = useQuery({
    queryKey: ['admin-audit-logs', { page: auditPage, date_from: auditDateFrom, date_to: auditDateTo, action: auditAction }],
    queryFn: () => adminApi.listAuditLogs({
      page: auditPage,
      size: 20,
      date_from: auditDateFrom || undefined,
      date_to: auditDateTo || undefined,
      action: auditAction || undefined,
    }),
  })

  // Mutations
  const createUserMutation = useMutation({
    mutationFn: (data: UserForm) =>
      adminApi.createUser({
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
        role: data.role,
        unit_id: data.unit_id ? Number(data.unit_id) : null,
        is_active: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      setUserDialogOpen(false)
      userFormHook.reset()
    },
  })

  const deactivateUserMutation = useMutation({
    mutationFn: (userId: number) => adminApi.deactivateUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
  })

  const updateUserMutation = useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: { first_name?: string; last_name?: string; role?: string; unit_id?: number | null } }) =>
      adminApi.updateUser(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      setEditingUser(null)
    },
  })

  const createUnitMutation = useMutation({
    mutationFn: (data: UnitForm) => {
      if (editingUnit) {
        return adminApi.updateUnit(editingUnit, data)
      }
      return adminApi.createUnit(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-units'] })
      setUnitDialogOpen(false)
      setEditingUnit(null)
      unitFormHook.reset()
    },
  })

  const createCategoryMutation = useMutation({
    mutationFn: (data: CategoryForm) => {
      if (editingCategory) {
        return adminApi.updateCategory(editingCategory, data)
      }
      return adminApi.createCategory(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-categories'] })
      setCategoryDialogOpen(false)
      setEditingCategory(null)
      categoryFormHook.reset()
    },
  })

  const createSkillMutation = useMutation({
    mutationFn: (data: SkillForm) => {
      if (editingSkill) {
        return adminApi.updateSkill(editingSkill, data)
      }
      return adminApi.createSkill(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-skills'] })
      setSkillDialogOpen(false)
      setEditingSkill(null)
      skillFormHook.reset()
    },
  })

  const deleteSkillMutation = useMutation({
    mutationFn: (id: number) => adminApi.deleteSkill(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-skills'] })
    },
  })

  // Forms
  const userFormHook = useForm<UserForm>({
    resolver: zodResolver(userSchema),
    defaultValues: { email: '', password: '', first_name: '', last_name: '', role: 'MSP', unit_id: '' },
  })

  const unitFormHook = useForm<UnitForm>({
    resolver: zodResolver(unitSchema),
    defaultValues: { name: '', description: '' },
  })

  const categoryFormHook = useForm<CategoryForm>({
    resolver: zodResolver(categorySchema),
    defaultValues: { name: '', label: '', color: '#3b82f6', icon: '' },
  })

  const skillFormHook = useForm<SkillForm>({
    resolver: zodResolver(skillSchema),
    defaultValues: { name: '', category: '', description: '' },
  })

  const formatDateDisplay = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'dd MMM yyyy HH:mm', { locale: fr })
    } catch {
      return dateStr
    }
  }

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <Shield className="mb-4 h-16 w-16 text-muted-foreground" />
        <h1 className="text-2xl font-bold">Accès refusé</h1>
        <p className="text-muted-foreground">
          Vous n'avez pas les droits pour accéder à cette page.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Administration</h1>
        <p className="text-muted-foreground">Gestion du système et des paramètres</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="flex-wrap">
          <TabsTrigger value="users">
            <Users className="mr-2 h-4 w-4" />
            Utilisateurs
          </TabsTrigger>
          <TabsTrigger value="units">
            <Building className="mr-2 h-4 w-4" />
            Unités
          </TabsTrigger>
          <TabsTrigger value="categories">
            <Tag className="mr-2 h-4 w-4" />
            Catégories journal
          </TabsTrigger>
          <TabsTrigger value="skills">
            <Star className="mr-2 h-4 w-4" />
            Référentiel compétences
          </TabsTrigger>
          <TabsTrigger value="audit">
            <ScrollText className="mr-2 h-4 w-4" />
            Logs d'audit
          </TabsTrigger>
        </TabsList>

        {/* Users tab */}
        <TabsContent value="users" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Rechercher..."
                className="pl-9"
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
              />
            </div>
            <Dialog open={userDialogOpen} onOpenChange={setUserDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nouvel utilisateur
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Créer un utilisateur</DialogTitle>
                  <DialogDescription>
                    Remplir les informations du nouvel utilisateur.
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={userFormHook.handleSubmit((data) => createUserMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Prénom</Label>
                      <Input {...userFormHook.register('first_name')} />
                      {userFormHook.formState.errors.first_name && (
                        <p className="text-sm text-destructive">{userFormHook.formState.errors.first_name.message}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label>Nom</Label>
                      <Input {...userFormHook.register('last_name')} />
                      {userFormHook.formState.errors.last_name && (
                        <p className="text-sm text-destructive">{userFormHook.formState.errors.last_name.message}</p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input type="email" {...userFormHook.register('email')} />
                    {userFormHook.formState.errors.email && (
                      <p className="text-sm text-destructive">{userFormHook.formState.errors.email.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Mot de passe</Label>
                    <Input type="password" {...userFormHook.register('password')} />
                    {userFormHook.formState.errors.password && (
                      <p className="text-sm text-destructive">{userFormHook.formState.errors.password.message}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Rôle</Label>
                      <Select
                        value={userFormHook.watch('role')}
                        onValueChange={(v) => userFormHook.setValue('role', v)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(roleLabels).map(([value, label]) => (
                            <SelectItem key={value} value={value}>{label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Unité</Label>
                      <Select
                        value={userFormHook.watch('unit_id') || ''}
                        onValueChange={(v) => userFormHook.setValue('unit_id', v)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Aucune" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">Aucune</SelectItem>
                          {units?.map((unit) => (
                            <SelectItem key={unit.id} value={String(unit.id)}>{unit.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setUserDialogOpen(false)}>Annuler</Button>
                    <Button type="submit" disabled={createUserMutation.isPending}>
                      {createUserMutation.isPending ? 'Création...' : 'Créer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              {usersLoading ? (
                <div className="space-y-4 p-6">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nom</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Unite</TableHead>
                      <TableHead>Actif</TableHead>
                      <TableHead>Dernière connexion</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usersData?.items.map((u) => (
                      <TableRow key={u.id}>
                        <TableCell className="font-medium">
                          {u.first_name} {u.last_name}
                        </TableCell>
                        <TableCell>{u.email}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{roleLabels[u.role] || u.role}</Badge>
                        </TableCell>
                        <TableCell>{u.unit_name || '-'}</TableCell>
                        <TableCell>
                          {u.is_active ? (
                            <Badge variant="default" className="bg-green-600">Actif</Badge>
                          ) : (
                            <Badge variant="secondary">Inactif</Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {u.last_login ? formatDateDisplay(u.last_login) : 'Jamais'}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setEditingUser({
                                id: u.id,
                                first_name: u.first_name,
                                last_name: u.last_name,
                                role: u.role,
                                unit_id: u.unit_id,
                              })}
                            >
                              <Edit className="mr-1 h-3 w-3" />
                              Modifier
                            </Button>
                            {u.is_active && u.id !== user?.id && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive"
                                onClick={() => {
                                  if (window.confirm('Désactiver cet utilisateur ?')) {
                                    deactivateUserMutation.mutate(u.id)
                                  }
                                }}
                              >
                                <UserX className="mr-1 h-3 w-3" />
                                Désactiver
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Edit User Dialog */}
          <Dialog open={!!editingUser} onOpenChange={(open) => { if (!open) setEditingUser(null) }}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Modifier l'utilisateur</DialogTitle>
                <DialogDescription>
                  Modifier les informations de l'utilisateur.
                </DialogDescription>
              </DialogHeader>
              {editingUser && (
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    const formData = new FormData(e.currentTarget)
                    const unitVal = formData.get('edit_unit_id') as string
                    updateUserMutation.mutate({
                      userId: editingUser.id,
                      data: {
                        first_name: formData.get('edit_first_name') as string,
                        last_name: formData.get('edit_last_name') as string,
                        role: formData.get('edit_role') as string,
                        unit_id: unitVal && unitVal !== 'none' ? Number(unitVal) : null,
                      },
                    })
                  }}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Prénom</Label>
                      <Input name="edit_first_name" defaultValue={editingUser.first_name} />
                    </div>
                    <div className="space-y-2">
                      <Label>Nom</Label>
                      <Input name="edit_last_name" defaultValue={editingUser.last_name} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Rôle</Label>
                      <select
                        name="edit_role"
                        defaultValue={editingUser.role}
                        className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                      >
                        {Object.entries(roleLabels).map(([value, label]) => (
                          <option key={value} value={value}>{label}</option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label>Unité</Label>
                      <select
                        name="edit_unit_id"
                        defaultValue={editingUser.unit_id ? String(editingUser.unit_id) : 'none'}
                        className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                      >
                        <option value="none">Aucune</option>
                        {units?.map((unit) => (
                          <option key={unit.id} value={String(unit.id)}>{unit.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setEditingUser(null)}>Annuler</Button>
                    <Button type="submit" disabled={updateUserMutation.isPending}>
                      {updateUserMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              )}
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* Units tab */}
        <TabsContent value="units" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Unités</h2>
            <Dialog open={unitDialogOpen} onOpenChange={(open) => {
              setUnitDialogOpen(open)
              if (!open) { setEditingUnit(null); unitFormHook.reset() }
            }}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nouvelle unité
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{editingUnit ? 'Modifier l\'unité' : 'Nouvelle unité'}</DialogTitle>
                  <DialogDescription>
                    {editingUnit ? 'Modifier les informations de l\'unite.' : 'Créer une nouvelle unité organisationnelle.'}
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={unitFormHook.handleSubmit((data) => createUnitMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="space-y-2">
                    <Label>Nom</Label>
                    <Input {...unitFormHook.register('name')} />
                    {unitFormHook.formState.errors.name && (
                      <p className="text-sm text-destructive">{unitFormHook.formState.errors.name.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Textarea {...unitFormHook.register('description')} placeholder="Description de l'unite..." />
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setUnitDialogOpen(false)}>Annuler</Button>
                    <Button type="submit" disabled={createUnitMutation.isPending}>
                      {createUnitMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {unitsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))}
            </div>
          ) : !units?.length ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center p-8">
                <Building className="mb-4 h-12 w-12 text-muted-foreground" />
                <p className="text-muted-foreground">Aucune unite definie</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {units.map((unit) => (
                <Card key={unit.id}>
                  <CardHeader className="flex flex-row items-start justify-between">
                    <div>
                      <CardTitle className="text-base">{unit.name}</CardTitle>
                      <CardDescription>{unit.description || 'Aucune description'}</CardDescription>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingUnit(unit.id)
                        unitFormHook.reset({ name: unit.name, description: unit.description || '' })
                        setUnitDialogOpen(true)
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Journal categories tab */}
        <TabsContent value="categories" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Categories du journal</h2>
            <Dialog open={categoryDialogOpen} onOpenChange={(open) => {
              setCategoryDialogOpen(open)
              if (!open) { setEditingCategory(null); categoryFormHook.reset() }
            }}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nouvelle categorie
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{editingCategory ? 'Modifier la categorie' : 'Nouvelle categorie'}</DialogTitle>
                  <DialogDescription>
                    Definir une categorie pour les entrees du journal.
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={categoryFormHook.handleSubmit((data) => createCategoryMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Nom (identifiant)</Label>
                      <Input {...categoryFormHook.register('name')} placeholder="ex: entretien" />
                      {categoryFormHook.formState.errors.name && (
                        <p className="text-sm text-destructive">{categoryFormHook.formState.errors.name.message}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label>Label (affichage)</Label>
                      <Input {...categoryFormHook.register('label')} placeholder="ex: Entretien individuel" />
                      {categoryFormHook.formState.errors.label && (
                        <p className="text-sm text-destructive">{categoryFormHook.formState.errors.label.message}</p>
                      )}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Couleur</Label>
                      <Input type="color" {...categoryFormHook.register('color')} />
                    </div>
                    <div className="space-y-2">
                      <Label>Icone</Label>
                      <Input {...categoryFormHook.register('icon')} placeholder="ex: message-circle" />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setCategoryDialogOpen(false)}>Annuler</Button>
                    <Button type="submit" disabled={createCategoryMutation.isPending}>
                      {createCategoryMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {categoriesLoading ? (
            <div className="space-y-4">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : !categories?.length ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center p-8">
                <Tag className="mb-4 h-12 w-12 text-muted-foreground" />
                <p className="text-muted-foreground">Aucune categorie definie</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-3">
              {categories.map((cat) => (
                <Card key={cat.id}>
                  <CardContent className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-4">
                      {cat.color && (
                        <div
                          className="h-6 w-6 rounded-full"
                          style={{ backgroundColor: cat.color }}
                        />
                      )}
                      <div>
                        <p className="font-medium">{cat.label}</p>
                        <p className="text-sm text-muted-foreground">{cat.name}</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingCategory(cat.id)
                        categoryFormHook.reset({
                          name: cat.name,
                          label: cat.label,
                          color: cat.color || '#3b82f6',
                          icon: cat.icon || '',
                        })
                        setCategoryDialogOpen(true)
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Skills reference tab */}
        <TabsContent value="skills" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Referentiel de competences</h2>
            <Dialog open={skillDialogOpen} onOpenChange={(open) => {
              setSkillDialogOpen(open)
              if (!open) { setEditingSkill(null); skillFormHook.reset() }
            }}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nouvelle competence
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{editingSkill ? 'Modifier la competence' : 'Nouvelle competence'}</DialogTitle>
                  <DialogDescription>
                    Definir une competence du referentiel.
                  </DialogDescription>
                </DialogHeader>
                <form
                  onSubmit={skillFormHook.handleSubmit((data) => createSkillMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div className="space-y-2">
                    <Label>Nom</Label>
                    <Input {...skillFormHook.register('name')} placeholder="Nom de la competence" />
                    {skillFormHook.formState.errors.name && (
                      <p className="text-sm text-destructive">{skillFormHook.formState.errors.name.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label>Categorie</Label>
                    <Input {...skillFormHook.register('category')} placeholder="ex: Savoir-faire, Savoir-etre" />
                    {skillFormHook.formState.errors.category && (
                      <p className="text-sm text-destructive">{skillFormHook.formState.errors.category.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Textarea {...skillFormHook.register('description')} placeholder="Description de la competence..." />
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setSkillDialogOpen(false)}>Annuler</Button>
                    <Button type="submit" disabled={createSkillMutation.isPending}>
                      {createSkillMutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              {skillsLoading ? (
                <div className="space-y-4 p-6">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !skills?.length ? (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <Star className="mb-4 h-12 w-12 text-muted-foreground" />
                  <p className="text-muted-foreground">Aucune competence definie</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nom</TableHead>
                      <TableHead>Categorie</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {skills.map((skill) => (
                      <TableRow key={skill.id}>
                        <TableCell className="font-medium">{skill.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{skill.category}</Badge>
                        </TableCell>
                        <TableCell className="max-w-[300px] truncate text-muted-foreground">
                          {skill.description || '-'}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                setEditingSkill(skill.id)
                                skillFormHook.reset({
                                  name: skill.name,
                                  category: skill.category,
                                  description: skill.description || '',
                                })
                                setSkillDialogOpen(true)
                              }}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-destructive"
                              onClick={() => {
                                if (window.confirm('Supprimer cette competence ?')) {
                                  deleteSkillMutation.mutate(skill.id)
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

        {/* Audit logs tab */}
        <TabsContent value="audit" className="space-y-4">
          <h2 className="text-lg font-semibold">Logs d'audit</h2>

          <div className="flex flex-wrap items-center gap-4">
            <div className="space-y-1">
              <Label className="text-xs">Date debut</Label>
              <Input
                type="date"
                value={auditDateFrom}
                onChange={(e) => { setAuditDateFrom(e.target.value); setAuditPage(1) }}
                className="w-[160px]"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Date fin</Label>
              <Input
                type="date"
                value={auditDateTo}
                onChange={(e) => { setAuditDateTo(e.target.value); setAuditPage(1) }}
                className="w-[160px]"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Action</Label>
              <Select value={auditAction} onValueChange={(v) => { setAuditAction(v === 'all' ? '' : v); setAuditPage(1) }}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Toutes les actions" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes les actions</SelectItem>
                  <SelectItem value="create">Creation</SelectItem>
                  <SelectItem value="update">Modification</SelectItem>
                  <SelectItem value="delete">Suppression</SelectItem>
                  <SelectItem value="login">Connexion</SelectItem>
                  <SelectItem value="export">Export</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              {auditLoading ? (
                <div className="space-y-4 p-6">
                  {[...Array(8)].map((_, i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : !auditLogs?.items.length ? (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <ScrollText className="mb-4 h-12 w-12 text-muted-foreground" />
                  <p className="text-muted-foreground">Aucun log d'audit trouve</p>
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Utilisateur</TableHead>
                        <TableHead>Action</TableHead>
                        <TableHead>Entite</TableHead>
                        <TableHead>Details</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {auditLogs.items.map((log) => (
                        <TableRow key={log.id}>
                          <TableCell className="text-sm">
                            {formatDateDisplay(log.created_at)}
                          </TableCell>
                          <TableCell className="font-medium">{log.user_name}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{log.action}</Badge>
                          </TableCell>
                          <TableCell>{log.entity_type}</TableCell>
                          <TableCell className="max-w-[300px] truncate text-sm text-muted-foreground">
                            {log.details || '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {auditLogs.pages > 1 && (
                    <div className="flex items-center justify-between border-t p-4">
                      <p className="text-sm text-muted-foreground">
                        Page {auditPage} sur {auditLogs.pages} ({auditLogs.total} resultats)
                      </p>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={auditPage === 1}
                          onClick={() => setAuditPage(auditPage - 1)}
                        >
                          Precedent
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={auditPage === auditLogs.pages}
                          onClick={() => setAuditPage(auditPage + 1)}
                        >
                          Suivant
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
