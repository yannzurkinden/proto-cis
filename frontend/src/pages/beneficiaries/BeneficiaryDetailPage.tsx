import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  User,
  Heart,
  Users,
  AlertTriangle,
  Target,
  BookOpen,
  Clock,
  Star,
  FileText,
  Edit,
  Trash2,
  Plus,
  Lock,
  Download,
  Upload,
  Phone,
  Mail,
  MapPin,
  Calendar,
  ChevronLeft,
  Loader2,
  X,
} from 'lucide-react'
import { format, parseISO, formatDistance } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { beneficiariesApi } from '@/api/beneficiaries'
import { objectivesApi } from '@/api/objectives'
import { journalApi } from '@/api/journal'
import { skillsApi } from '@/api/skills'
import { timeTrackingApi } from '@/api/timeTracking'
import { documentsApi } from '@/api/documents'
import { useAuthStore } from '@/stores/authStore'
import type { Contact, Beneficiary } from '@/types/api'

// ---- Helpers ----

function getStatusBadge(status: string) {
  switch (status) {
    case 'active':
      return <Badge variant="success">Actif</Badge>
    case 'paused':
      return <Badge variant="warning">En pause</Badge>
    case 'exited':
      return <Badge variant="secondary">Sorti</Badge>
    case 'draft':
      return <Badge variant="outline">Brouillon</Badge>
    default:
      return <Badge>{status}</Badge>
  }
}

function getObjectiveStatusBadge(status: string) {
  switch (status) {
    case 'achieved':
      return <Badge variant="success">Atteint</Badge>
    case 'in_progress':
      return <Badge variant="default">En cours</Badge>
    case 'pending':
      return <Badge variant="outline">En attente</Badge>
    case 'abandoned':
      return <Badge variant="secondary">Abandonne</Badge>
    default:
      return <Badge>{status}</Badge>
  }
}

function getObjectiveTypeBadge(type: string) {
  switch (type) {
    case 'pai':
      return <Badge variant="default">PAI</Badge>
    case 'behavioral':
      return <Badge variant="warning">Comportemental</Badge>
    case 'operational':
      return <Badge variant="secondary">Operationnel</Badge>
    default:
      return <Badge>{type}</Badge>
  }
}

function getPensionTypeLabel(type: string | null) {
  switch (type) {
    case 'quarter':
      return 'Quart de rente'
    case 'half':
      return 'Demi-rente'
    case 'three_quarter':
      return 'Trois-quarts de rente'
    case 'full':
      return 'Rente entiere'
    default:
      return type || '-'
  }
}

function getContactTypeLabel(type: string) {
  switch (type) {
    case 'emergency':
      return 'Urgence'
    case 'doctor':
      return 'Medecin'
    case 'psychologist':
      return 'Psychologue'
    case 'ai_referent':
      return 'Referent AI'
    case 'other':
      return 'Autre'
    default:
      return type
  }
}

function formatDateFr(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  try {
    return format(parseISO(dateStr), 'dd MMMM yyyy', { locale: fr })
  } catch {
    return dateStr
  }
}

function formatRelativeDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  try {
    return formatDistance(parseISO(dateStr), new Date(), { addSuffix: true, locale: fr })
  } catch {
    return dateStr
  }
}

const SKILL_LEVELS = [
  { value: 0, label: 'Non evalue', color: 'bg-gray-200' },
  { value: 1, label: 'Debutant', color: 'bg-red-300' },
  { value: 2, label: 'En acquisition', color: 'bg-orange-300' },
  { value: 3, label: 'Acquis', color: 'bg-yellow-300' },
  { value: 4, label: 'Maitrise', color: 'bg-green-400' },
]

// ---- Tab Components ----

function ProfilTab({ beneficiary }: { beneficiary: Beneficiary }) {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Personal Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Informations personnelles</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">
              {beneficiary.first_name} {beneficiary.last_name}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span>Ne(e) le {formatDateFr(beneficiary.date_of_birth)}</span>
          </div>
          {beneficiary.phone && (
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span>{beneficiary.phone}</span>
            </div>
          )}
          {beneficiary.email && (
            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <span>{beneficiary.email}</span>
            </div>
          )}
          {(beneficiary.address || beneficiary.city) && (
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <span>
                {[beneficiary.address, beneficiary.postal_code, beneficiary.city]
                  .filter(Boolean)
                  .join(', ')}
              </span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Langue:</span>
            <span>{beneficiary.language || 'Francais'}</span>
          </div>
        </CardContent>
      </Card>

      {/* Admin Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Informations administratives</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {beneficiary.ai_number && (
            <div>
              <span className="text-sm text-muted-foreground">Numero AI:</span>{' '}
              <span className="font-medium">{beneficiary.ai_number}</span>
            </div>
          )}
          <div>
            <span className="text-sm text-muted-foreground">Type de rente:</span>{' '}
            <span>{getPensionTypeLabel(beneficiary.pension_type)}</span>
          </div>
          {beneficiary.guardianship_status && (
            <div>
              <span className="text-sm text-muted-foreground">Curatelle:</span>{' '}
              <span>{beneficiary.guardianship_status}</span>
            </div>
          )}
          <div>
            <span className="text-sm text-muted-foreground">Date d'entree:</span>{' '}
            <span>{formatDateFr(beneficiary.entry_date)}</span>
          </div>
          {beneficiary.exit_date && (
            <div>
              <span className="text-sm text-muted-foreground">Date de sortie:</span>{' '}
              <span>{formatDateFr(beneficiary.exit_date)}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Contract Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Contrat</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {beneficiary.contract_type && (
            <div>
              <span className="text-sm text-muted-foreground">Type de contrat:</span>{' '}
              <span>{beneficiary.contract_type}</span>
            </div>
          )}
          <div>
            <span className="text-sm text-muted-foreground">Taux d'occupation:</span>{' '}
            <span>{beneficiary.occupation_rate ? `${beneficiary.occupation_rate}%` : '-'}</span>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">Unite:</span>{' '}
            <span>{beneficiary.unit_name || '-'}</span>
          </div>
          <div>
            <span className="text-sm text-muted-foreground">MSP referent:</span>{' '}
            <span>{beneficiary.referent_name || '-'}</span>
          </div>
        </CardContent>
      </Card>

      {/* PAI Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">PAI actuel</CardTitle>
        </CardHeader>
        <CardContent>
          {beneficiary.current_pai ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {getStatusBadge(beneficiary.current_pai.status)}
                <span className="text-sm text-muted-foreground">
                  Du {formatDateFr(beneficiary.current_pai.valid_from)}
                  {beneficiary.current_pai.valid_to && (
                    <> au {formatDateFr(beneficiary.current_pai.valid_to)}</>
                  )}
                </span>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link to={`/beneficiaries/${beneficiary.id}/pais/${beneficiary.current_pai.id}`}>
                  Voir le PAI
                </Link>
              </Button>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-muted-foreground mb-2">Aucun PAI actif</p>
              <Button variant="outline" size="sm" asChild>
                <Link to={`/beneficiaries/${beneficiary.id}/pais/new`}>
                  <Plus className="mr-2 h-4 w-4" />
                  Creer un PAI
                </Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats */}
      {beneficiary.stats && (
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Statistiques</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="text-center">
                <p className="text-2xl font-bold">{beneficiary.stats.objectives_total}</p>
                <p className="text-sm text-muted-foreground">Objectifs total</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {beneficiary.stats.objectives_achieved}
                </p>
                <p className="text-sm text-muted-foreground">Atteints</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {beneficiary.stats.objectives_in_progress}
                </p>
                <p className="text-sm text-muted-foreground">En cours</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">
                  {beneficiary.stats.objectives_overdue}
                </p>
                <p className="text-sm text-muted-foreground">En retard</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function MedicalTab({ beneficiaryId }: { beneficiaryId: number }) {
  const { user } = useAuthStore()
  const canView =
    user?.role === 'ADMIN' || user?.role === 'RES' || user?.role === 'RUA' || user?.role === 'MSP'

  const { data: medicalData, isLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'medical'],
    queryFn: () => beneficiariesApi.getMedicalData(beneficiaryId),
    enabled: canView,
  })

  if (!canView) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Lock className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium">Acces restreint</p>
          <p className="text-muted-foreground">
            Vous n'avez pas les droits pour consulter les donnees medicales.
          </p>
        </CardContent>
      </Card>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Chargement des donnees medicales...</span>
      </div>
    )
  }

  const data = medicalData || {}

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Lock className="h-4 w-4" />
        <span>Donnees medicales confidentielles - Acces restreint</span>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Medicaments</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{data.medication || 'Aucune information'}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Restrictions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{data.restrictions || 'Aucune restriction'}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Allergies</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{data.allergies || 'Aucune allergie connue'}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Notes medicales</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{data.medical_notes || 'Aucune note'}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function ContactsTab({ beneficiary }: { beneficiary: Beneficiary }) {
  const queryClient = useQueryClient()
  const beneficiaryId = beneficiary.id
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [editingContact, setEditingContact] = useState<Contact | null>(null)
  const [contactForm, setContactForm] = useState({
    contact_type: 'other' as Contact['contact_type'],
    name: '',
    organization: '',
    phone: '',
    email: '',
    address: '',
    notes: '',
    is_emergency_contact: false,
  })

  const { data: contacts, isLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'contacts'],
    queryFn: () => beneficiariesApi.getContacts(beneficiaryId),
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<Contact>) => beneficiariesApi.createContact(beneficiaryId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beneficiary', beneficiaryId, 'contacts'] })
      queryClient.invalidateQueries({ queryKey: ['beneficiary', beneficiaryId] })
      setShowAddDialog(false)
      resetForm()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ contactId, data }: { contactId: number; data: Partial<Contact> }) =>
      beneficiariesApi.updateContact(beneficiaryId, contactId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beneficiary', beneficiaryId, 'contacts'] })
      setEditingContact(null)
      resetForm()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (contactId: number) => beneficiariesApi.deleteContact(beneficiaryId, contactId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beneficiary', beneficiaryId, 'contacts'] })
    },
  })

  function resetForm() {
    setContactForm({
      contact_type: 'other',
      name: '',
      organization: '',
      phone: '',
      email: '',
      address: '',
      notes: '',
      is_emergency_contact: false,
    })
  }

  function openEdit(contact: Contact) {
    setEditingContact(contact)
    setContactForm({
      contact_type: contact.contact_type,
      name: contact.name,
      organization: contact.organization || '',
      phone: contact.phone || '',
      email: contact.email || '',
      address: contact.address || '',
      notes: contact.notes || '',
      is_emergency_contact: contact.is_emergency_contact,
    })
  }

  function handleSubmit() {
    const data = {
      ...contactForm,
      organization: contactForm.organization || null,
      phone: contactForm.phone || null,
      email: contactForm.email || null,
      address: contactForm.address || null,
      notes: contactForm.notes || null,
    }
    if (editingContact) {
      updateMutation.mutate({ contactId: editingContact.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const isFormOpen = showAddDialog || editingContact !== null

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  const contactList = contacts || beneficiary.contacts || []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Reseau / Contacts</h3>
        <Button
          size="sm"
          onClick={() => {
            resetForm()
            setShowAddDialog(true)
          }}
        >
          <Plus className="mr-2 h-4 w-4" />
          Ajouter un contact
        </Button>
      </div>

      {contactList.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <Users className="h-10 w-10 text-muted-foreground mb-2" />
            <p className="text-muted-foreground">Aucun contact enregistre</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {contactList.map((contact) => (
            <Card key={contact.id}>
              <CardContent className="flex items-center justify-between p-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium">{contact.name}</span>
                    <Badge variant="outline">{getContactTypeLabel(contact.contact_type)}</Badge>
                    {contact.is_emergency_contact && (
                      <Badge variant="destructive">Urgence</Badge>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground space-y-0.5">
                    {contact.organization && <div>{contact.organization}</div>}
                    {contact.phone && <div>{contact.phone}</div>}
                    {contact.email && <div>{contact.email}</div>}
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="icon" onClick={() => openEdit(contact)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      if (confirm('Supprimer ce contact ?')) {
                        deleteMutation.mutate(contact.id)
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Contact Form Dialog */}
      {isFormOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg bg-background p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {editingContact ? 'Modifier le contact' : 'Ajouter un contact'}
              </h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  setShowAddDialog(false)
                  setEditingContact(null)
                  resetForm()
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4">
              <div>
                <Label>Type de contact</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={contactForm.contact_type}
                  onChange={(e) =>
                    setContactForm({ ...contactForm, contact_type: e.target.value as Contact['contact_type'] })
                  }
                >
                  <option value="emergency">Urgence</option>
                  <option value="doctor">Medecin</option>
                  <option value="psychologist">Psychologue</option>
                  <option value="ai_referent">Referent AI</option>
                  <option value="other">Autre</option>
                </select>
              </div>
              <div>
                <Label>Nom *</Label>
                <Input
                  value={contactForm.name}
                  onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                />
              </div>
              <div>
                <Label>Organisation</Label>
                <Input
                  value={contactForm.organization}
                  onChange={(e) => setContactForm({ ...contactForm, organization: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Telephone</Label>
                  <Input
                    value={contactForm.phone}
                    onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Email</Label>
                  <Input
                    type="email"
                    value={contactForm.email}
                    onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <Label>Notes</Label>
                <textarea
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={contactForm.notes}
                  onChange={(e) => setContactForm({ ...contactForm, notes: e.target.value })}
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_emergency"
                  checked={contactForm.is_emergency_contact}
                  onChange={(e) =>
                    setContactForm({ ...contactForm, is_emergency_contact: e.target.checked })
                  }
                />
                <Label htmlFor="is_emergency">Contact d'urgence</Label>
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddDialog(false)
                    setEditingContact(null)
                    resetForm()
                  }}
                >
                  Annuler
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={!contactForm.name || createMutation.isPending || updateMutation.isPending}
                >
                  {(createMutation.isPending || updateMutation.isPending) && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  {editingContact ? 'Modifier' : 'Ajouter'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function RiskBehaviorsTab({ beneficiaryId }: { beneficiaryId: number }) {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ description: '', severity: 'low', notes: '' })

  // Risk behaviors are fetched from the beneficiary's medical/risk data endpoint
  const { data: risks, isLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'risks'],
    queryFn: async () => {
      const response = await beneficiariesApi.getMedicalData(beneficiaryId)
      return response?.risk_behaviors || []
    },
  })

  const severityBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return <Badge variant="destructive">Eleve</Badge>
      case 'medium':
        return <Badge variant="warning">Moyen</Badge>
      case 'low':
        return <Badge variant="outline">Faible</Badge>
      default:
        return <Badge>{severity}</Badge>
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  const riskList = risks || []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Comportements a risque</h3>
        <Button size="sm" onClick={() => setShowForm(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {riskList.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <AlertTriangle className="h-10 w-10 text-muted-foreground mb-2" />
            <p className="text-muted-foreground">Aucun comportement a risque signale</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {riskList.map((risk: { id: number; description: string; severity: string; notes?: string; reported_at?: string }) => (
            <Card key={risk.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{risk.description}</span>
                  {severityBadge(risk.severity)}
                </div>
                {risk.notes && (
                  <p className="text-sm text-muted-foreground">{risk.notes}</p>
                )}
                {risk.reported_at && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Signale {formatRelativeDate(risk.reported_at)}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Ajouter un comportement a risque</h3>
              <Button variant="ghost" size="icon" onClick={() => setShowForm(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4">
              <div>
                <Label>Description *</Label>
                <Input
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div>
                <Label>Severite</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                >
                  <option value="low">Faible</option>
                  <option value="medium">Moyen</option>
                  <option value="high">Eleve</option>
                </select>
              </div>
              <div>
                <Label>Notes</Label>
                <textarea
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowForm(false)}>
                  Annuler
                </Button>
                <Button disabled={!formData.description}>Enregistrer</Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ObjectivesTab({ beneficiaryId }: { beneficiaryId: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['objectives', { beneficiary_id: beneficiaryId }],
    queryFn: () => objectivesApi.list({ beneficiary_id: beneficiaryId, size: 50 }),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  const objectives = data?.items || []

  if (objectives.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-8">
          <Target className="h-10 w-10 text-muted-foreground mb-2" />
          <p className="text-muted-foreground">Aucun objectif defini</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {objectives.map((obj) => (
        <Link key={obj.id} to={`/objectives/${obj.id}`}>
          <Card className="transition-colors hover:bg-accent">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{obj.title}</span>
                  {getObjectiveTypeBadge(obj.objective_type)}
                  {getObjectiveStatusBadge(obj.status)}
                </div>
                {obj.due_date && (
                  <span className="text-sm text-muted-foreground">
                    Echeance: {formatDateFr(obj.due_date)}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4">
                <Progress value={obj.progress} className="flex-1 h-2" />
                <span className="text-sm font-medium">{obj.progress}%</span>
              </div>
              {obj.description && (
                <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                  {obj.description}
                </p>
              )}
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  )
}

function JournalTab({ beneficiaryId }: { beneficiaryId: number }) {
  const [categoryFilter, setCategoryFilter] = useState<string>('')

  const { data, isLoading } = useQuery({
    queryKey: ['journal', { beneficiary_id: beneficiaryId, category: categoryFilter }],
    queryFn: () =>
      journalApi.list({
        beneficiary_id: beneficiaryId,
        size: 10,
        category: categoryFilter || undefined,
      }),
  })

  const { data: categories } = useQuery({
    queryKey: ['journal-categories'],
    queryFn: () => journalApi.getCategories(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  const entries = data?.items || []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Label>Categorie:</Label>
          <select
            className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">Toutes</option>
            {categories?.map((cat) => (
              <option key={cat.id} value={cat.name}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
        <Button variant="outline" size="sm" asChild>
          <Link to={`/journal?beneficiary_id=${beneficiaryId}`}>Voir tout le journal</Link>
        </Button>
      </div>

      {entries.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <BookOpen className="h-10 w-10 text-muted-foreground mb-2" />
            <p className="text-muted-foreground">Aucune entree de journal</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {entries.map((entry) => (
            <Link key={entry.id} to={`/journal/${entry.id}`}>
              <Card className="transition-colors hover:bg-accent">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{entry.title}</span>
                    <span className="text-sm text-muted-foreground">
                      {formatDateFr(entry.entry_date)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    {entry.content.replace(/<[^>]*>/g, '').substring(0, 150)}
                  </p>
                  <div className="flex items-center gap-2 flex-wrap">
                    {entry.categories.map((cat) => (
                      <Badge key={cat.id} variant="outline" className="text-xs">
                        {cat.label}
                      </Badge>
                    ))}
                    {entry.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

function TimeAbsencesTab({ beneficiaryId }: { beneficiaryId: number }) {
  const { data: vacationData, isLoading: vacLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'vacation-balance'],
    queryFn: () => timeTrackingApi.getVacationBalance(beneficiaryId),
  })

  const { data: absenceStats, isLoading: statsLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'absence-stats'],
    queryFn: () => timeTrackingApi.getStats(beneficiaryId),
  })

  const { data: recentAbsences, isLoading: absLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'absences'],
    queryFn: () => timeTrackingApi.getAbsences(beneficiaryId),
  })

  const isLoading = vacLoading || statsLoading || absLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  const absenceTypeLabel = (type: string) => {
    switch (type) {
      case 'justified':
        return 'Justifiee'
      case 'unjustified':
        return 'Non justifiee'
      case 'medical':
        return 'Medicale'
      case 'vacation':
        return 'Vacances'
      default:
        return type
    }
  }

  const absenceTypeVariant = (type: string) => {
    switch (type) {
      case 'unjustified':
        return 'destructive' as const
      case 'medical':
        return 'warning' as const
      case 'vacation':
        return 'success' as const
      default:
        return 'outline' as const
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        {/* Vacation Balance */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Solde vacances</CardTitle>
          </CardHeader>
          <CardContent>
            {vacationData ? (
              <>
                <div className="text-2xl font-bold">
                  {vacationData.remaining_days} jours
                </div>
                <p className="text-xs text-muted-foreground">
                  {vacationData.taken_days} utilises sur {vacationData.entitled_days} total
                </p>
                <Progress
                  value={(vacationData.taken_days / Math.max(vacationData.entitled_days, 1)) * 100}
                  className="mt-2 h-2"
                />
              </>
            ) : (
              <p className="text-muted-foreground">Donnees non disponibles</p>
            )}
          </CardContent>
        </Card>

        {/* Absence Rate */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Taux d'absence</CardTitle>
          </CardHeader>
          <CardContent>
            {absenceStats ? (
              <>
                <div className="text-2xl font-bold">
                  {typeof absenceStats.absence_rate === 'number'
                    ? `${absenceStats.absence_rate.toFixed(1)}%`
                    : '-'}
                </div>
                <p className="text-xs text-muted-foreground">sur les 30 derniers jours</p>
              </>
            ) : (
              <p className="text-muted-foreground">Donnees non disponibles</p>
            )}
          </CardContent>
        </Card>

        {/* Total Absences */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Absences recentes</CardTitle>
          </CardHeader>
          <CardContent>
            {absenceStats ? (
              <>
                <div className="text-2xl font-bold">
                  {absenceStats.absences_this_month ?? 0}
                </div>
                <p className="text-xs text-muted-foreground">sur les 30 derniers jours</p>
              </>
            ) : (
              <p className="text-muted-foreground">Donnees non disponibles</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Absences Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Absences recentes</CardTitle>
        </CardHeader>
        <CardContent>
          {recentAbsences && Array.isArray(recentAbsences) && recentAbsences.length > 0 ? (
            <div className="space-y-2">
              {recentAbsences.slice(0, 10).map((absence) => (
                <div key={absence.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <span className="font-medium">{formatDateFr(absence.start_date)}</span>
                    {absence.reason && (
                      <p className="text-sm text-muted-foreground">{absence.reason}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={absenceTypeVariant(absence.absence_type)}>
                      {absenceTypeLabel(absence.absence_type)}
                    </Badge>
                    {absence.duration_days && (
                      <span className="text-sm text-muted-foreground">
                        {absence.duration_days}j
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-4">Aucune absence recente</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function SkillsTab({ beneficiaryId }: { beneficiaryId: number }) {
  const { data: skills, isLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'skills'],
    queryFn: () => skillsApi.getEvaluations(beneficiaryId),
  })

  const { data: allSkills } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsApi.listSkills(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  // Map string levels to numeric for display
  const levelToNumber: Record<string, number> = {
    not_acquired: 0,
    in_progress: 2,
    acquired: 3,
    mastered: 4,
  }

  // Group skills by category
  const skillsByCategory: Record<string, Array<{
    skill_name: string
    level: number
    evaluated_at: string | null
  }>> = {}

  if (skills && Array.isArray(skills)) {
    skills.forEach((s) => {
      const cat = s.skill_category || 'Autre'
      if (!skillsByCategory[cat]) skillsByCategory[cat] = []
      skillsByCategory[cat].push({
        skill_name: s.skill_name || '',
        level: levelToNumber[s.level] ?? 0,
        evaluated_at: s.evaluated_at || null,
      })
    })
  }

  const categoryNames = Object.keys(skillsByCategory)

  if (categoryNames.length === 0 && (!allSkills || allSkills.length === 0)) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-8">
          <Star className="h-10 w-10 text-muted-foreground mb-2" />
          <p className="text-muted-foreground">Aucune competence evaluee</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4 text-sm">
        <span className="text-muted-foreground">Legende:</span>
        {SKILL_LEVELS.map((level) => (
          <div key={level.value} className="flex items-center gap-1">
            <div className={`h-4 w-4 rounded ${level.color}`} />
            <span>{level.label}</span>
          </div>
        ))}
      </div>

      {categoryNames.map((category) => (
        <Card key={category}>
          <CardHeader>
            <CardTitle className="text-lg">{category}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              {skillsByCategory[category].map((skill) => (
                <div key={skill.skill_name} className="flex items-center gap-4">
                  <span className="w-48 text-sm font-medium">{skill.skill_name}</span>
                  <div className="flex gap-1">
                    {SKILL_LEVELS.map((level) => (
                      <div
                        key={level.value}
                        className={`h-8 w-8 rounded flex items-center justify-center text-xs font-medium ${
                          skill.level >= level.value && level.value > 0
                            ? level.color + ' text-white'
                            : 'bg-gray-100'
                        }`}
                        title={level.label}
                      >
                        {level.value}
                      </div>
                    ))}
                  </div>
                  {skill.evaluated_at && (
                    <span className="text-xs text-muted-foreground">
                      {formatRelativeDate(skill.evaluated_at)}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function DocumentsTab({ beneficiaryId }: { beneficiaryId: number }) {
  const queryClient = useQueryClient()
  const [uploading, setUploading] = useState(false)

  const { data: documents, isLoading } = useQuery({
    queryKey: ['beneficiary', beneficiaryId, 'documents'],
    queryFn: () => documentsApi.list({ beneficiary_id: beneficiaryId }),
  })

  const deleteMutation = useMutation({
    mutationFn: (docId: number) => documentsApi.delete(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beneficiary', beneficiaryId, 'documents'] })
    },
  })

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      await documentsApi.upload(file, {
        beneficiary_id: beneficiaryId,
        document_type: 'other',
      })
      queryClient.invalidateQueries({ queryKey: ['beneficiary', beneficiaryId, 'documents'] })
    } catch (err) {
      console.error('Erreur lors du telechargement:', err)
    } finally {
      setUploading(false)
    }
  }

  async function handleDownload(docId: number, filename: string) {
    try {
      const blob = await documentsApi.download(docId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Erreur lors du telechargement:', err)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  const docList = documents?.items || (Array.isArray(documents) ? documents : [])

  const formatFileSize = (size: number | null) => {
    if (!size) return '-'
    if (size < 1024) return `${size} o`
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} Ko`
    return `${(size / (1024 * 1024)).toFixed(1)} Mo`
  }

  const confidentialityBadge = (level: string) => {
    switch (level) {
      case 'highly_confidential':
        return <Badge variant="destructive">Hautement confidentiel</Badge>
      case 'confidential':
        return <Badge variant="warning">Confidentiel</Badge>
      default:
        return <Badge variant="outline">Standard</Badge>
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Documents</h3>
        <div>
          <input
            type="file"
            id="file-upload"
            className="hidden"
            onChange={handleUpload}
            disabled={uploading}
          />
          <Button size="sm" asChild>
            <label htmlFor="file-upload" className="cursor-pointer">
              {uploading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Upload className="mr-2 h-4 w-4" />
              )}
              {uploading ? 'Envoi en cours...' : 'Telecharger un document'}
            </label>
          </Button>
        </div>
      </div>

      {docList.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <FileText className="h-10 w-10 text-muted-foreground mb-2" />
            <p className="text-muted-foreground">Aucun document</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {docList.map((doc: { id: number; original_filename: string; document_type: string; file_size: number | null; confidentiality: string; uploaded_at: string }) => (
            <Card key={doc.id}>
              <CardContent className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{doc.original_filename}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{doc.document_type}</span>
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>{formatDateFr(doc.uploaded_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {confidentialityBadge(doc.confidentiality)}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDownload(doc.id, doc.original_filename)}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      if (confirm('Supprimer ce document ?')) {
                        deleteMutation.mutate(doc.id)
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

// ---- Main Page Component ----

const TABS = [
  { id: 'profil', label: 'Profil', icon: User },
  { id: 'medical', label: 'Donnees medicales', icon: Heart },
  { id: 'contacts', label: 'Reseau / Contacts', icon: Users },
  { id: 'risques', label: 'Comportements a risque', icon: AlertTriangle },
  { id: 'objectifs', label: 'Objectifs', icon: Target },
  { id: 'journal', label: 'Journal', icon: BookOpen },
  { id: 'temps', label: 'Temps & Absences', icon: Clock },
  { id: 'competences', label: 'Competences', icon: Star },
  { id: 'documents', label: 'Documents', icon: FileText },
]

export function BeneficiaryDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('profil')

  const beneficiaryId = Number(id)

  const {
    data: beneficiary,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['beneficiary', beneficiaryId],
    queryFn: () => beneficiariesApi.get(beneficiaryId),
    enabled: !!beneficiaryId && !isNaN(beneficiaryId),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-3 text-lg">Chargement du profil...</span>
      </div>
    )
  }

  if (error || !beneficiary) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <h2 className="text-xl font-bold mb-2">Beneficiaire introuvable</h2>
        <p className="text-muted-foreground mb-4">
          Le beneficiaire demande n'existe pas ou vous n'avez pas les droits d'acces.
        </p>
        <Button variant="outline" onClick={() => navigate('/beneficiaries')}>
          <ChevronLeft className="mr-2 h-4 w-4" />
          Retour a la liste
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/beneficiaries')}>
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <Avatar className="h-16 w-16">
          <AvatarFallback className="text-lg">
            {beneficiary.first_name[0]}
            {beneficiary.last_name[0]}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">
              {beneficiary.first_name} {beneficiary.last_name}
            </h1>
            {getStatusBadge(beneficiary.status)}
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
            {beneficiary.unit_name && <span>Unite: {beneficiary.unit_name}</span>}
            {beneficiary.referent_name && <span>MSP: {beneficiary.referent_name}</span>}
            {beneficiary.stats?.last_journal_entry && (
              <span>
                Dernier journal: {formatRelativeDate(beneficiary.stats.last_journal_entry)}
              </span>
            )}
          </div>
        </div>
        <Button asChild>
          <Link to={`/beneficiaries/${beneficiary.id}/edit`}>
            <Edit className="mr-2 h-4 w-4" />
            Modifier
          </Link>
        </Button>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-1 overflow-x-auto" role="tablist">
          {TABS.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                role="tab"
                aria-selected={activeTab === tab.id}
                className={`flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'profil' && <ProfilTab beneficiary={beneficiary} />}
        {activeTab === 'medical' && <MedicalTab beneficiaryId={beneficiaryId} />}
        {activeTab === 'contacts' && <ContactsTab beneficiary={beneficiary} />}
        {activeTab === 'risques' && <RiskBehaviorsTab beneficiaryId={beneficiaryId} />}
        {activeTab === 'objectifs' && <ObjectivesTab beneficiaryId={beneficiaryId} />}
        {activeTab === 'journal' && <JournalTab beneficiaryId={beneficiaryId} />}
        {activeTab === 'temps' && <TimeAbsencesTab beneficiaryId={beneficiaryId} />}
        {activeTab === 'competences' && <SkillsTab beneficiaryId={beneficiaryId} />}
        {activeTab === 'documents' && <DocumentsTab beneficiaryId={beneficiaryId} />}
      </div>
    </div>
  )
}
