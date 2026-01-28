# 08 - Plan d'implémentation détaillé

> Dernière mise à jour : 2026-01-28
> Contexte : Développement avec Claude Code, déploiement Docker sur Infomaniak

---

## Table des matières

1. [État des lieux](#1-état-des-lieux)
2. [Phase 1 — Fondations](#2-phase-1--fondations)
3. [Phase 2 — Backend : compléments](#3-phase-2--backend-compléments)
4. [Phase 3 — Frontend : composants partagés](#4-phase-3--frontend-composants-partagés)
5. [Phase 4 — Frontend : pages principales](#5-phase-4--frontend-pages-principales)
6. [Phase 5 — Frontend : pages secondaires](#6-phase-5--frontend-pages-secondaires)
7. [Phase 6 — Sécurité et conformité](#7-phase-6--sécurité-et-conformité)
8. [Phase 7 — Tests](#8-phase-7--tests)
9. [Phase 8 — Déploiement Infomaniak](#9-phase-8--déploiement-infomaniak)
10. [Annexes](#10-annexes)

---

## 1. État des lieux

### Ce qui est fait

| Couche | Avancement | Détail |
|--------|-----------|--------|
| **Modèles SQLAlchemy** | 100% | 11 fichiers, toutes les entités (beneficiary, PAI, objectives, journal, time_tracking, skills, documents, audit) |
| **Schemas Pydantic** | 95% | Toutes les entités CRUD |
| **Repositories** | 90% | 8 repositories avec filtres, pagination, stats |
| **API Endpoints** | 85% | Auth, users, units, beneficiaries, PAIs, objectives, journal, documents, dashboard |
| **Sécurité backend** | 90% | JWT, RBAC, bcrypt, AES-256, dependencies d'auth |
| **Docker / Nginx** | 95% | Compose, Dockerfiles, reverse proxy, rate limiting, health checks |
| **Frontend - Layout** | 100% | MainLayout, Sidebar, Header |
| **Frontend - Pages** | 25% | LoginPage, DashboardPage, BeneficiaryListPage |
| **Frontend - Composants UI** | 30% | button, input, label, card, badge, avatar, progress (shadcn/ui) |
| **Frontend - API client** | 70% | client.ts, auth, beneficiaries, objectives, journal, dashboard |
| **Frontend - Stores** | 30% | authStore, uiStore |
| **Documentation** | 100% | 8 documents de spécification |
| **Tests** | 5% | Quelques tests auth basiques |

### Ce qui manque (résumé)

- **0 migration Alembic** (bloquant)
- **0 données de seed**
- **12 TODO dans le backend** (calculs stats, email, MinIO)
- **~30 pages frontend** non implémentées (routes placeholder `<div>`)
- **Endpoints manquants** : risk behaviors, skills, time tracking, admin, reports, notifications
- **Composants frontend** : DataTable, formulaires, modales, rich text, upload
- **Intégrations** : MinIO (storage fichiers), SMTP (emails), PDF (rapports)
- **Tests** : ~5% couverture

---

## 2. Phase 1 — Fondations

> Pré-requis pour pouvoir développer et tester toutes les fonctionnalités.

### 1.1 Migrations Alembic

```
Fichier : backend/alembic/versions/
```

- [ ] Générer la migration initiale depuis les modèles existants
  ```bash
  cd backend && alembic revision --autogenerate -m "Initial schema"
  ```
- [ ] Vérifier le fichier généré (tables, contraintes, index)
- [ ] Tester `alembic upgrade head` sur une base vierge
- [ ] Vérifier que toutes les 24+ tables sont créées correctement
- [ ] Vérifier les index GIN pour la recherche full-text (si définis dans les modèles)

### 1.2 Script de seed

```
Fichier : backend/scripts/seed.py
```

- [ ] Créer un script Python de seed avec :
  - 3 unités (Atelier Bois, Atelier Cuisine, Atelier Bureautique)
  - 1 ADMIN, 2 RUA, 2 RES, 4 MSP, 1 CONSULT (répartis sur les unités)
  - 10-15 bénéficiaires avec données réalistes (statuts variés : active, suspended, exited)
  - 3-4 PAI avec objectifs (différents statuts et types)
  - 20-30 entrées journal avec catégories variées
  - Quelques absences et entrées de temps
  - Compétences de référence (10-15 skills)
  - Quelques documents (métadonnées, sans fichiers physiques)
- [ ] Rendre le script idempotent (vérifier existence avant création)
- [ ] Documenter les identifiants de test (admin@cis.ch / password123, etc.)

### 1.3 Vérification Docker Compose

- [ ] S'assurer que `docker-compose up` démarre tous les services
- [ ] Vérifier que le backend applique les migrations au démarrage
- [ ] Vérifier la connexion frontend → backend via Nginx
- [ ] Tester le health check : `GET /health`

---

## 3. Phase 2 — Backend : compléments

### 2.1 Résoudre les TODO existants

```
Fichiers concernés :
  - backend/app/api/v1/dashboard.py (lignes 58, 154, 155, 159, 164)
  - backend/app/api/v1/beneficiaries.py (lignes 85, 86, 162)
  - backend/app/api/v1/journal.py (lignes 87, 94)
  - backend/app/api/v1/auth.py (lignes 201, 213)
```

#### Dashboard TODO :

- [ ] `last_journal_entry` (L58) : Requête `journal_entries` triée par `entry_date DESC` pour chaque bénéficiaire
- [ ] `new_this_month` (L154) : `COUNT beneficiaries WHERE entry_date >= premier jour du mois courant`
- [ ] `exited_this_month` (L155) : `COUNT beneficiaries WHERE exit_date >= premier jour du mois courant`
- [ ] `achieved_this_month` (L159) : `COUNT objectives WHERE status = 'achieved' AND updated_at >= premier jour du mois`
- [ ] `global_rate` (L164) : `SUM(heures absence) / SUM(heures attendues) * 100` par unité et global

#### Beneficiaries TODO :

- [ ] `objectives_in_progress` (L85) : `COUNT objectives WHERE beneficiary_id = X AND status = 'in_progress'`
- [ ] `objectives_overdue` (L86) : `COUNT objectives WHERE beneficiary_id = X AND status IN ('pending','in_progress') AND due_date < today`
- [ ] `BeneficiaryStats` (L162) : Agréger les stats (total objectifs, taux réussite, absences, dernière note journal)

#### Journal TODO :

- [ ] `author_name` (L87) : Joindre `users` table via `author_id` et retourner `full_name`
- [ ] `attachments_count` (L94) : `COUNT documents WHERE journal_entry_id = X` (si relation existe) ou champ dédié

#### Auth TODO :

- [ ] `send_password_reset_email` (L201) : Implémenter envoi SMTP (voir Phase 2.4)
- [ ] `token_verification` (L213) : Vérifier le token de reset stocké en DB avec expiration

### 2.2 Endpoints manquants — Risk Behaviors

```
Fichier à créer : backend/app/api/v1/risk_behaviors.py
```

Les modèles existent déjà (`RiskBehavior` dans `beneficiary.py`).

- [ ] `GET /beneficiaries/{id}/risk-behaviors` — Lister les comportements à risque
- [ ] `POST /beneficiaries/{id}/risk-behaviors` — Ajouter un comportement
- [ ] `PUT /beneficiaries/{id}/risk-behaviors/{risk_id}` — Modifier
- [ ] `DELETE /beneficiaries/{id}/risk-behaviors/{risk_id}` — Supprimer
- [ ] Schema Pydantic : `RiskBehaviorCreate`, `RiskBehaviorUpdate`, `RiskBehaviorResponse`
- [ ] Repository : `RiskBehaviorRepository` avec filtres par sévérité, statut actif
- [ ] Enregistrer le router dans `router.py`

### 2.3 Endpoints manquants — Skills & Trainings

```
Fichier à créer : backend/app/api/v1/skills.py
```

Les modèles existent (`Skill`, `BeneficiarySkill`, `Training` dans `skill.py`).

- [ ] `GET /skills` — Liste du référentiel de compétences
- [ ] `POST /skills` — Créer une compétence (ADMIN/RUA)
- [ ] `PUT /skills/{id}` — Modifier
- [ ] `DELETE /skills/{id}` — Supprimer
- [ ] `GET /beneficiaries/{id}/skills` — Matrice de compétences du bénéficiaire
- [ ] `PUT /beneficiaries/{id}/skills/{skill_id}` — Évaluer une compétence (level: not_acquired/in_progress/acquired/mastered)
- [ ] `GET /beneficiaries/{id}/trainings` — Liste des formations
- [ ] `POST /beneficiaries/{id}/trainings` — Ajouter une formation
- [ ] `PUT /beneficiaries/{id}/trainings/{training_id}` — Modifier
- [ ] `DELETE /beneficiaries/{id}/trainings/{training_id}` — Supprimer
- [ ] Schemas : `SkillCreate/Update/Response`, `BeneficiarySkillEvaluate/Response`, `TrainingCreate/Update/Response`
- [ ] Repository : `SkillRepository`

### 2.4 Endpoints manquants — Time Tracking

```
Fichier à créer : backend/app/api/v1/time_tracking.py
```

Les modèles existent (`TimeEntry`, `Absence`, `VacationBalance` dans `time_tracking.py`).

- [ ] `GET /beneficiaries/{id}/time-entries` — Liste des pointages (filtrable par date)
- [ ] `POST /beneficiaries/{id}/time-entries` — Ajouter un pointage
- [ ] `PUT /beneficiaries/{id}/time-entries/{entry_id}` — Modifier
- [ ] `DELETE /beneficiaries/{id}/time-entries/{entry_id}` — Supprimer
- [ ] `GET /beneficiaries/{id}/absences` — Liste des absences (filtrable par type, statut)
- [ ] `POST /beneficiaries/{id}/absences` — Déclarer une absence
- [ ] `PUT /beneficiaries/{id}/absences/{absence_id}` — Modifier
- [ ] `DELETE /beneficiaries/{id}/absences/{absence_id}` — Supprimer
- [ ] `POST /beneficiaries/{id}/absences/{absence_id}/validate` — Valider (RES/RUA)
- [ ] `GET /beneficiaries/{id}/vacation-balance` — Solde vacances
- [ ] `GET /beneficiaries/{id}/absence-stats` — Statistiques d'absences (taux, jours par type)
- [ ] Schemas : `TimeEntryCreate/Update/Response`, `AbsenceCreate/Update/Response`, `VacationBalanceResponse`, `AbsenceStatsResponse`
- [ ] Repository : `TimeTrackingRepository`

### 2.5 Endpoints manquants — Admin

```
Fichier à créer : backend/app/api/v1/admin.py
```

- [ ] `GET /admin/journal-categories` — Liste des catégories journal
- [ ] `POST /admin/journal-categories` — Créer catégorie
- [ ] `PUT /admin/journal-categories/{id}` — Modifier
- [ ] `GET /admin/audit-logs` — Consulter les logs d'audit (filtrable par action, user, date)
- [ ] Restriction : ADMIN uniquement (sauf categories accessible aux RUA)

### 2.6 Endpoints manquants — Notifications

```
Fichier à créer : backend/app/api/v1/notifications.py
```

Le modèle existe (`Notification` dans `audit.py`).

- [ ] `GET /notifications` — Liste des notifications de l'utilisateur courant
- [ ] `POST /notifications/{id}/read` — Marquer comme lue
- [ ] `POST /notifications/read-all` — Marquer toutes comme lues
- [ ] `GET /notifications/unread-count` — Nombre de non-lues (pour le badge header)
- [ ] Repository : `NotificationRepository`

### 2.7 Endpoints manquants — Reports

```
Fichier à créer : backend/app/api/v1/reports.py
```

- [ ] `GET /reports/beneficiary/{id}/summary` — Résumé PDF individuel
  - Générer PDF avec WeasyPrint ou ReportLab
  - Inclure : infos perso, objectifs, journal récent, compétences, absences
  - Retourner `StreamingResponse` avec `Content-Type: application/pdf`
- [ ] `GET /reports/activity` — Rapport d'activité mensuel (JSON ou PDF)
- [ ] `GET /reports/objectives` — Export objectifs (Excel via openpyxl)
- [ ] `GET /reports/absenteeism` — Stats d'absentéisme (JSON ou Excel)
- [ ] Dépendances à ajouter : `weasyprint` ou `reportlab`, `openpyxl`

### 2.8 Intégration MinIO (stockage fichiers)

```
Fichiers concernés :
  - backend/app/services/storage.py (à créer)
  - backend/app/api/v1/documents.py (à modifier)
  - docker-compose.yml (service MinIO déjà configuré)
```

- [ ] Créer `StorageService` avec interface :
  - `upload_file(bucket, filename, content, content_type) -> str` (retourne URL)
  - `download_file(bucket, filename) -> bytes`
  - `delete_file(bucket, filename) -> bool`
  - `get_presigned_url(bucket, filename, expiry) -> str`
- [ ] Utiliser `minio` Python SDK
- [ ] Modifier `upload_document` (documents.py L92-131) : envoyer le fichier à MinIO au lieu de juste lire le contenu
- [ ] Modifier `download_document` (documents.py L134-163) : streamer depuis MinIO au lieu de retourner 501
- [ ] Modifier `delete_document` (documents.py L189-206) : supprimer aussi de MinIO
- [ ] Créer le bucket `cis-documents` au démarrage si inexistant
- [ ] Configurer les variables d'environnement MinIO dans `.env`

### 2.9 Service Email (SMTP)

```
Fichier à créer : backend/app/services/email.py
```

- [ ] Créer `EmailService` avec :
  - `send_password_reset(email, token, reset_url)`
  - `send_notification(email, subject, body)`
  - `send_report(email, subject, body, attachment_bytes, filename)`
- [ ] Utiliser `aiosmtplib` pour envoi async
- [ ] Templates HTML pour les emails (Jinja2)
- [ ] Configuration SMTP via variables d'env (compatible Infomaniak SMTP)
- [ ] Intégrer dans `auth.py` pour le reset password

### 2.10 Service de génération PDF

```
Fichier à créer : backend/app/services/pdf.py
```

- [ ] Créer `PDFService` avec :
  - `generate_beneficiary_summary(beneficiary_data) -> bytes`
  - `generate_activity_report(data, date_range) -> bytes`
- [ ] Templates HTML → PDF (WeasyPrint) ou construction directe (ReportLab)
- [ ] En-tête avec logo CIS, pied de page avec date et pagination
- [ ] Intégrer dans `reports.py`

---

## 4. Phase 3 — Frontend : composants partagés

> Construire les briques réutilisables avant les pages.

### 3.1 Installer les composants shadcn/ui manquants

```bash
npx shadcn@latest add dialog select checkbox textarea tabs accordion
npx shadcn@latest add dropdown-menu separator toast calendar popover command
npx shadcn@latest add table skeleton alert-dialog tooltip sheet
```

- [ ] Installer chaque composant
- [ ] Vérifier que les imports fonctionnent

### 3.2 DataTable générique

```
Fichier : frontend/src/components/shared/DataTable.tsx
```

- [ ] Basé sur `@tanstack/react-table`
- [ ] Props : `columns`, `data`, `pagination`, `sorting`, `filtering`, `onRowClick`
- [ ] Fonctionnalités :
  - Tri par colonne (asc/desc)
  - Pagination (page, taille, total)
  - Recherche globale (texte)
  - Filtres par colonne (select, date range)
  - Sélection de lignes (checkbox)
  - Skeleton loading
  - Empty state
- [ ] Responsive : scroll horizontal sur mobile

### 3.3 Formulaires réutilisables

```
Fichier : frontend/src/components/shared/FormField.tsx
Fichier : frontend/src/components/shared/FormSelect.tsx
Fichier : frontend/src/components/shared/FormDatePicker.tsx
Fichier : frontend/src/components/shared/FormTextarea.tsx
Fichier : frontend/src/components/shared/FormMultiSelect.tsx
```

- [ ] `FormField` : Wrapper React Hook Form + label + erreur + hint
- [ ] `FormSelect` : Select avec options typées
- [ ] `FormDatePicker` : Calendar popover avec date-fns
- [ ] `FormTextarea` : Textarea avec compteur de caractères
- [ ] `FormMultiSelect` : Multi-sélection avec tags
- [ ] Tous les composants intègrent la validation Zod via `useFormContext`

### 3.4 Modale de confirmation

```
Fichier : frontend/src/components/shared/ConfirmDialog.tsx
```

- [ ] Props : `open`, `onConfirm`, `onCancel`, `title`, `description`, `variant` (default/destructive)
- [ ] Variante destructive (rouge) pour les suppressions
- [ ] Bouton de chargement pendant l'action

### 3.5 Composant StatusBadge

```
Fichier : frontend/src/components/shared/StatusBadge.tsx
```

- [ ] Mapping des statuts vers couleurs :
  - `active` → vert, `suspended` → orange, `exited` → gris
  - `pending` → jaune, `in_progress` → bleu, `achieved` → vert, `abandoned` → rouge
  - `draft` → gris, `active` → vert, `closed` → bleu
- [ ] Icône optionnelle
- [ ] Tooltip avec détail

### 3.6 Composant FileUpload

```
Fichier : frontend/src/components/shared/FileUpload.tsx
```

- [ ] Drag & drop zone
- [ ] Clic pour sélectionner
- [ ] Preview (images, nom fichier pour autres)
- [ ] Barre de progression upload
- [ ] Validation : taille max (10MB), types acceptés
- [ ] Multiple files (optionnel)

### 3.7 Rich Text Editor (Journal)

```
Fichier : frontend/src/components/shared/RichTextEditor.tsx
```

- [ ] Basé sur TipTap ou React Quill
- [ ] Toolbar : gras, italique, listes, liens
- [ ] Output : HTML stocké en DB
- [ ] Sanitization côté affichage (DOMPurify)

### 3.8 Composant EmptyState

```
Fichier : frontend/src/components/shared/EmptyState.tsx
```

- [ ] Props : `icon`, `title`, `description`, `action` (bouton optionnel)
- [ ] Utilisé quand une liste est vide

### 3.9 Composant PageHeader

```
Fichier : frontend/src/components/shared/PageHeader.tsx
```

- [ ] Props : `title`, `description`, `actions` (boutons à droite)
- [ ] Breadcrumb optionnel
- [ ] Pattern réutilisé sur toutes les pages

### 3.10 Hooks partagés

```
Fichier : frontend/src/hooks/useDebounce.ts
Fichier : frontend/src/hooks/usePagination.ts
Fichier : frontend/src/hooks/useQueryParams.ts
```

- [ ] `useDebounce(value, delay)` : Pour la recherche
- [ ] `usePagination(initialPage, initialSize)` : État pagination
- [ ] `useQueryParams()` : Synchroniser filtres avec l'URL

### 3.11 API clients manquants

```
Fichiers à créer :
  - frontend/src/api/timeTracking.ts
  - frontend/src/api/skills.ts
  - frontend/src/api/documents.ts
  - frontend/src/api/reports.ts
  - frontend/src/api/notifications.ts
  - frontend/src/api/admin.ts
```

- [ ] Chaque client suit le même pattern qu'`auth.ts` / `beneficiaries.ts`
- [ ] Types TypeScript pour chaque entité (request/response)
- [ ] Utiliser l'instance Axios de `client.ts`

### 3.12 Stores Zustand manquants

```
Fichiers à créer :
  - frontend/src/stores/notificationStore.ts
  - frontend/src/stores/filterStore.ts
```

- [ ] `notificationStore` : `unreadCount`, `notifications[]`, `markAsRead()`, `fetchNotifications()`
- [ ] `filterStore` : Filtres globaux persistés (par page)

---

## 5. Phase 4 — Frontend : pages principales

> Les pages les plus utilisées au quotidien.

### 4.1 Page — Fiche bénéficiaire (détail)

```
Fichier : frontend/src/pages/beneficiaries/BeneficiaryDetailPage.tsx
Route : /beneficiaries/:id
```

Structure en onglets (Tabs) :

#### Onglet "Profil"
- [ ] Infos personnelles : nom, prénom, date de naissance, adresse, téléphone, email, langue
- [ ] Photo (avatar)
- [ ] Infos administratives : numéro AI, type de rente, mesure de protection, statut
- [ ] Infos contractuelles : type contrat, taux occupation, salaire, unité, MSP référent
- [ ] Bouton "Modifier" → ouvre formulaire d'édition
- [ ] Bouton "Changer de statut" (active/suspended/exited)

#### Onglet "Données médicales" (accès restreint)
- [ ] Vérifier le rôle avant affichage (MSP référent, RES, RUA, ADMIN)
- [ ] Médicaments, restrictions, allergies, notes médicales
- [ ] Icône de cadenas (données chiffrées)
- [ ] Formulaire d'édition in-place

#### Onglet "Réseau / Contacts"
- [ ] Liste des contacts (urgence, médecin, psy, référent AI, autres)
- [ ] Tableau : nom, rôle, téléphone, email
- [ ] Boutons : Ajouter, Modifier, Supprimer (avec confirmation)
- [ ] Formulaire modale pour ajout/édition

#### Onglet "Comportements à risque"
- [ ] Liste : type, description, sévérité (low/medium/high/critical), mesures préventives
- [ ] Badge de sévérité coloré
- [ ] Ajout/Édition/Suppression via modale

#### Onglet "Objectifs" (résumé)
- [ ] Liste des objectifs du bénéficiaire (PAI courant)
- [ ] Progress bar pour chaque objectif
- [ ] StatusBadge (pending/in_progress/achieved/abandoned)
- [ ] Lien vers la page détail objectif
- [ ] Bouton "Ajouter un objectif"

#### Onglet "Journal" (résumé)
- [ ] 10 dernières entrées du journal pour ce bénéficiaire
- [ ] Filtre par catégorie
- [ ] Lien vers la page journal complète

#### Onglet "Temps & Absences" (résumé)
- [ ] Solde vacances (jours pris / jours restants)
- [ ] Taux d'absentéisme
- [ ] Dernières absences
- [ ] Lien vers la page temps complète

#### Onglet "Compétences"
- [ ] Grille/matrice : compétence × niveau (not_acquired → mastered)
- [ ] Indicateur visuel (icône ou couleur)
- [ ] Date de dernière évaluation
- [ ] Bouton "Évaluer" → modale avec select de niveau

#### Onglet "Documents"
- [ ] Liste des documents liés
- [ ] Filtre par type, confidentialité
- [ ] Preview (images, PDF)
- [ ] Upload nouveau document
- [ ] Téléchargement

### 4.2 Page — Création/Édition bénéficiaire

```
Fichier : frontend/src/pages/beneficiaries/BeneficiaryFormPage.tsx
Route : /beneficiaries/new et /beneficiaries/:id/edit
```

- [ ] Formulaire multi-sections (accordéon ou stepper) :
  1. Informations personnelles (nom*, prénom*, DDN*, adresse, tel, email, langue)
  2. Informations administratives (numéro AI*, type rente, protection, date entrée*)
  3. Informations contractuelles (type contrat, taux occupation, unité*, MSP référent*)
- [ ] Validation Zod complète
- [ ] Mode création vs édition (pré-remplissage)
- [ ] Boutons : Sauvegarder, Annuler
- [ ] Redirection vers la fiche après sauvegarde

### 4.3 Page — PAI (Plan d'Accompagnement Individualisé)

```
Fichier : frontend/src/pages/pais/PAIDetailPage.tsx
Fichier : frontend/src/pages/pais/PAIFormPage.tsx
Route : /beneficiaries/:id/pais/:paiId
```

#### Détail PAI :
- [ ] En-tête : titre, statut (draft/active/closed), dates, bénéficiaire
- [ ] Bilan initial : forces, difficultés, souhaits
- [ ] Liste des objectifs groupés par type (PAI, comportemental, opérationnel)
- [ ] Pour chaque objectif :
  - Titre, description, terme (court/moyen/long)
  - Priorité (haute/moyenne/basse)
  - Progress bar + pourcentage
  - Indicateurs de réussite (checklist)
  - Actions/sous-tâches avec responsable et statut
  - Date d'échéance
- [ ] Boutons : Activer le PAI, Clôturer le PAI, Modifier
- [ ] Historique des révisions

#### Formulaire PAI :
- [ ] Bilan initial (textareas)
- [ ] Section objectifs (ajout dynamique)
- [ ] Pour chaque objectif : formulaire imbriqué avec indicateurs et actions

### 4.4 Page — Liste des objectifs

```
Fichier : frontend/src/pages/objectives/ObjectiveListPage.tsx
Route : /objectives
```

- [ ] DataTable avec colonnes : bénéficiaire, titre, type, terme, priorité, statut, progression, échéance
- [ ] Filtres :
  - Statut (pending, in_progress, achieved, abandoned)
  - Type (pai, behavioral, operational)
  - Terme (short, medium, long)
  - En retard (oui/non)
  - Bénéficiaire (select)
- [ ] Tri par colonne
- [ ] Code couleur : vert (OK), orange (attention), rouge (en retard)
- [ ] Export Excel (bouton)
- [ ] Clic sur ligne → détail objectif

### 4.5 Page — Détail objectif

```
Fichier : frontend/src/pages/objectives/ObjectiveDetailPage.tsx
Route : /objectives/:id
```

- [ ] Infos : titre, description, bénéficiaire, type, terme, priorité
- [ ] Progress bar éditable (slider)
- [ ] Changement de statut (dropdown)
- [ ] Indicateurs de réussite :
  - Checklist interactive (cocher = atteint)
  - Métrique avec valeur cible vs actuelle
- [ ] Actions/sous-tâches :
  - Liste avec responsable, statut, échéance
  - Ajouter/modifier/supprimer
- [ ] Rappels et notifications liés
- [ ] Historique des modifications

### 4.6 Page — Journal de bord

```
Fichier : frontend/src/pages/journal/JournalListPage.tsx
Fichier : frontend/src/pages/journal/JournalEntryPage.tsx
Fichier : frontend/src/pages/journal/JournalFormPage.tsx
Route : /journal, /journal/:id, /journal/new
```

#### Liste :
- [ ] Timeline ou liste de cartes
- [ ] Filtres : catégorie, bénéficiaire, date (range), tags, recherche plein texte
- [ ] Catégories avec icônes et couleurs (santé=rouge, comportement=orange, compétences=bleu, etc.)
- [ ] Bénéficiaire associé (avatar + nom)
- [ ] Date et auteur
- [ ] Bouton "Nouvelle entrée"
- [ ] Export (PDF, Excel)

#### Détail :
- [ ] Titre, contenu (rich text), date, auteur
- [ ] Catégories (badges)
- [ ] Tags
- [ ] Pièces jointes (documents liés)
- [ ] Niveau de visibilité (team, unit, inter-unit)
- [ ] Boutons : Modifier, Supprimer (avec confirmation)

#### Formulaire :
- [ ] Titre, Rich Text Editor pour le contenu
- [ ] Sélection bénéficiaire (searchable select)
- [ ] Multi-sélection catégories
- [ ] Tags (input avec suggestions)
- [ ] Visibilité (radio : équipe, unité, inter-unités)
- [ ] Upload pièces jointes
- [ ] Validation : titre et contenu requis, au moins une catégorie

---

## 6. Phase 5 — Frontend : pages secondaires

### 5.1 Page — Gestion du temps

```
Fichier : frontend/src/pages/time/TimeTrackingPage.tsx
Route : /beneficiaries/:id/time (accessible depuis fiche bénéficiaire)
```

- [ ] Onglet "Pointages" :
  - Tableau : date, heure arrivée, heure départ, type (travail, formation, RDV), durée calculée
  - Ajout rapide
  - Résumé hebdo/mensuel (total heures)
- [ ] Onglet "Absences" :
  - Tableau : date début, date fin, type (maladie, vacances, accident, injustifiée), justifiée (oui/non), statut validation
  - Ajouter absence avec justificatif (upload)
  - Bouton "Valider" pour RES/RUA
- [ ] Onglet "Solde vacances" :
  - Jours acquis, pris, restants
  - Historique annuel
- [ ] Stats en cartes : taux absentéisme, heures ce mois, absences ce mois

### 5.2 Page — Compétences & Formations

```
Fichier : frontend/src/pages/skills/SkillsPage.tsx
Route : /beneficiaries/:id/skills (accessible depuis fiche bénéficiaire)
```

- [ ] Onglet "Matrice de compétences" :
  - Grille : nom compétence × niveau (4 niveaux)
  - Indicateur visuel (couleur ou icône par niveau)
  - Date dernière évaluation
  - Bouton "Évaluer" sur chaque ligne
- [ ] Onglet "Formations" :
  - Tableau : titre, date, durée, formateur, certificat (oui/non)
  - Ajout/Édition/Suppression
  - Upload certificat

### 5.3 Page — Documents (GED)

```
Fichier : frontend/src/pages/documents/DocumentListPage.tsx
Route : /documents
```

- [ ] DataTable : nom fichier, type, bénéficiaire, date document, date upload, auteur, confidentialité, taille
- [ ] Filtres : type document, bénéficiaire, confidentialité, date range
- [ ] Recherche par nom fichier
- [ ] Preview : clic → affiche image ou PDF dans modale
- [ ] Upload : bouton + drag&drop zone
- [ ] Téléchargement : bouton download
- [ ] Suppression avec confirmation
- [ ] Icônes par type de fichier (PDF, image, Word, etc.)

### 5.4 Page — Administration

```
Fichier : frontend/src/pages/admin/AdminPage.tsx
Route : /settings (renommer en /admin pour clarté)
```

#### Sous-pages (tabs ou navigation) :

- [ ] **Utilisateurs** (`/admin/users`) :
  - DataTable : nom, email, rôle, unité, statut (actif/inactif), dernière connexion
  - Créer utilisateur (formulaire modale)
  - Modifier rôle / unité
  - Désactiver (pas supprimer)

- [ ] **Unités** (`/admin/units`) :
  - Liste : nom, description, nombre de bénéficiaires, nombre de MSP
  - Créer/Modifier unité

- [ ] **Catégories journal** (`/admin/categories`) :
  - Liste : nom, icône, couleur, description
  - Créer/Modifier/Désactiver

- [ ] **Référentiel compétences** (`/admin/skills`) :
  - Liste : nom, catégorie, description
  - Créer/Modifier/Supprimer

- [ ] **Logs d'audit** (`/admin/audit`) :
  - DataTable : date, utilisateur, action, entité, détails
  - Filtres : date range, utilisateur, action
  - Read-only (pas de modification)

### 5.5 Page — Rapports

```
Fichier : frontend/src/pages/reports/ReportsPage.tsx
Route : /reports (ajouter à la sidebar)
```

- [ ] Cartes de rapports disponibles :
  - **Résumé bénéficiaire** : Sélectionner bénéficiaire → Générer PDF
  - **Rapport d'activité** : Sélectionner période → Générer PDF
  - **Bilan objectifs** : Sélectionner filtres → Export Excel
  - **Statistiques absences** : Sélectionner unité + période → Export Excel
  - **Répertoire comportements à risque** : Export Excel
- [ ] Chaque carte : description, bouton "Générer", paramètres (date, bénéficiaire, unité)
- [ ] Téléchargement automatique après génération

### 5.6 Page — Notifications

```
Fichier : frontend/src/pages/notifications/NotificationsPage.tsx
Route : /notifications (accessible via l'icône cloche du header)
```

- [ ] Liste chronologique des notifications
- [ ] Types : objectif en retard, rappel, nouvelle entrée journal, absence à valider
- [ ] Marquer comme lue (individuel + tout marquer)
- [ ] Clic → navigation vers l'élément concerné
- [ ] Badge dans le header avec le count non-lues

### 5.7 Mise à jour du routing (App.tsx)

```
Fichier : frontend/src/App.tsx
```

- [ ] Ajouter toutes les nouvelles routes
- [ ] Ajouter `ProtectedRoute` component (vérifie auth + rôle)
- [ ] Routes imbriquées pour bénéficiaire (tabs)
- [ ] Route 404 avec page dédiée
- [ ] Lazy loading des pages (`React.lazy` + `Suspense`)

### 5.8 Mise à jour de la Sidebar

```
Fichier : frontend/src/components/layout/Sidebar.tsx
```

- [ ] Ajouter les entrées manquantes :
  - Rapports (icône `FileBarChart`)
  - Administration (icône `Shield`, visible ADMIN/RUA seulement)
  - Temps (icône `Clock`, peut-être dans la fiche bénéficiaire uniquement)
- [ ] Badge de notifications sur l'icône

### 5.9 Mise à jour du Header

```
Fichier : frontend/src/components/layout/Header.tsx
```

- [ ] Icône notifications (cloche) avec badge count
- [ ] Dropdown notifications (preview des 5 dernières)
- [ ] Recherche globale (SearchCommand avec `cmdk`)
- [ ] Menu utilisateur : profil, changer mot de passe, déconnexion

---

## 7. Phase 6 — Sécurité et conformité

### 6.1 Vérification chiffrement médical

- [ ] Tester que les données médicales sont bien chiffrées en DB (AES-256)
- [ ] Vérifier que le déchiffrement fonctionne correctement à la lecture
- [ ] Vérifier que seuls les rôles autorisés peuvent accéder à `/medical`
- [ ] Log d'audit sur chaque accès aux données médicales

### 6.2 Audit trail complet

- [ ] Vérifier que chaque action sensible crée un `AuditLog` :
  - Connexion/déconnexion
  - Création/modification/suppression de bénéficiaire
  - Accès aux données médicales
  - Modification d'objectifs
  - Exports et téléchargements
- [ ] Stocker : `user_id`, `action`, `entity_type`, `entity_id`, `old_values`, `new_values`, `ip_address`, `user_agent`
- [ ] Créer un middleware FastAPI pour capturer automatiquement les changements

### 6.3 Protection CSRF

- [ ] Implémenter les tokens CSRF pour les formulaires
- [ ] Ou s'appuyer sur les headers CORS + JWT (suffisant pour API REST SPA)

### 6.4 Sanitization des inputs

- [ ] Backend : Valider et sanitiser tous les champs texte (HTML, scripts)
- [ ] Frontend : Utiliser DOMPurify pour afficher le contenu rich text du journal
- [ ] Vérifier les headers de sécurité Nginx (déjà configurés, valider)

### 6.5 Rate limiting

- [ ] Vérifier la config Nginx existante (10 r/s general, 5 r/m login)
- [ ] Ajouter rate limiting applicatif si nécessaire (slowapi pour FastAPI)

### 6.6 Politique de mots de passe

- [ ] Vérifier : min 12 chars, majuscule, minuscule, chiffre, caractère spécial
- [ ] Rotation 90 jours (champ `password_changed_at` + middleware de vérification)
- [ ] Historique des 5 derniers mots de passe (empêcher réutilisation)
- [ ] Lockout après 5 tentatives (15 min)

---

## 8. Phase 7 — Tests

### 7.1 Tests backend — API (pytest)

```
Fichier : backend/tests/test_api/
```

Pour chaque module API, tester :

- [ ] **Auth** : login ok, login fail, refresh token, change password, permissions
- [ ] **Users** : CRUD, filtrage par rôle, isolation par unité
- [ ] **Beneficiaries** : CRUD, filtres, accès par unité, données médicales (accès restreint)
- [ ] **PAIs** : CRUD, activation, clôture, validation des statuts
- [ ] **Objectives** : CRUD, mise à jour progression, changement statut, filtres (overdue, par type)
- [ ] **Journal** : CRUD, filtres catégorie/date/tags, recherche plein texte, visibilité
- [ ] **Documents** : Upload, download, suppression, accès par confidentialité
- [ ] **Time Tracking** : Pointages, absences, validation, calcul stats
- [ ] **Skills** : Référentiel, évaluation, formations
- [ ] **Dashboard** : MSP dashboard, Management dashboard, calculs corrects
- [ ] **Admin** : Gestion unités, catégories, audit logs (accès ADMIN only)
- [ ] **Notifications** : Liste, mark read, unread count
- [ ] **Reports** : Génération PDF, export Excel

Setup tests :
- [ ] Fixtures : base de données de test (SQLite ou PostgreSQL de test)
- [ ] Factory functions pour créer les entités de test
- [ ] Client HTTP de test (httpx AsyncClient)
- [ ] Nettoyage entre les tests (rollback transaction)

### 7.2 Tests frontend — Composants (Vitest)

```
Fichier : frontend/src/__tests__/
```

- [ ] Tests composants partagés : DataTable, FormField, StatusBadge, ConfirmDialog
- [ ] Tests pages : Login (soumission formulaire, erreurs), Dashboard (affichage données)
- [ ] Tests hooks : useDebounce, usePagination
- [ ] Tests stores : authStore (login, logout, token refresh)
- [ ] Mocks : API calls (msw ou vi.mock)

### 7.3 Objectif de couverture

- [ ] Backend : 80%+ sur les services et API
- [ ] Frontend : 60%+ sur les composants critiques
- [ ] Tests de sécurité : tous les contrôles d'accès RBAC testés

---

## 9. Phase 8 — Déploiement Infomaniak

### 8.1 Choix d'infrastructure

- [ ] **Option recommandée** : VPS Infomaniak (ou Public Cloud) avec Docker
  - VPS Linux (Ubuntu 22.04 ou Debian 12)
  - Min 4 vCPU, 8 GB RAM, 100 GB SSD (à ajuster selon charge)
  - IP publique fixe
- [ ] Alternative : Jelastic Cloud Infomaniak (PaaS avec Docker)

### 8.2 Setup serveur

- [ ] Provisionner le VPS sur Infomaniak
- [ ] Installer Docker + Docker Compose
- [ ] Configurer le firewall (UFW) : ports 80, 443, 22 uniquement
- [ ] Créer un utilisateur dédié (pas root)
- [ ] Configurer SSH (clé, désactiver password auth)

### 8.3 Configuration DNS

- [ ] Pointer le domaine (ex: `cis.votredomaine.ch`) vers l'IP du VPS
- [ ] Configurer les enregistrements DNS sur Infomaniak

### 8.4 SSL/TLS

- [ ] Installer Certbot dans le conteneur Nginx ou en sidecar
- [ ] Décommenter la config HTTPS dans `nginx.conf`
- [ ] Forcer la redirection HTTP → HTTPS
- [ ] Renouvellement automatique (cron certbot renew)

### 8.5 Docker Compose production

```
Fichier : docker-compose.prod.yml (override)
```

- [ ] Variables d'environnement via `.env.production` (ne PAS committer)
  - `SECRET_KEY` (généré, 64+ chars)
  - `DATABASE_URL` (avec mot de passe fort)
  - `REDIS_URL`
  - `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` (Infomaniak SMTP)
  - `ALLOWED_ORIGINS` (domaine de production)
- [ ] Restart policy : `unless-stopped`
- [ ] Limites de ressources (memory, CPU)
- [ ] Logging driver (json-file avec rotation)
- [ ] Networks : isoler frontend, backend, database

### 8.6 Backups automatisés

- [ ] Script `backup.sh` :
  - `pg_dump` de PostgreSQL (compressé, daté)
  - Copie des fichiers MinIO
  - Chiffrement GPG des backups
- [ ] Cron : backup quotidien à 2h du matin
- [ ] Rétention : 30 jours local, archivage sur Infomaniak Swiss Backup (ou Object Storage)
- [ ] Script de restauration documenté et testé

### 8.7 SMTP Infomaniak

- [ ] Créer une adresse email dédiée (ex: `noreply@votredomaine.ch`) sur Infomaniak
- [ ] Configurer les variables SMTP dans le backend :
  - Host : `mail.infomaniak.com`
  - Port : `587` (STARTTLS)
  - User : l'adresse email créée
  - Password : mot de passe de l'adresse
- [ ] Tester l'envoi d'email (reset password)

### 8.8 Monitoring

- [ ] Health check automatique (cron curl /health toutes les 5 min)
- [ ] Alertes email si service down
- [ ] Option : Prometheus + Grafana dans Docker (si besoin de métriques avancées)
- [ ] Logs centralisés : docker logs avec rotation

### 8.9 CI/CD (optionnel mais recommandé)

- [ ] GitHub Actions workflow :
  1. Push sur `main` → build Docker images
  2. Run tests
  3. SSH deploy sur le VPS (docker-compose pull && docker-compose up -d)
- [ ] Ou script de déploiement manuel :
  ```bash
  ssh user@server "cd /opt/cis && git pull && docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
  ```

### 8.10 Checklist pré-production

- [ ] Toutes les variables d'environnement configurées
- [ ] SSL/TLS actif avec certificat valide
- [ ] Backups fonctionnels et testés
- [ ] Données de seed de production (unités réelles, comptes utilisateurs réels)
- [ ] Mot de passe admin changé après premier login
- [ ] Rate limiting vérifié
- [ ] Headers de sécurité validés (securityheaders.com)
- [ ] Logs d'audit fonctionnels
- [ ] Email de test envoyé et reçu
- [ ] Test de restauration de backup réussi

---

## 10. Annexes

### Annexe A — Ordre de priorité recommandé

```
Phase 1 (Fondations)       ← Faire en premier, bloquant
Phase 2 (Backend)           ← Compléter les TODO + endpoints manquants
Phase 3 (Composants)        ← Briques réutilisables
Phase 4 (Pages principales) ← Bénéficiaires, PAI, Objectifs, Journal
Phase 5 (Pages secondaires) ← Temps, Compétences, Documents, Admin, Rapports
Phase 6 (Sécurité)          ← Vérification et renforcement
Phase 7 (Tests)             ← Peut commencer en parallèle dès Phase 2
Phase 8 (Déploiement)       ← Peut commencer dès Phase 1 pour l'infra de base
```

### Annexe B — Dépendances npm à ajouter

```bash
npm install @tanstack/react-table recharts date-fns
npm install @tiptap/react @tiptap/starter-kit @tiptap/extension-link  # Rich text
npm install dompurify @types/dompurify                                  # Sanitization
npm install cmdk                                                        # Command palette (search)
npm install react-dropzone                                              # File upload
npm install xlsx                                                        # Excel export (frontend)
```

### Annexe C — Dépendances Python à ajouter

```bash
pip install minio          # Object storage
pip install aiosmtplib     # Async email
pip install weasyprint     # PDF generation
pip install openpyxl       # Excel generation
pip install slowapi         # Rate limiting applicatif
pip install python-multipart # File upload (déjà probablement inclus)
```

### Annexe D — Structure des fichiers à créer

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── risk_behaviors.py    (NOUVEAU)
│   │   ├── skills.py            (NOUVEAU)
│   │   ├── time_tracking.py     (NOUVEAU)
│   │   ├── admin.py             (NOUVEAU)
│   │   ├── notifications.py     (NOUVEAU)
│   │   └── reports.py           (NOUVEAU)
│   ├── services/
│   │   ├── storage.py           (NOUVEAU - MinIO)
│   │   ├── email.py             (NOUVEAU - SMTP)
│   │   └── pdf.py               (NOUVEAU - PDF generation)
│   └── repositories/
│       ├── skill_repository.py       (NOUVEAU)
│       ├── time_tracking_repository.py (NOUVEAU)
│       ├── notification_repository.py  (NOUVEAU)
│       └── risk_behavior_repository.py (NOUVEAU)
├── scripts/
│   └── seed.py                  (NOUVEAU)

frontend/
├── src/
│   ├── api/
│   │   ├── timeTracking.ts      (NOUVEAU)
│   │   ├── skills.ts            (NOUVEAU)
│   │   ├── documents.ts         (NOUVEAU)
│   │   ├── reports.ts           (NOUVEAU)
│   │   ├── notifications.ts     (NOUVEAU)
│   │   └── admin.ts             (NOUVEAU)
│   ├── components/
│   │   └── shared/
│   │       ├── DataTable.tsx     (NOUVEAU)
│   │       ├── FormField.tsx     (NOUVEAU)
│   │       ├── FormSelect.tsx    (NOUVEAU)
│   │       ├── FormDatePicker.tsx(NOUVEAU)
│   │       ├── FormTextarea.tsx  (NOUVEAU)
│   │       ├── FormMultiSelect.tsx(NOUVEAU)
│   │       ├── ConfirmDialog.tsx (NOUVEAU)
│   │       ├── StatusBadge.tsx   (NOUVEAU)
│   │       ├── FileUpload.tsx    (NOUVEAU)
│   │       ├── RichTextEditor.tsx(NOUVEAU)
│   │       ├── EmptyState.tsx    (NOUVEAU)
│   │       └── PageHeader.tsx    (NOUVEAU)
│   ├── hooks/
│   │   ├── useDebounce.ts       (NOUVEAU)
│   │   ├── usePagination.ts     (NOUVEAU)
│   │   └── useQueryParams.ts    (NOUVEAU)
│   ├── stores/
│   │   ├── notificationStore.ts (NOUVEAU)
│   │   └── filterStore.ts       (NOUVEAU)
│   └── pages/
│       ├── beneficiaries/
│       │   ├── BeneficiaryDetailPage.tsx (NOUVEAU)
│       │   └── BeneficiaryFormPage.tsx   (NOUVEAU)
│       ├── pais/
│       │   ├── PAIDetailPage.tsx  (NOUVEAU)
│       │   └── PAIFormPage.tsx    (NOUVEAU)
│       ├── objectives/
│       │   ├── ObjectiveListPage.tsx   (NOUVEAU)
│       │   └── ObjectiveDetailPage.tsx (NOUVEAU)
│       ├── journal/
│       │   ├── JournalListPage.tsx   (NOUVEAU)
│       │   ├── JournalEntryPage.tsx  (NOUVEAU)
│       │   └── JournalFormPage.tsx   (NOUVEAU)
│       ├── time/
│       │   └── TimeTrackingPage.tsx  (NOUVEAU)
│       ├── skills/
│       │   └── SkillsPage.tsx       (NOUVEAU)
│       ├── documents/
│       │   └── DocumentListPage.tsx  (NOUVEAU)
│       ├── admin/
│       │   └── AdminPage.tsx        (NOUVEAU)
│       ├── reports/
│       │   └── ReportsPage.tsx      (NOUVEAU)
│       └── notifications/
│           └── NotificationsPage.tsx (NOUVEAU)
```

### Annexe E — Compteurs

| Catégorie | Existant | À créer | Total |
|-----------|---------|---------|-------|
| Backend API routes | 9 fichiers | 6 fichiers | 15 |
| Backend services | 0 | 3 | 3 |
| Backend repositories | 8 | 4 | 12 |
| Frontend pages | 3 | ~15 | ~18 |
| Frontend composants shared | 0 | 12 | 12 |
| Frontend API clients | 6 | 6 | 12 |
| Frontend hooks | 0 | 3 | 3 |
| Frontend stores | 2 | 2 | 4 |
| shadcn/ui composants | 7 | ~15 | ~22 |
