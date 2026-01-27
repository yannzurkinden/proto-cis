# Modèle de Données - CIS

## 1. Diagramme Entité-Relation (Simplifié)

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│    User     │       │   Beneficiary   │       │    Unit     │
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ id          │       │ id              │       │ id          │
│ email       │──────▶│ referent_id (FK)│◀──────│ name        │
│ role        │       │ unit_id (FK)    │───────│ description │
│ unit_id(FK) │───────│ first_name      │       └─────────────┘
└─────────────┘       │ last_name       │
                      │ status          │
                      └────────┬────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│      PAI        │  │  JournalEntry   │  │    Document     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ id              │  │ id              │  │ id              │
│ beneficiary_id  │  │ beneficiary_id  │  │ beneficiary_id  │
│ status          │  │ author_id       │  │ uploaded_by     │
│ valid_from      │  │ category        │  │ file_path       │
│ valid_to        │  │ content         │  │ doc_type        │
└────────┬────────┘  │ created_at      │  └─────────────────┘
         │           └─────────────────┘
         ▼
┌─────────────────┐
│   Objective     │
├─────────────────┤       ┌─────────────────┐
│ id              │       │     Action      │
│ pai_id          │       ├─────────────────┤
│ title           │◀──────│ id              │
│ type            │       │ objective_id    │
│ status          │       │ description     │
│ progress        │       │ due_date        │
│ due_date        │       │ status          │
└─────────────────┘       └─────────────────┘
```

---

## 2. Tables Détaillées

### 2.1 Gestion des Utilisateurs

#### Table `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'MSP',
    unit_id INTEGER REFERENCES units(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_role CHECK (role IN ('ADMIN', 'RUA', 'RES', 'MSP', 'CONSULT'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_unit ON users(unit_id);
```

#### Table `units` (Unités/Ateliers)
```sql
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2.2 Gestion des Bénéficiaires

#### Table `beneficiaries`
```sql
CREATE TABLE beneficiaries (
    id SERIAL PRIMARY KEY,

    -- Données personnelles
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    photo_url VARCHAR(500),
    address TEXT,
    postal_code VARCHAR(10),
    city VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    language VARCHAR(10) DEFAULT 'fr',

    -- Données administratives
    ai_number VARCHAR(50),
    pension_type VARCHAR(20),
    guardianship_status VARCHAR(50),
    guardian_contact_id INTEGER REFERENCES contacts(id),
    entry_date DATE NOT NULL,
    exit_date DATE,
    status VARCHAR(20) DEFAULT 'active',

    -- Données contractuelles
    contract_type VARCHAR(50),
    occupation_rate DECIMAL(5,2),
    salary DECIMAL(10,2),
    unit_id INTEGER REFERENCES units(id),
    referent_id INTEGER REFERENCES users(id),

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),

    CONSTRAINT valid_status CHECK (status IN ('active', 'paused', 'exited')),
    CONSTRAINT valid_pension CHECK (pension_type IN ('quarter', 'half', 'three_quarter', 'full'))
);

CREATE INDEX idx_beneficiaries_status ON beneficiaries(status);
CREATE INDEX idx_beneficiaries_unit ON beneficiaries(unit_id);
CREATE INDEX idx_beneficiaries_referent ON beneficiaries(referent_id);
CREATE INDEX idx_beneficiaries_name ON beneficiaries(last_name, first_name);
-- Index pour recherche full-text
CREATE INDEX idx_beneficiaries_search ON beneficiaries
    USING GIN (to_tsvector('french', first_name || ' ' || last_name));
```

#### Table `beneficiary_medical_data` (données sensibles séparées)
```sql
CREATE TABLE beneficiary_medical_data (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL UNIQUE REFERENCES beneficiaries(id) ON DELETE CASCADE,

    -- Données médicales (chiffrées en application)
    medication TEXT,  -- Chiffré AES
    restrictions TEXT,  -- Chiffré AES
    allergies TEXT,  -- Chiffré AES
    medical_notes TEXT,  -- Chiffré AES

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);
```

#### Table `contacts` (Réseau)
```sql
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER REFERENCES beneficiaries(id) ON DELETE CASCADE,

    contact_type VARCHAR(50) NOT NULL,  -- emergency, doctor, psychologist, ai_referent, other
    name VARCHAR(200) NOT NULL,
    organization VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    notes TEXT,
    is_emergency_contact BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contacts_beneficiary ON contacts(beneficiary_id);
CREATE INDEX idx_contacts_type ON contacts(contact_type);
```

#### Table `risk_behaviors` (Comportements à risque)
```sql
CREATE TABLE risk_behaviors (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,

    risk_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- low, medium, high, critical
    preventive_measures TEXT,
    reported_date DATE NOT NULL,
    reported_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_behaviors_beneficiary ON risk_behaviors(beneficiary_id);
CREATE INDEX idx_risk_behaviors_severity ON risk_behaviors(severity);
CREATE INDEX idx_risk_behaviors_active ON risk_behaviors(is_active);
```

---

### 2.3 Plans d'Accompagnement et Objectifs

#### Table `pais` (Plans d'Accompagnement Individualisés)
```sql
CREATE TABLE pais (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,

    status VARCHAR(20) DEFAULT 'draft',  -- draft, active, closed
    valid_from DATE NOT NULL,
    valid_to DATE,

    -- Bilan initial
    strengths TEXT,
    difficulties TEXT,
    beneficiary_wishes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),

    CONSTRAINT valid_pai_status CHECK (status IN ('draft', 'active', 'closed'))
);

CREATE INDEX idx_pais_beneficiary ON pais(beneficiary_id);
CREATE INDEX idx_pais_status ON pais(status);
```

#### Table `objectives`
```sql
CREATE TABLE objectives (
    id SERIAL PRIMARY KEY,
    pai_id INTEGER REFERENCES pais(id) ON DELETE CASCADE,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,

    title VARCHAR(255) NOT NULL,
    description TEXT,
    objective_type VARCHAR(30) NOT NULL,  -- pai, behavioral, operational
    term VARCHAR(20) NOT NULL,  -- short, medium, long
    priority VARCHAR(10) DEFAULT 'medium',  -- high, medium, low
    status VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, achieved, abandoned
    progress INTEGER DEFAULT 0,  -- 0-100
    due_date DATE,

    -- Rappels
    reminder_frequency VARCHAR(20),  -- daily, weekly, monthly, none
    last_reminder_sent TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),

    CONSTRAINT valid_objective_type CHECK (objective_type IN ('pai', 'behavioral', 'operational')),
    CONSTRAINT valid_term CHECK (term IN ('short', 'medium', 'long')),
    CONSTRAINT valid_priority CHECK (priority IN ('high', 'medium', 'low')),
    CONSTRAINT valid_objective_status CHECK (status IN ('pending', 'in_progress', 'achieved', 'abandoned')),
    CONSTRAINT valid_progress CHECK (progress >= 0 AND progress <= 100)
);

CREATE INDEX idx_objectives_pai ON objectives(pai_id);
CREATE INDEX idx_objectives_beneficiary ON objectives(beneficiary_id);
CREATE INDEX idx_objectives_status ON objectives(status);
CREATE INDEX idx_objectives_due_date ON objectives(due_date);
```

#### Table `objective_indicators` (Indicateurs de réussite)
```sql
CREATE TABLE objective_indicators (
    id SERIAL PRIMARY KEY,
    objective_id INTEGER NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,

    description VARCHAR(255) NOT NULL,
    is_achieved BOOLEAN DEFAULT FALSE,
    achieved_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_indicators_objective ON objective_indicators(objective_id);
```

#### Table `actions` (Tâches/Actions pour atteindre un objectif)
```sql
CREATE TABLE actions (
    id SERIAL PRIMARY KEY,
    objective_id INTEGER NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,

    description TEXT NOT NULL,
    responsible VARCHAR(50),  -- beneficiary, msp, other
    responsible_name VARCHAR(100),  -- Si other
    due_date DATE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, done
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_action_status CHECK (status IN ('pending', 'done'))
);

CREATE INDEX idx_actions_objective ON actions(objective_id);
CREATE INDEX idx_actions_status ON actions(status);
```

---

### 2.4 Journal de Bord

#### Table `journal_categories` (Types d'entrées)
```sql
CREATE TABLE journal_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    label VARCHAR(100) NOT NULL,
    color VARCHAR(7),  -- Code couleur hex
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
);

-- Données initiales
INSERT INTO journal_categories (name, label, color, icon, sort_order) VALUES
('health', 'Santé', '#10B981', 'heart', 1),
('behavior', 'Comportement', '#F59E0B', 'alert-triangle', 2),
('conflict', 'Conflit', '#EF4444', 'zap', 3),
('skills', 'Compétences / Formation', '#3B82F6', 'book', 4),
('private', 'Vie privée', '#8B5CF6', 'user', 5),
('inter_unit', 'Échange inter-unités', '#06B6D4', 'users', 6),
('interview', 'Entretien', '#6366F1', 'message-circle', 7),
('incident', 'Incident', '#DC2626', 'alert-circle', 8),
('progress', 'Progrès / Réussite', '#22C55E', 'trending-up', 9),
('other', 'Autre', '#6B7280', 'file-text', 10);
```

#### Table `journal_entries`
```sql
CREATE TABLE journal_entries (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id),

    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visibility VARCHAR(20) DEFAULT 'unit',  -- team, unit, inter_unit

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_visibility CHECK (visibility IN ('team', 'unit', 'inter_unit'))
);

CREATE INDEX idx_journal_beneficiary ON journal_entries(beneficiary_id);
CREATE INDEX idx_journal_author ON journal_entries(author_id);
CREATE INDEX idx_journal_date ON journal_entries(entry_date DESC);
-- Index full-text pour recherche
CREATE INDEX idx_journal_search ON journal_entries
    USING GIN (to_tsvector('french', title || ' ' || content));
```

#### Table `journal_entry_categories` (Association many-to-many)
```sql
CREATE TABLE journal_entry_categories (
    journal_entry_id INTEGER NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES journal_categories(id),
    PRIMARY KEY (journal_entry_id, category_id)
);

CREATE INDEX idx_jec_category ON journal_entry_categories(category_id);
```

#### Table `journal_entry_tags`
```sql
CREATE TABLE journal_entry_tags (
    id SERIAL PRIMARY KEY,
    journal_entry_id INTEGER NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,

    UNIQUE(journal_entry_id, tag)
);

CREATE INDEX idx_jet_tag ON journal_entry_tags(tag);
```

---

### 2.5 Gestion du Temps

#### Table `time_entries` (Timbrages)
```sql
CREATE TABLE time_entries (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,

    entry_date DATE NOT NULL,
    time_in TIME,
    time_out TIME,
    entry_type VARCHAR(20) DEFAULT 'work',  -- work, training, appointment
    hours_worked DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN time_in IS NOT NULL AND time_out IS NOT NULL
        THEN EXTRACT(EPOCH FROM (time_out - time_in))/3600
        ELSE NULL END
    ) STORED,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(beneficiary_id, entry_date)
);

CREATE INDEX idx_time_entries_beneficiary ON time_entries(beneficiary_id);
CREATE INDEX idx_time_entries_date ON time_entries(entry_date);
```

#### Table `absences`
```sql
CREATE TABLE absences (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,

    absence_type VARCHAR(30) NOT NULL,  -- sick, vacation, accident, unauthorized, other
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    justification_document_id INTEGER REFERENCES documents(id),
    validated_by INTEGER REFERENCES users(id),
    validated_at TIMESTAMP,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_absence_type CHECK (absence_type IN ('sick', 'vacation', 'accident', 'unauthorized', 'other')),
    CONSTRAINT valid_date_range CHECK (end_date >= start_date)
);

CREATE INDEX idx_absences_beneficiary ON absences(beneficiary_id);
CREATE INDEX idx_absences_dates ON absences(start_date, end_date);
CREATE INDEX idx_absences_type ON absences(absence_type);
```

#### Table `vacation_balances` (Soldes vacances)
```sql
CREATE TABLE vacation_balances (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,

    year INTEGER NOT NULL,
    entitled_days DECIMAL(5,2) NOT NULL,  -- Jours acquis
    taken_days DECIMAL(5,2) DEFAULT 0,  -- Jours pris
    remaining_days DECIMAL(5,2) GENERATED ALWAYS AS (entitled_days - taken_days) STORED,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(beneficiary_id, year)
);

CREATE INDEX idx_vacation_beneficiary_year ON vacation_balances(beneficiary_id, year);
```

---

### 2.6 Compétences et Formations

#### Table `skills` (Référentiel compétences)
```sql
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
);
```

#### Table `beneficiary_skills` (Matrice compétences)
```sql
CREATE TABLE beneficiary_skills (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id),

    level VARCHAR(20) NOT NULL,  -- not_acquired, in_progress, acquired, mastered
    evaluation_date DATE NOT NULL,
    evaluated_by INTEGER REFERENCES users(id),
    comments TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(beneficiary_id, skill_id),
    CONSTRAINT valid_skill_level CHECK (level IN ('not_acquired', 'in_progress', 'acquired', 'mastered'))
);

CREATE INDEX idx_bskills_beneficiary ON beneficiary_skills(beneficiary_id);
```

#### Table `trainings` (Formations)
```sql
CREATE TABLE trainings (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,

    title VARCHAR(255) NOT NULL,
    training_date DATE NOT NULL,
    duration_hours DECIMAL(5,2),
    trainer VARCHAR(200),
    certificate_document_id INTEGER REFERENCES documents(id),
    comments TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trainings_beneficiary ON trainings(beneficiary_id);
```

---

### 2.7 Gestion Documentaire

#### Table `documents`
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    beneficiary_id INTEGER REFERENCES beneficiaries(id) ON DELETE CASCADE,

    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,  -- UUID ou hash
    file_path VARCHAR(500) NOT NULL,  -- Chemin MinIO
    file_size INTEGER,
    mime_type VARCHAR(100),

    document_type VARCHAR(50) NOT NULL,  -- contract, medical_cert, evaluation, report, correspondence, other
    document_date DATE,
    confidentiality VARCHAR(20) DEFAULT 'standard',  -- standard, confidential, highly_confidential
    description TEXT,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id),

    -- Versioning
    version INTEGER DEFAULT 1,
    previous_version_id INTEGER REFERENCES documents(id),
    is_current BOOLEAN DEFAULT TRUE,

    CONSTRAINT valid_confidentiality CHECK (confidentiality IN ('standard', 'confidential', 'highly_confidential'))
);

CREATE INDEX idx_documents_beneficiary ON documents(beneficiary_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_uploaded ON documents(uploaded_at DESC);
```

---

### 2.8 Audit et Logs

#### Table `audit_logs`
```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,

    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,  -- create, read, update, delete, login, logout, export
    resource_type VARCHAR(50) NOT NULL,  -- beneficiary, objective, journal, document, etc.
    resource_id INTEGER,

    old_values JSONB,  -- Valeurs avant modification
    new_values JSONB,  -- Valeurs après modification

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_date ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_action ON audit_logs(action);
```

#### Table `notifications`
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    link VARCHAR(500),  -- URL relative vers la ressource

    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_date ON notifications(created_at DESC);
```

---

## 3. Vues Utiles

### 3.1 Vue Dashboard Bénéficiaires
```sql
CREATE VIEW v_beneficiary_dashboard AS
SELECT
    b.id,
    b.first_name,
    b.last_name,
    b.status,
    b.photo_url,
    u.name as unit_name,
    CONCAT(ref.first_name, ' ', ref.last_name) as referent_name,

    -- Objectifs en cours
    (SELECT COUNT(*) FROM objectives o WHERE o.beneficiary_id = b.id AND o.status = 'in_progress') as objectives_in_progress,

    -- Objectifs en retard
    (SELECT COUNT(*) FROM objectives o WHERE o.beneficiary_id = b.id AND o.status IN ('pending', 'in_progress') AND o.due_date < CURRENT_DATE) as objectives_overdue,

    -- Dernière entrée journal
    (SELECT entry_date FROM journal_entries j WHERE j.beneficiary_id = b.id ORDER BY entry_date DESC LIMIT 1) as last_journal_entry,

    -- Taux absentéisme (30 derniers jours)
    (SELECT COALESCE(SUM(end_date - start_date + 1), 0) FROM absences a WHERE a.beneficiary_id = b.id AND a.start_date >= CURRENT_DATE - 30) as absence_days_30d

FROM beneficiaries b
LEFT JOIN units u ON b.unit_id = u.id
LEFT JOIN users ref ON b.referent_id = ref.id
WHERE b.status = 'active';
```

### 3.2 Vue Statistiques Objectifs
```sql
CREATE VIEW v_objectives_stats AS
SELECT
    b.id as beneficiary_id,
    b.first_name,
    b.last_name,
    u.name as unit_name,
    COUNT(*) FILTER (WHERE o.status = 'pending') as pending_count,
    COUNT(*) FILTER (WHERE o.status = 'in_progress') as in_progress_count,
    COUNT(*) FILTER (WHERE o.status = 'achieved') as achieved_count,
    COUNT(*) FILTER (WHERE o.status = 'abandoned') as abandoned_count,
    COUNT(*) FILTER (WHERE o.due_date < CURRENT_DATE AND o.status IN ('pending', 'in_progress')) as overdue_count,
    AVG(o.progress) FILTER (WHERE o.status IN ('pending', 'in_progress')) as avg_progress
FROM beneficiaries b
LEFT JOIN objectives o ON o.beneficiary_id = b.id
LEFT JOIN units u ON b.unit_id = u.id
WHERE b.status = 'active'
GROUP BY b.id, b.first_name, b.last_name, u.name;
```

---

## 4. Migrations Alembic

### Structure des migrations
```
alembic/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_journal_fulltext.py
│   ├── 003_add_audit_logs.py
│   └── ...
├── env.py
└── script.py.mako
```

### Exemple de migration
```python
"""Initial schema

Revision ID: 001
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        # ... autres colonnes
    )

    # Indexes
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_table('users')
```

### Commandes Alembic
```bash
# Créer une migration
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Voir l'historique
alembic history
```

---

## 5. Considérations Performances

### 5.1 Index recommandés
- Tous les champs de filtrage fréquent (status, unit_id, referent_id)
- Colonnes de dates pour les requêtes temporelles
- Index GIN pour recherche full-text (PostgreSQL)
- Index composites pour les requêtes multi-critères

### 5.2 Partitionnement (si volume important)
```sql
-- Partitionnement de audit_logs par mois
CREATE TABLE audit_logs (
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 5.3 Archivage
- Politique de rétention des logs (ex: 2 ans)
- Archivage des PAI clôturés après X années
- Suppression/anonymisation conformément LPD
