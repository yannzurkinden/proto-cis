# Documentation Projet CIS

## Vue d'Ensemble

**CIS** (Centrale d'Information Socioprofessionnelle) est une application de suivi de l'accompagnement socioprofessionnel pour les personnes bénéficiaires de l'Assurance Invalidité (AI) en Suisse.

## Documents du Cahier des Charges

| Document | Description |
|----------|-------------|
| [01-cahier-des-charges.md](./01-cahier-des-charges.md) | Cahier des charges fonctionnel complet |
| [02-architecture-technique.md](./02-architecture-technique.md) | Architecture technique et stack |
| [03-modele-donnees.md](./03-modele-donnees.md) | Schéma de base de données PostgreSQL |
| [04-specifications-api.md](./04-specifications-api.md) | Spécifications API REST complètes |
| [05-specifications-ui-ux.md](./05-specifications-ui-ux.md) | Design system et maquettes UI |
| [06-securite-conformite.md](./06-securite-conformite.md) | Sécurité, RBAC et conformité LPD |

## Stack Technique

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                          │
│  React 18 + TypeScript + Vite + Tailwind + shadcn   │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    BACKEND                           │
│  Python 3.11 + FastAPI + SQLAlchemy 2.0 + Alembic  │
└─────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐    ┌──────────┐
    │PostgreSQL│   │  Redis   │    │  MinIO   │
    │   15+    │   │ (cache)  │    │ (files)  │
    └──────────┘   └──────────┘    └──────────┘

Conteneurisation: Docker + Docker Compose
```

## Modules Fonctionnels

1. **Gestion des Bénéficiaires (CAI)**
   - Profil complet (personnel, administratif, médical)
   - Réseau de contacts
   - Comportements à risque

2. **Plans d'Accompagnement (PAI)**
   - Bilan initial
   - Objectifs (court/moyen/long terme)
   - Actions et indicateurs

3. **Journal de Bord**
   - Entrées catégorisées et taguées
   - Recherche plein texte
   - Collaboration inter-unités

4. **Gestion du Temps**
   - Timbrages
   - Absences et justificatifs
   - Statistiques absentéisme

5. **Compétences et Formations**
   - Matrice de compétences
   - Historique formations

6. **Documents (GED)**
   - Upload et versioning
   - Niveaux de confidentialité

7. **Tableaux de Bord**
   - Vue MSP (mes bénéficiaires)
   - Vue Direction (statistiques globales)
   - Vue Objectifs (tous les CAI)

8. **Rapports**
   - Synthèse individuelle
   - Rapport d'activité
   - Exports PDF/Excel

## Rôles Utilisateurs

| Rôle | Code | Accès |
|------|------|-------|
| Administrateur | ADMIN | Complet |
| Responsable d'unité | RUA | Unité + lecture inter-unités |
| Responsable | RES | Équipe |
| Maître socioprofessionnel | MSP | Ses références + lecture unité |
| Consultation | CONSULT | Lecture seule unité |

## Points Clés Sécurité

- Authentification JWT avec refresh tokens
- Chiffrement AES-256 des données médicales
- RBAC avec permissions granulaires
- Audit trail complet
- Conformité LPD suisse
- Hébergement on-premise obligatoire

## Démarrage Rapide (Développement)

```bash
# Cloner le repo
git clone <repo-url>
cd cis_projet

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (nouveau terminal)
cd frontend
npm install
npm run dev

# Docker (alternative)
docker-compose up -d
```

## Contacts

- **Product Owner**: [À définir]
- **Tech Lead**: [À définir]
- **Équipe Métier**: [À définir]
