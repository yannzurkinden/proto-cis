# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CIS** - Application de suivi de l'accompagnement socioprofessionnel pour les bénéficiaires de l'Assurance Invalidité (AI) en Suisse.

## Documentation

Cahier des charges complet disponible dans `/docs/`:
- `00-index.md` - Vue d'ensemble et démarrage rapide
- `01-cahier-des-charges.md` - Exigences fonctionnelles détaillées
- `02-architecture-technique.md` - Stack technique et structure projet
- `03-modele-donnees.md` - Schéma PostgreSQL complet
- `04-specifications-api.md` - Endpoints REST API
- `05-specifications-ui-ux.md` - Design system et composants
- `06-securite-conformite.md` - Sécurité et conformité LPD

## Stack Technique

```
Frontend:  React 18 + TypeScript + Vite + Tailwind + shadcn/ui
Backend:   Python 3.11 + FastAPI + SQLAlchemy 2.0 (async)
Database:  PostgreSQL 15 + Alembic (migrations)
Cache:     Redis
Storage:   MinIO (S3-compatible, on-premise)
Infra:     Docker + Docker Compose + Nginx
```

## Domain Concepts

- **CAI** (Collaborateur en Atelier d'Insertion): Bénéficiaire accompagné
- **MSP** (Maître Socioprofessionnel): Accompagnant/référent
- **PAI** (Plan d'Accompagnement Individualisé): Plan avec objectifs
- **RUA/RES**: Rôles de direction avec accès élargi

## Project Structure

```
cis_projet/
├── docs/               # Cahier des charges (cette doc)
├── backend/
│   ├── app/
│   │   ├── api/v1/     # Routes FastAPI
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   └── repositories/
│   ├── alembic/        # DB migrations
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # React components
│   │   ├── pages/      # Page views
│   │   ├── hooks/      # Custom hooks
│   │   └── stores/     # Zustand stores
│   └── tests/
└── docker-compose.yml
```

## Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload          # Dev server
alembic upgrade head                    # Run migrations
alembic revision --autogenerate -m "x"  # Create migration
pytest                                  # Run tests
ruff check .                           # Lint

# Frontend
cd frontend
npm run dev                            # Dev server
npm run build                          # Production build
npm run test                           # Run tests
npm run lint                           # ESLint

# Docker
docker-compose up -d                   # Start all services
docker-compose logs -f backend         # View logs
docker-compose exec backend alembic upgrade head
```

## Key Constraints

- **On-premise hosting** (no public cloud)
- **Swiss LPD compliance** (data protection)
- **Medical data encrypted** (AES-256)
- **RBAC** with unit-level isolation
- **Audit trail** for all sensitive actions
