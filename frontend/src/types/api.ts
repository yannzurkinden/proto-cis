// Common API types

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'ADMIN' | 'RUA' | 'RES' | 'MSP' | 'CONSULT'
  unit_id: number | null
  unit_name: string | null
  is_active: boolean
  last_login: string | null
  created_at: string
}

export interface Unit {
  id: number
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Beneficiary {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  photo_url: string | null
  address: string | null
  postal_code: string | null
  city: string | null
  phone: string | null
  email: string | null
  language: string
  ai_number: string | null
  pension_type: 'quarter' | 'half' | 'three_quarter' | 'full' | null
  guardianship_status: string | null
  entry_date: string
  exit_date: string | null
  status: 'active' | 'paused' | 'exited'
  contract_type: string | null
  occupation_rate: number | null
  salary: number | null
  unit_id: number | null
  unit_name: string | null
  referent_id: number | null
  referent_name: string | null
  current_pai: {
    id: number
    status: string
    valid_from: string
    valid_to: string | null
  } | null
  stats: {
    objectives_total: number
    objectives_achieved: number
    objectives_in_progress: number
    objectives_overdue: number
    absence_rate_30d: number
    last_journal_entry: string | null
  } | null
  contacts: Contact[]
  created_at: string
  updated_at: string
}

export interface BeneficiaryListItem {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  photo_url: string | null
  status: string
  unit_id: number | null
  unit_name: string | null
  referent_id: number | null
  referent_name: string | null
  entry_date: string
  occupation_rate: number | null
  objectives_in_progress: number
  objectives_overdue: number
}

export interface Contact {
  id: number
  contact_type: 'emergency' | 'doctor' | 'psychologist' | 'ai_referent' | 'other'
  name: string
  organization: string | null
  phone: string | null
  email: string | null
  address: string | null
  notes: string | null
  is_emergency_contact: boolean
}

export interface PAI {
  id: number
  beneficiary_id: number
  status: 'draft' | 'active' | 'closed'
  valid_from: string
  valid_to: string | null
  strengths: string | null
  difficulties: string | null
  beneficiary_wishes: string | null
  objectives: ObjectiveSummary[]
  created_at: string
  created_by: number | null
  created_by_name: string | null
}

export interface ObjectiveSummary {
  id: number
  title: string
  objective_type: string
  term: string
  status: string
  progress: number
  due_date: string | null
}

export interface Objective {
  id: number
  pai_id: number | null
  beneficiary_id: number
  beneficiary_name: string | null
  title: string
  description: string | null
  objective_type: 'pai' | 'behavioral' | 'operational'
  term: 'short' | 'medium' | 'long'
  priority: 'high' | 'medium' | 'low'
  status: 'pending' | 'in_progress' | 'achieved' | 'abandoned'
  progress: number
  due_date: string | null
  reminder_frequency: string | null
  last_reminder_sent: string | null
  indicators: Indicator[]
  actions: Action[]
  created_at: string
  created_by_name: string | null
}

export interface Indicator {
  id: number
  description: string
  is_achieved: boolean
  achieved_at: string | null
}

export interface Action {
  id: number
  description: string
  responsible: 'beneficiary' | 'msp' | 'other' | null
  responsible_name: string | null
  due_date: string | null
  status: 'pending' | 'done'
  notes: string | null
}

export interface JournalEntry {
  id: number
  beneficiary_id: number
  beneficiary_name: string | null
  author_id: number
  author_name: string | null
  title: string
  content: string
  entry_date: string
  visibility: 'team' | 'unit' | 'inter_unit'
  categories: JournalCategory[]
  tags: string[]
  attachments_count: number
  created_at: string
  updated_at: string
}

export interface JournalCategory {
  id: number
  name: string
  label: string
  color: string | null
  icon: string | null
}

export interface Document {
  id: number
  beneficiary_id: number | null
  original_filename: string
  file_size: number | null
  mime_type: string | null
  document_type: string
  document_date: string | null
  confidentiality: 'standard' | 'confidential' | 'highly_confidential'
  description: string | null
  version: number
  is_current: boolean
  uploaded_at: string
  uploaded_by: number | null
}

// Auth types
export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}
