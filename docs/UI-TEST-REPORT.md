# CIS Application - UI Test Report

**Date:** 2026-01-29
**Tester:** Automated UI Testing (Claude)
**Environment:** Docker Compose (localhost:8088)
**User:** admin@cis.local (ADMIN role)

---

## Executive Summary

The CIS application is functional overall with most pages rendering correctly and navigation working. However, several **critical backend API errors**, **frontend-backend path mismatches**, and **data issues** prevent key features from working. Additionally, **French accents are missing throughout** the entire application.

### Severity Legend
- **CRITICAL** - Feature completely broken, blocks usage
- **HIGH** - Feature partially broken, significant impact
- **MEDIUM** - Feature works but with notable issues
- **LOW** - Cosmetic or minor issues

---

## 1. CRITICAL - Broken Backend API Endpoints (500 Errors)

### 1.1 `GET /api/v1/skills` - 500 Internal Server Error
- **Error:** `AttributeError: 'SkillRepository' object has no attribute 'get_all_skills'`
- **Location:** `backend/app/api/v1/admin.py:362`
- **Impact:** Admin "Referentiel competences" tab may fail to load reference skills list. The SkillsPage on beneficiary detail also calls this endpoint.
- **Fix needed:** The `SkillRepository` has a method called `get_all_active()` (used in `skills.py:40`), but `admin.py:362` calls `get_all_skills()` which doesn't exist.

### 1.2 `GET /api/v1/skills/beneficiaries/{id}/trainings` - 500 Internal Server Error
- **Error:** `AttributeError: 'SkillRepository' object has no attribute 'get_beneficiary_trainings'`
- **Location:** `backend/app/api/v1/skills.py:212`
- **Impact:** Training list for beneficiaries is completely broken.
- **Fix needed:** Add `get_beneficiary_trainings()` method to `SkillRepository`.

### 1.3 `GET /api/v1/reports/beneficiary/{id}/summary` - 500 Internal Server Error
- **Error:** `TypeError: PDFService.generate_beneficiary_summary() got an unexpected keyword argument 'beneficiary'`
- **Location:** `backend/app/api/v1/reports.py`
- **Impact:** PDF report generation for beneficiary summaries is completely broken.
- **Fix needed:** Align the keyword arguments between the route handler and `PDFService.generate_beneficiary_summary()`.

### 1.4 All Report Endpoints - 500/503 Errors
- `GET /api/v1/reports/activity` - 503
- `GET /api/v1/reports/objectives` - 503
- `GET /api/v1/reports/absences/stats` - 503
- **Impact:** The entire Reports page ("Rapports") is non-functional. All 4 report types (PDF and Excel) will fail.
- **Fix needed:** Verify PDFService and report generation dependencies are properly installed and configured.

---

## 2. CRITICAL - Missing Backend Routes (404 Errors)

### 2.1 `GET /api/v1/beneficiaries/{id}/pais` - 404 Not Found
- **Impact:** Cannot list PAIs for a beneficiary. The frontend `pais.ts:30` calls this path, but the backend only registers PAI routes under the `/pais` prefix (router.py:28). There is no route handler for listing beneficiary PAIs.
- **Fix needed:** Add a route in the `pais.py` or `beneficiaries.py` router to handle `GET /beneficiaries/{id}/pais`.

### 2.2 `GET /api/v1/beneficiaries/{id}/absences/stats` - 405 Method Not Allowed
- **Impact:** Absence statistics are unavailable. The "Temps & Absences" tab shows "Donnees non disponibles" for the "Taux d'absence" card.
- **Fix needed:** The route exists but the HTTP method doesn't match. Check if the endpoint is registered as POST instead of GET.

---

## 3. HIGH - Frontend-Backend API Path Mismatches

### 3.1 SkillsPage calls wrong endpoints
- **Observed network requests from the SkillsPage:**
  - `GET /api/v1/beneficiaries/1/skills/evaluations` → **404** (path doesn't exist)
  - `GET /api/v1/beneficiaries/1/skills` → **404** (wrong prefix)
  - `GET /api/v1/skills` → **500** (backend error, see 1.1)
- **Correct endpoint:** `GET /api/v1/skills/beneficiaries/1/skills` → **200** (works)
- **Impact:** The "Competences" tab on beneficiary detail shows "Aucune competence evaluee" despite data existing (verified via direct API call - 7+ evaluations exist).
- **Fix needed:** Update `SkillsPage.tsx` to call the correct API path `/skills/beneficiaries/{id}/skills` instead of `/beneficiaries/{id}/skills/evaluations`.

---

## 4. HIGH - Data Issues

### 4.1 Medical data returns empty
- **Endpoint:** `GET /api/v1/beneficiaries/1/medical` returns 200 with all empty strings:
  ```json
  {"beneficiary_id":1,"medication":"","restrictions":"","allergies":"","medical_notes":""}
  ```
- **Impact:** "Donnees medicales" tab shows "Aucune information" for all fields despite seed data creating medical records with medication, restrictions, allergies.
- **Root cause:** Likely an encryption/decryption issue. The seed data stores medical data but the AES-256 encryption may not be properly encrypting during seed or decrypting during retrieval.

### 4.2 Time entries not displayed in UI
- **Endpoint:** `GET /api/v1/beneficiaries/1/time-entries` returns 200 with data.
- **Impact:** The "Temps & Absences" tab only shows vacation balance and empty absences section. There is no UI section to display actual time entries (attendance records). The seed data creates ~300+ time entries but they are invisible in the UI.
- **Fix needed:** Add a time entries table/list to the TimeTrackingPage component.

### 4.3 Absence data not shown despite existing
- The "Absences recentes" card and section show "Donnees non disponibles" / "Aucune absence recente" despite seed data creating absences.

---

## 5. MEDIUM - Business Logic Issues

### 5.1 PAI shows "Actif" after expiration
- David Schneider's PAI is valid "Du 10 juin 2024 au 10 juin 2025" but still displays the green "Actif" badge.
- **Fix needed:** Add logic to mark PAIs as expired when `valid_to` date has passed, or display a warning.

### 5.2 Overdue objectives lack visual indicator
- Objectives with past due dates (e.g., "Echeance: 18 janvier 2026") on the beneficiary detail Objectifs tab show the date but no red/warning overdue indicator. The objectives list page shows red dates but the per-beneficiary view does not highlight overdue status.

### 5.3 Dashboard alerts in English
- Alert messages show "is overdue" in English: *"Objective 'Maitriser les outils de l'atelier' is overdue"*
- Should be in French to match the rest of the UI.

### 5.4 Audit logs empty
- The "Logs d'audit" tab shows "Aucun log d'audit trouve" despite multiple user actions being performed during the session. The AuditMiddleware may not be properly storing logs.

### 5.5 Beneficiary list filter not functional
- The filter icon (funnel) on the Beneficiary list page does not open a filter panel when clicked. The search bar works, but the advanced filter (by status, unit, etc.) appears unimplemented.

---

## 6. MEDIUM - Missing UI Features

### 6.1 No "Edit User" action in Admin
- The Users tab in Administration only has a "Desactiver" button per user. There is no way to edit user details (name, email, role, unit assignment).

### 6.2 No time entry creation UI
- The "Temps & Absences" tab lacks buttons to create new time entries or log attendance. Only vacation balance is displayed.

### 6.3 No absence creation UI
- No visible button to record a new absence from the "Temps & Absences" tab.

### 6.4 No "Forgot Password" link on login
- The login page has no "Mot de passe oublie?" link despite the backend having `POST /auth/forgot-password` and `POST /auth/reset-password` endpoints.

### 6.5 Notification bell has no dropdown
- The notification bell icon in the header navigates to `/notifications` page but doesn't show a quick dropdown/popover with recent notifications.

---

## 7. LOW - Cosmetic / Localization Issues

### 7.1 Missing French accents throughout the entire application
This is a **systemic issue** affecting every page. All text stored in the database and hardcoded in the frontend is missing French diacritical marks. Examples:

| Displayed | Expected |
|-----------|----------|
| Unite | Unité |
| Numero AI | Numéro AI |
| Ne(e) le | Né(e) le |
| Donnees medicales | Données médicales |
| Reseau / Contacts | Réseau / Contacts |
| Comportements a risque | Comportements à risque |
| Competences | Compétences |
| Echeance | Échéance |
| Priorite | Priorité |
| Confidentialite | Confidentialité |
| Derniere connexion | Dernière connexion |
| Desactiver | Désactiver |
| Referentiel competences | Référentiel compétences |
| Categories journal | Catégories journal |
| Generer PDF | Générer PDF |
| Resume beneficiaire | Résumé bénéficiaire |
| Sante | Santé |
| Vie privee | Vie privée |
| Ponctualite | Ponctualité |
| Qualite du travail | Qualité du travail |

This affects: page titles, tab labels, form labels, table headers, button text, status badges, and all seed data content.

### 7.2 Language displayed as code
- Beneficiary profile shows `Langue: fr` instead of `Langue: Francais`.

### 7.3 Pension type not translated
- Shows "Demi-rente" which is acceptable but other values may show raw enum values.

---

## 8. Pages Tested - Status Summary

| Page | Route | Status | Notes |
|------|-------|--------|-------|
| Login | `/login` | OK | Works, missing "forgot password" link |
| Dashboard | `/dashboard` | OK | Stats cards, alerts work. Alert text in English. |
| Beneficiary List | `/beneficiaries` | PARTIAL | List works, search works, filter icon broken |
| Beneficiary Detail | `/beneficiaries/:id` | PARTIAL | Profile tab OK, multiple tabs have data issues |
| - Profil tab | | OK | Data displays correctly (minus accents) |
| - Donnees medicales | | BROKEN | All fields empty despite seed data |
| - Reseau/Contacts | | OK | Lists contacts, edit/delete/add buttons work |
| - Comportements a risque | | OK | Shows data when present, add button works |
| - Objectifs | | OK | Shows objectives with progress bars |
| - Journal | | OK | Shows entries with category filter |
| - Temps & Absences | | PARTIAL | Vacation balance OK, absences/time entries broken |
| - Competences | | BROKEN | Shows empty due to API path mismatch |
| - Documents | | OK | Empty state with upload button |
| PAI Detail | `/beneficiaries/:id/pais/:paiId` | OK | Shows strengths/difficulties/wishes/objectives |
| Objectifs List | `/objectives` | OK | Table with filters, badges, progress bars |
| Journal List | `/journal` | OK | Search, filters, category badges |
| Documents List | `/documents` | OK | Search, type/confidentiality filters |
| Notifications | `/notifications` | OK | Empty state (no seed data) |
| Rapports | `/reports` | BROKEN | UI renders but all 4 export buttons will fail (500/503) |
| Administration | `/admin` | PARTIAL | |
| - Utilisateurs | | PARTIAL | List works, missing edit action |
| - Unites | | OK | Cards with edit, add button |
| - Categories journal | | OK | Color-coded list with edit |
| - Referentiel competences | | OK | Table with edit/delete |
| - Logs d'audit | | BROKEN | Always empty, filters present |
| 404 Page | `/*` | OK | Not tested but route exists |

---

## 9. API Endpoints - Full Test Results

| Status | Endpoint | Issue |
|--------|----------|-------|
| 200 | `GET /api/v1/dashboard/msp` | OK |
| 200 | `GET /api/v1/dashboard/management` | OK |
| 200 | `GET /api/v1/beneficiaries` | OK |
| 200 | `GET /api/v1/beneficiaries/1` | OK |
| 200 | `GET /api/v1/beneficiaries/1/medical` | Returns empty data |
| 200 | `GET /api/v1/beneficiaries/1/contacts` | OK |
| 200 | `GET /api/v1/beneficiaries/1/risk-behaviors` | OK |
| **404** | `GET /api/v1/beneficiaries/1/pais` | **Route missing** |
| 200 | `GET /api/v1/pais/1` | OK |
| 200 | `GET /api/v1/objectives` | OK |
| 200 | `GET /api/v1/objectives/overview` | OK |
| 200 | `GET /api/v1/journal` | OK |
| 200 | `GET /api/v1/documents` | OK |
| **500** | `GET /api/v1/skills` | **SkillRepository.get_all_skills missing** |
| 200 | `GET /api/v1/skills/beneficiaries/1/skills` | OK |
| **500** | `GET /api/v1/skills/beneficiaries/1/trainings` | **SkillRepository.get_beneficiary_trainings missing** |
| 200 | `GET /api/v1/beneficiaries/1/time-entries` | OK (but no UI) |
| 200 | `GET /api/v1/beneficiaries/1/absences` | OK |
| **405** | `GET /api/v1/beneficiaries/1/absences/stats` | **Wrong HTTP method** |
| 200 | `GET /api/v1/beneficiaries/1/vacation-balance` | OK |
| 200 | `GET /api/v1/notifications` | OK |
| 200 | `GET /api/v1/notifications/unread-count` | OK |
| 200 | `GET /api/v1/admin/journal-categories` | OK |
| 200 | `GET /api/v1/admin/audit-logs` | OK (returns empty) |
| 200 | `GET /api/v1/users` | OK |
| 200 | `GET /api/v1/users/me` | OK |
| 200 | `GET /api/v1/units` | OK |
| **500** | `GET /api/v1/reports/beneficiary/1/summary` | **PDFService argument mismatch** |
| **503** | `GET /api/v1/reports/activity` | **Service unavailable** |
| **503** | `GET /api/v1/reports/objectives` | **Service unavailable** |
| **503** | `GET /api/v1/reports/absences/stats` | **Service unavailable** |

---

## 10. Priority Fix Recommendations

### Immediate (CRITICAL)
1. Fix `SkillRepository` missing methods (`get_all_skills`, `get_beneficiary_trainings`)
2. Fix `PDFService.generate_beneficiary_summary()` argument mismatch
3. Add `GET /beneficiaries/{id}/pais` route to backend
4. Fix SkillsPage frontend API paths
5. Fix medical data encryption/decryption pipeline

### Short-term (HIGH)
6. Fix absence stats endpoint (405 error)
7. Add time entries display to TimeTrackingPage
8. Fix absences display in TimeTrackingPage
9. Fix all report generation (503 errors)

### Medium-term (MEDIUM)
10. Add French accents to all UI text and seed data
11. Implement beneficiary list filter panel
12. Add Edit User functionality in Admin
13. Fix PAI expiration status logic
14. Translate dashboard alert messages to French
15. Fix audit log recording

### Nice-to-have (LOW)
16. Add "Forgot password" link to login page
17. Add notification dropdown in header
18. Display language as "Francais" instead of "fr"
