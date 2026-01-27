# Spécifications API - CIS

## 1. Informations Générales

### 1.1 Base URL
```
Production:  https://cis.example.ch/api/v1
Development: http://localhost:8000/api/v1
```

### 1.2 Format
- **Content-Type**: `application/json`
- **Encoding**: UTF-8
- **Dates**: ISO 8601 (`2024-01-15T14:30:00Z`)

### 1.3 Authentification
```http
Authorization: Bearer <access_token>
```

### 1.4 Codes de réponse HTTP

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé avec succès |
| 204 | Succès sans contenu (DELETE) |
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Non autorisé |
| 404 | Ressource non trouvée |
| 422 | Erreur de validation |
| 500 | Erreur serveur |

### 1.5 Format des erreurs
```json
{
  "detail": "Description de l'erreur",
  "code": "ERROR_CODE",
  "errors": [
    {
      "field": "email",
      "message": "Format d'email invalide"
    }
  ]
}
```

### 1.6 Pagination
```http
GET /beneficiaries?page=1&size=20&sort=-created_at
```

**Réponse paginée:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

---

## 2. Authentification (`/auth`)

### 2.1 Login
```http
POST /auth/login
```

**Body:**
```json
{
  "email": "user@example.ch",
  "password": "password123"
}
```

**Réponse 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "email": "user@example.ch",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "MSP",
    "unit_id": 1,
    "unit_name": "Atelier Bois"
  }
}
```

*Note: Le refresh token est envoyé en cookie httpOnly*

### 2.2 Refresh Token
```http
POST /auth/refresh
```

*Cookie refresh_token requis*

**Réponse 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 2.3 Logout
```http
POST /auth/logout
```

**Réponse 200:**
```json
{
  "message": "Déconnexion réussie"
}
```

### 2.4 Mot de passe oublié
```http
POST /auth/forgot-password
```

**Body:**
```json
{
  "email": "user@example.ch"
}
```

### 2.5 Réinitialiser mot de passe
```http
POST /auth/reset-password
```

**Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newPassword123"
}
```

### 2.6 Changer mot de passe
```http
POST /auth/change-password
```

**Body:**
```json
{
  "current_password": "oldPassword",
  "new_password": "newPassword123"
}
```

---

## 3. Utilisateurs (`/users`)

### 3.1 Liste des utilisateurs
```http
GET /users?role=MSP&unit_id=1&is_active=true
```

**Permissions:** ADMIN, RUA

**Réponse 200:**
```json
{
  "items": [
    {
      "id": 1,
      "email": "jean.dupont@example.ch",
      "first_name": "Jean",
      "last_name": "Dupont",
      "role": "MSP",
      "unit_id": 1,
      "unit_name": "Atelier Bois",
      "is_active": true,
      "last_login": "2024-01-15T08:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "size": 20,
  "pages": 2
}
```

### 3.2 Détail utilisateur
```http
GET /users/{id}
```

### 3.3 Créer un utilisateur
```http
POST /users
```

**Permissions:** ADMIN

**Body:**
```json
{
  "email": "nouveau.user@example.ch",
  "password": "tempPassword123",
  "first_name": "Marie",
  "last_name": "Martin",
  "role": "MSP",
  "unit_id": 2
}
```

### 3.4 Modifier un utilisateur
```http
PUT /users/{id}
```

**Body:**
```json
{
  "first_name": "Marie",
  "last_name": "Martin-Dubois",
  "role": "RES",
  "unit_id": 2,
  "is_active": true
}
```

### 3.5 Utilisateur courant
```http
GET /users/me
```

---

## 4. Bénéficiaires (`/beneficiaries`)

### 4.1 Liste des bénéficiaires
```http
GET /beneficiaries?status=active&unit_id=1&referent_id=5&search=martin
```

**Paramètres de filtre:**
| Paramètre | Type | Description |
|-----------|------|-------------|
| status | string | active, paused, exited |
| unit_id | integer | ID de l'unité |
| referent_id | integer | ID du MSP référent |
| search | string | Recherche nom/prénom |
| page | integer | Page (défaut: 1) |
| size | integer | Taille page (défaut: 20, max: 100) |
| sort | string | Champ de tri (prefix `-` pour DESC) |

**Réponse 200:**
```json
{
  "items": [
    {
      "id": 1,
      "first_name": "Pierre",
      "last_name": "Martin",
      "date_of_birth": "1985-03-15",
      "photo_url": "/uploads/photos/1.jpg",
      "status": "active",
      "unit_id": 1,
      "unit_name": "Atelier Bois",
      "referent_id": 5,
      "referent_name": "Jean Dupont",
      "entry_date": "2023-06-01",
      "occupation_rate": 80.00,
      "objectives_in_progress": 3,
      "objectives_overdue": 1
    }
  ],
  "total": 45,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

### 4.2 Détail bénéficiaire
```http
GET /beneficiaries/{id}
```

**Réponse 200:**
```json
{
  "id": 1,
  "first_name": "Pierre",
  "last_name": "Martin",
  "date_of_birth": "1985-03-15",
  "photo_url": "/uploads/photos/1.jpg",
  "address": "Rue de la Gare 10",
  "postal_code": "1000",
  "city": "Lausanne",
  "phone": "+41 79 123 45 67",
  "email": "pierre.martin@email.ch",
  "language": "fr",

  "ai_number": "AI-12345",
  "pension_type": "half",
  "guardianship_status": null,
  "entry_date": "2023-06-01",
  "exit_date": null,
  "status": "active",

  "contract_type": "cdi",
  "occupation_rate": 80.00,
  "salary": 1500.00,
  "unit_id": 1,
  "unit_name": "Atelier Bois",
  "referent_id": 5,
  "referent_name": "Jean Dupont",

  "contacts": [
    {
      "id": 1,
      "contact_type": "emergency",
      "name": "Marie Martin",
      "phone": "+41 79 987 65 43",
      "is_emergency_contact": true
    }
  ],

  "current_pai": {
    "id": 3,
    "status": "active",
    "valid_from": "2024-01-01",
    "valid_to": "2024-12-31"
  },

  "stats": {
    "objectives_total": 8,
    "objectives_achieved": 4,
    "objectives_in_progress": 3,
    "objectives_overdue": 1,
    "absence_rate_30d": 5.5,
    "last_journal_entry": "2024-01-14"
  },

  "created_at": "2023-06-01T09:00:00Z",
  "updated_at": "2024-01-10T14:30:00Z"
}
```

### 4.3 Créer un bénéficiaire
```http
POST /beneficiaries
```

**Body:**
```json
{
  "first_name": "Pierre",
  "last_name": "Martin",
  "date_of_birth": "1985-03-15",
  "address": "Rue de la Gare 10",
  "postal_code": "1000",
  "city": "Lausanne",
  "phone": "+41 79 123 45 67",
  "email": "pierre.martin@email.ch",
  "language": "fr",
  "ai_number": "AI-12345",
  "pension_type": "half",
  "entry_date": "2023-06-01",
  "contract_type": "cdi",
  "occupation_rate": 80.00,
  "unit_id": 1,
  "referent_id": 5
}
```

### 4.4 Modifier un bénéficiaire
```http
PUT /beneficiaries/{id}
```

### 4.5 Données médicales (accès restreint)
```http
GET /beneficiaries/{id}/medical
```

**Permissions:** ADMIN, RUA, RES, MSP (référent uniquement)

**Réponse 200:**
```json
{
  "beneficiary_id": 1,
  "medication": "Lithium 400mg matin et soir",
  "restrictions": "Pas de travail en hauteur",
  "allergies": "Arachides",
  "medical_notes": "Suivi psychiatrique mensuel"
}
```

```http
PUT /beneficiaries/{id}/medical
```

### 4.6 Comportements à risque
```http
GET /beneficiaries/{id}/risk-behaviors
POST /beneficiaries/{id}/risk-behaviors
PUT /beneficiaries/{id}/risk-behaviors/{risk_id}
DELETE /beneficiaries/{id}/risk-behaviors/{risk_id}
```

### 4.7 Contacts réseau
```http
GET /beneficiaries/{id}/contacts
POST /beneficiaries/{id}/contacts
PUT /beneficiaries/{id}/contacts/{contact_id}
DELETE /beneficiaries/{id}/contacts/{contact_id}
```

---

## 5. Plans d'Accompagnement (`/pais`)

### 5.1 Liste PAI d'un bénéficiaire
```http
GET /beneficiaries/{beneficiary_id}/pais?status=active
```

### 5.2 Détail PAI
```http
GET /pais/{id}
```

**Réponse 200:**
```json
{
  "id": 3,
  "beneficiary_id": 1,
  "status": "active",
  "valid_from": "2024-01-01",
  "valid_to": "2024-12-31",

  "strengths": "Ponctuel, travailleur, bonne dextérité",
  "difficulties": "Gestion du stress, communication en groupe",
  "beneficiary_wishes": "Obtenir un CFC, travailler dans une menuiserie",

  "objectives": [
    {
      "id": 10,
      "title": "Améliorer la gestion du stress",
      "objective_type": "behavioral",
      "term": "medium",
      "status": "in_progress",
      "progress": 40,
      "due_date": "2024-06-30"
    }
  ],

  "created_at": "2024-01-05T10:00:00Z",
  "created_by": 5,
  "created_by_name": "Jean Dupont"
}
```

### 5.3 Créer un PAI
```http
POST /beneficiaries/{beneficiary_id}/pais
```

**Body:**
```json
{
  "valid_from": "2024-01-01",
  "valid_to": "2024-12-31",
  "strengths": "Ponctuel, travailleur, bonne dextérité",
  "difficulties": "Gestion du stress, communication en groupe",
  "beneficiary_wishes": "Obtenir un CFC, travailler dans une menuiserie"
}
```

### 5.4 Modifier un PAI
```http
PUT /pais/{id}
```

### 5.5 Activer/Clôturer un PAI
```http
POST /pais/{id}/activate
POST /pais/{id}/close
```

---

## 6. Objectifs (`/objectives`)

### 6.1 Liste des objectifs
```http
GET /objectives?beneficiary_id=1&status=in_progress&type=pai&overdue=true
```

**Paramètres:**
| Paramètre | Type | Description |
|-----------|------|-------------|
| beneficiary_id | integer | Filtrer par bénéficiaire |
| pai_id | integer | Filtrer par PAI |
| status | string | pending, in_progress, achieved, abandoned |
| type | string | pai, behavioral, operational |
| term | string | short, medium, long |
| overdue | boolean | Uniquement les objectifs en retard |

### 6.2 Vue globale objectifs (tous bénéficiaires)
```http
GET /objectives/overview?unit_id=1
```

**Réponse 200:**
```json
{
  "summary": {
    "total": 120,
    "pending": 30,
    "in_progress": 50,
    "achieved": 35,
    "abandoned": 5,
    "overdue": 12
  },
  "by_beneficiary": [
    {
      "beneficiary_id": 1,
      "beneficiary_name": "Pierre Martin",
      "unit_name": "Atelier Bois",
      "objectives": [
        {
          "id": 10,
          "title": "Améliorer gestion stress",
          "status": "in_progress",
          "progress": 40,
          "due_date": "2024-06-30",
          "is_overdue": false
        }
      ]
    }
  ]
}
```

### 6.3 Détail objectif
```http
GET /objectives/{id}
```

**Réponse 200:**
```json
{
  "id": 10,
  "pai_id": 3,
  "beneficiary_id": 1,
  "beneficiary_name": "Pierre Martin",

  "title": "Améliorer la gestion du stress",
  "description": "Développer des stratégies pour mieux gérer les situations stressantes au travail",
  "objective_type": "behavioral",
  "term": "medium",
  "priority": "high",
  "status": "in_progress",
  "progress": 40,
  "due_date": "2024-06-30",

  "reminder_frequency": "weekly",
  "last_reminder_sent": "2024-01-08T08:00:00Z",

  "indicators": [
    {
      "id": 1,
      "description": "Participer à 3 séances de relaxation",
      "is_achieved": true,
      "achieved_at": "2024-01-10T00:00:00Z"
    },
    {
      "id": 2,
      "description": "Utiliser les techniques apprises lors de 2 situations stressantes",
      "is_achieved": false
    }
  ],

  "actions": [
    {
      "id": 1,
      "description": "Inscription atelier gestion du stress",
      "responsible": "msp",
      "due_date": "2024-01-15",
      "status": "done"
    },
    {
      "id": 2,
      "description": "Pratique quotidienne exercices respiration",
      "responsible": "beneficiary",
      "due_date": null,
      "status": "pending"
    }
  ],

  "created_at": "2024-01-05T10:30:00Z",
  "created_by_name": "Jean Dupont"
}
```

### 6.4 Créer un objectif
```http
POST /objectives
```

**Body:**
```json
{
  "pai_id": 3,
  "beneficiary_id": 1,
  "title": "Améliorer la gestion du stress",
  "description": "Développer des stratégies pour mieux gérer les situations stressantes",
  "objective_type": "behavioral",
  "term": "medium",
  "priority": "high",
  "due_date": "2024-06-30",
  "reminder_frequency": "weekly",
  "indicators": [
    {"description": "Participer à 3 séances de relaxation"},
    {"description": "Utiliser les techniques lors de 2 situations"}
  ],
  "actions": [
    {
      "description": "Inscription atelier gestion du stress",
      "responsible": "msp",
      "due_date": "2024-01-15"
    }
  ]
}
```

### 6.5 Mettre à jour progression
```http
PATCH /objectives/{id}/progress
```

**Body:**
```json
{
  "progress": 60,
  "note": "2 indicateurs sur 3 atteints"
}
```

### 6.6 Changer statut
```http
PATCH /objectives/{id}/status
```

**Body:**
```json
{
  "status": "achieved",
  "note": "Objectif atteint avec succès"
}
```

### 6.7 Actions d'un objectif
```http
GET /objectives/{id}/actions
POST /objectives/{id}/actions
PUT /objectives/{id}/actions/{action_id}
DELETE /objectives/{id}/actions/{action_id}
```

### 6.8 Indicateurs d'un objectif
```http
POST /objectives/{id}/indicators/{indicator_id}/achieve
```

---

## 7. Journal de Bord (`/journal`)

### 7.1 Liste des entrées
```http
GET /journal?beneficiary_id=1&category=health,conflict&date_from=2024-01-01&search=stress
```

**Paramètres:**
| Paramètre | Type | Description |
|-----------|------|-------------|
| beneficiary_id | integer | Filtrer par bénéficiaire |
| author_id | integer | Filtrer par auteur |
| category | string | Catégories (séparées par virgule) |
| date_from | date | Date début |
| date_to | date | Date fin |
| search | string | Recherche plein texte |
| tags | string | Tags (séparés par virgule) |

**Réponse 200:**
```json
{
  "items": [
    {
      "id": 150,
      "beneficiary_id": 1,
      "beneficiary_name": "Pierre Martin",
      "author_id": 5,
      "author_name": "Jean Dupont",
      "title": "Entretien mensuel - janvier",
      "content": "Discussion sur les progrès réalisés...",
      "entry_date": "2024-01-15T14:00:00Z",
      "categories": [
        {"id": 7, "name": "interview", "label": "Entretien", "color": "#6366F1"}
      ],
      "tags": ["entretien-mensuel", "bilan"],
      "visibility": "unit",
      "attachments_count": 1
    }
  ],
  "total": 45,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

### 7.2 Détail entrée
```http
GET /journal/{id}
```

### 7.3 Créer une entrée
```http
POST /journal
```

**Body:**
```json
{
  "beneficiary_id": 1,
  "title": "Entretien mensuel - janvier",
  "content": "Discussion sur les progrès réalisés en matière de gestion du stress...",
  "entry_date": "2024-01-15T14:00:00Z",
  "category_ids": [7],
  "tags": ["entretien-mensuel", "bilan"],
  "visibility": "unit"
}
```

### 7.4 Modifier une entrée
```http
PUT /journal/{id}
```

### 7.5 Supprimer une entrée
```http
DELETE /journal/{id}
```

### 7.6 Catégories disponibles
```http
GET /journal/categories
```

### 7.7 Tags utilisés
```http
GET /journal/tags?beneficiary_id=1
```

### 7.8 Export historique
```http
GET /journal/export?beneficiary_id=1&format=pdf&date_from=2024-01-01
```

---

## 8. Gestion du Temps (`/time`)

### 8.1 Timbrages
```http
GET /beneficiaries/{id}/time-entries?month=2024-01
POST /beneficiaries/{id}/time-entries
PUT /beneficiaries/{id}/time-entries/{entry_id}
```

### 8.2 Absences
```http
GET /beneficiaries/{id}/absences?year=2024
POST /beneficiaries/{id}/absences
PUT /beneficiaries/{id}/absences/{absence_id}
DELETE /beneficiaries/{id}/absences/{absence_id}
```

**Body création absence:**
```json
{
  "absence_type": "sick",
  "start_date": "2024-01-10",
  "end_date": "2024-01-12",
  "notes": "Grippe"
}
```

### 8.3 Valider une absence
```http
POST /beneficiaries/{id}/absences/{absence_id}/validate
```

### 8.4 Solde vacances
```http
GET /beneficiaries/{id}/vacation-balance?year=2024
```

**Réponse 200:**
```json
{
  "year": 2024,
  "entitled_days": 25.0,
  "taken_days": 5.0,
  "remaining_days": 20.0,
  "pending_requests": 3.0
}
```

### 8.5 Statistiques absentéisme
```http
GET /beneficiaries/{id}/absence-stats?period=2024
```

**Réponse 200:**
```json
{
  "total_days": 15,
  "by_type": {
    "sick": 10,
    "vacation": 5,
    "accident": 0,
    "unauthorized": 0
  },
  "absence_rate": 6.5,
  "monthly_breakdown": [
    {"month": "2024-01", "days": 3},
    {"month": "2024-02", "days": 0}
  ]
}
```

---

## 9. Documents (`/documents`)

### 9.1 Liste documents
```http
GET /documents?beneficiary_id=1&type=medical_cert&confidentiality=standard
```

### 9.2 Upload document
```http
POST /documents
Content-Type: multipart/form-data
```

**Form data:**
- `file`: Fichier (max 10MB)
- `beneficiary_id`: integer
- `document_type`: string
- `document_date`: date
- `confidentiality`: string
- `description`: string

### 9.3 Télécharger document
```http
GET /documents/{id}/download
```

### 9.4 Supprimer document
```http
DELETE /documents/{id}
```

### 9.5 Métadonnées document
```http
GET /documents/{id}
PUT /documents/{id}
```

---

## 10. Compétences et Formations (`/skills`)

### 10.1 Référentiel compétences
```http
GET /skills
```

### 10.2 Matrice compétences bénéficiaire
```http
GET /beneficiaries/{id}/skills
PUT /beneficiaries/{id}/skills/{skill_id}
```

**Body évaluation:**
```json
{
  "level": "acquired",
  "comments": "Maîtrise les techniques de base"
}
```

### 10.3 Formations
```http
GET /beneficiaries/{id}/trainings
POST /beneficiaries/{id}/trainings
PUT /beneficiaries/{id}/trainings/{training_id}
```

---

## 11. Dashboard (`/dashboard`)

### 11.1 Dashboard MSP
```http
GET /dashboard/msp
```

**Réponse 200:**
```json
{
  "my_beneficiaries": [
    {
      "id": 1,
      "name": "Pierre Martin",
      "photo_url": "/uploads/photos/1.jpg",
      "status": "active",
      "objectives_overdue": 1,
      "last_journal_entry": "2024-01-14"
    }
  ],
  "today_reminders": [
    {
      "type": "objective_due",
      "beneficiary_id": 1,
      "beneficiary_name": "Pierre Martin",
      "objective_id": 10,
      "objective_title": "Améliorer gestion stress",
      "due_date": "2024-01-15"
    }
  ],
  "recent_journal_entries": [...],
  "pending_tasks": [...]
}
```

### 11.2 Dashboard Direction
```http
GET /dashboard/management?unit_id=1
```

**Réponse 200:**
```json
{
  "summary": {
    "total_beneficiaries": 45,
    "active_beneficiaries": 42,
    "new_this_month": 2,
    "exited_this_month": 1
  },
  "objectives_overview": {
    "total": 150,
    "achieved_this_month": 12,
    "overdue": 8,
    "achievement_rate": 75.5
  },
  "absence_stats": {
    "global_rate": 5.2,
    "by_unit": [
      {"unit_id": 1, "unit_name": "Atelier Bois", "rate": 4.5},
      {"unit_id": 2, "unit_name": "Atelier Métal", "rate": 6.1}
    ]
  },
  "alerts": [
    {
      "type": "high_absence",
      "beneficiary_id": 5,
      "beneficiary_name": "Jean Durand",
      "message": "Taux absentéisme > 20%"
    }
  ]
}
```

---

## 12. Rapports (`/reports`)

### 12.1 Synthèse individuelle
```http
GET /reports/beneficiary/{id}/summary?format=pdf
```

### 12.2 Rapport d'activité
```http
GET /reports/activity?period=2024-01&unit_id=1&format=excel
```

### 12.3 Rapport objectifs
```http
GET /reports/objectives?period=2024&status=all&format=pdf
```

### 12.4 Extraction comportements à risque
```http
GET /reports/risk-behaviors?unit_id=1&severity=high&format=excel
```

---

## 13. Notifications (`/notifications`)

### 13.1 Liste notifications
```http
GET /notifications?unread_only=true
```

### 13.2 Marquer comme lu
```http
POST /notifications/{id}/read
POST /notifications/read-all
```

### 13.3 Préférences notifications
```http
GET /users/me/notification-preferences
PUT /users/me/notification-preferences
```

---

## 14. Administration (`/admin`)

### 14.1 Unités
```http
GET /admin/units
POST /admin/units
PUT /admin/units/{id}
```

### 14.2 Catégories journal
```http
GET /admin/journal-categories
POST /admin/journal-categories
PUT /admin/journal-categories/{id}
```

### 14.3 Référentiel compétences
```http
POST /admin/skills
PUT /admin/skills/{id}
DELETE /admin/skills/{id}
```

### 14.4 Audit logs
```http
GET /admin/audit-logs?user_id=1&action=update&resource_type=beneficiary&date_from=2024-01-01
```

---

## 15. Export ICS (Calendrier)

### 15.1 Export objectifs
```http
GET /calendar/objectives.ics?beneficiary_id=1
```

Retourne un fichier ICS compatible Outlook/Google Calendar avec les échéances d'objectifs.

---

## 16. Webhooks (optionnel)

### 16.1 Configuration
```http
GET /webhooks
POST /webhooks
DELETE /webhooks/{id}
```

### 16.2 Événements disponibles
- `beneficiary.created`
- `beneficiary.updated`
- `objective.created`
- `objective.status_changed`
- `objective.overdue`
- `journal.created`

---

## 17. Health Checks

### 17.1 Statut global
```http
GET /health
```

**Réponse 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

### 17.2 Statut détaillé
```http
GET /health/detailed
```

**Réponse 200:**
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "up", "latency_ms": 5},
    "redis": {"status": "up", "latency_ms": 1},
    "storage": {"status": "up"}
  }
}
```
