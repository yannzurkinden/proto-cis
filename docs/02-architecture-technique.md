# Architecture Technique - CIS

## 1. Vue d'Ensemble

### 1.1 Diagramme d'Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INFRASTRUCTURE                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Docker Host (On-Premise)                      │   │
│  │                                                                       │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  │   │
│  │  │   Nginx     │    │   React     │    │       FastAPI           │  │   │
│  │  │   Reverse   │───▶│   Frontend  │    │       Backend           │  │   │
│  │  │   Proxy     │    │   :3000     │    │       :8000             │  │   │
│  │  │   :80/:443  │───▶│             │───▶│                         │  │   │
│  │  └─────────────┘    └─────────────┘    └───────────┬─────────────┘  │   │
│  │                                                     │                 │   │
│  │                                        ┌────────────┼────────────┐   │   │
│  │                                        │            │            │   │   │
│  │                                        ▼            ▼            ▼   │   │
│  │                                 ┌──────────┐ ┌──────────┐ ┌────────┐│   │
│  │                                 │PostgreSQL│ │  Redis   │ │ MinIO  ││   │
│  │                                 │  :5432   │ │  :6379   │ │ :9000  ││   │
│  │                                 │          │ │ (cache)  │ │(files) ││   │
│  │                                 └──────────┘ └──────────┘ └────────┘│   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Volumes persistants : postgres_data, redis_data, minio_data, uploads      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Composants

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Reverse Proxy | Nginx | SSL termination, routing, load balancing |
| Frontend | React + TypeScript | Interface utilisateur SPA |
| Backend | FastAPI (Python) | API REST, logique métier |
| Base de données | PostgreSQL 15 | Stockage relationnel |
| Cache | Redis | Sessions, cache requêtes |
| Stockage fichiers | MinIO | Stockage S3-compatible on-premise |
| Migrations | Alembic | Versioning schéma BDD |

---

## 2. Stack Technique Détaillée

### 2.1 Frontend

```yaml
Framework: React 18+
Langage: TypeScript 5+
Build: Vite
State Management: Zustand ou React Query
Routing: React Router v6
UI Components:
  - Tailwind CSS
  - shadcn/ui (composants)
  - Lucide React (icônes)
Formulaires: React Hook Form + Zod
Tables: TanStack Table
Charts: Recharts
Date: date-fns
HTTP Client: Axios ou fetch natif
Tests: Vitest + React Testing Library
```

### 2.2 Backend

```yaml
Framework: FastAPI 0.100+
Langage: Python 3.11+
ORM: SQLAlchemy 2.0 (async)
Migrations: Alembic
Validation: Pydantic v2
Auth: python-jose (JWT) + passlib (bcrypt)
Background Tasks: Celery + Redis (optionnel)
Email: fastapi-mail
PDF Generation: WeasyPrint ou ReportLab
Excel Export: openpyxl
Tests: pytest + pytest-asyncio + httpx
Linting: ruff
Type Checking: mypy
```

### 2.3 Base de Données

```yaml
SGBD: PostgreSQL 15+
Extensions:
  - pg_trgm (recherche floue)
  - unaccent (recherche sans accents)
  - pgcrypto (chiffrement)
Pooling: asyncpg (intégré SQLAlchemy async)
Backups: pg_dump automatisé (cron)
```

### 2.4 Infrastructure

```yaml
Conteneurisation: Docker 24+
Orchestration: Docker Compose
Reverse Proxy: Nginx (Alpine)
SSL: Let's Encrypt ou certificat interne
Monitoring:
  - Prometheus + Grafana (métriques)
  - Sentry (erreurs)
Logs: Loki ou ELK stack (optionnel)
```

---

## 3. Structure des Projets

### 3.1 Structure Backend

```
backend/
├── alembic/
│   ├── versions/           # Fichiers de migration
│   ├── env.py
│   └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py             # Point d'entrée FastAPI
│   ├── config.py           # Configuration (pydantic-settings)
│   ├── database.py         # Connexion BDD async
│   ├── dependencies.py     # Dépendances FastAPI (auth, db session)
│   │
│   ├── models/             # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py         # Base déclarative
│   │   ├── user.py
│   │   ├── beneficiary.py
│   │   ├── objective.py
│   │   ├── journal.py
│   │   ├── document.py
│   │   └── ...
│   │
│   ├── schemas/            # Schémas Pydantic
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── beneficiary.py
│   │   ├── objective.py
│   │   └── ...
│   │
│   ├── api/                # Routes API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py   # Router principal v1
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── beneficiaries.py
│   │   │   ├── objectives.py
│   │   │   ├── journal.py
│   │   │   ├── documents.py
│   │   │   ├── reports.py
│   │   │   └── dashboard.py
│   │   └── deps.py         # Dépendances communes API
│   │
│   ├── services/           # Logique métier
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── beneficiary_service.py
│   │   ├── objective_service.py
│   │   ├── report_service.py
│   │   └── notification_service.py
│   │
│   ├── repositories/       # Accès données (pattern repository)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── beneficiary_repository.py
│   │   └── ...
│   │
│   └── utils/              # Utilitaires
│       ├── __init__.py
│       ├── security.py     # Hashing, JWT
│       ├── pagination.py
│       ├── filters.py
│       └── export.py       # PDF, Excel
│
├── tests/
│   ├── conftest.py         # Fixtures pytest
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
│
├── scripts/
│   ├── init_db.py          # Initialisation BDD
│   └── seed_data.py        # Données de test
│
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── .env.example
```

### 3.2 Structure Frontend

```
frontend/
├── public/
│   ├── favicon.ico
│   └── locales/            # Fichiers i18n (si multilingue)
│
├── src/
│   ├── main.tsx            # Point d'entrée
│   ├── App.tsx             # Composant racine
│   ├── vite-env.d.ts
│   │
│   ├── api/                # Appels API
│   │   ├── client.ts       # Configuration Axios
│   │   ├── auth.ts
│   │   ├── beneficiaries.ts
│   │   ├── objectives.ts
│   │   └── ...
│   │
│   ├── components/         # Composants réutilisables
│   │   ├── ui/             # Composants shadcn/ui
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   └── ...
│   │   ├── beneficiary/
│   │   │   ├── BeneficiaryCard.tsx
│   │   │   ├── BeneficiaryForm.tsx
│   │   │   └── ...
│   │   ├── objective/
│   │   ├── journal/
│   │   └── common/
│   │       ├── DataTable.tsx
│   │       ├── SearchInput.tsx
│   │       ├── StatusBadge.tsx
│   │       └── ...
│   │
│   ├── pages/              # Pages/vues
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── ...
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   ├── beneficiaries/
│   │   │   ├── BeneficiaryListPage.tsx
│   │   │   ├── BeneficiaryDetailPage.tsx
│   │   │   └── BeneficiaryEditPage.tsx
│   │   ├── objectives/
│   │   ├── journal/
│   │   ├── documents/
│   │   ├── reports/
│   │   └── settings/
│   │
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useBeneficiaries.ts
│   │   ├── useDebounce.ts
│   │   └── ...
│   │
│   ├── stores/             # State management (Zustand)
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── ...
│   │
│   ├── lib/                # Utilitaires
│   │   ├── utils.ts
│   │   ├── constants.ts
│   │   └── validators.ts
│   │
│   ├── types/              # Types TypeScript
│   │   ├── api.ts
│   │   ├── beneficiary.ts
│   │   ├── objective.ts
│   │   └── ...
│   │
│   └── styles/
│       └── globals.css     # Tailwind + customs
│
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── .env.example
```

---

## 4. Configuration Docker

### 4.1 docker-compose.yml

```yaml
version: '3.8'

services:
  # Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  # Frontend React
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=/api
    restart: unless-stopped

  # Backend FastAPI
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://cis:${DB_PASSWORD}@db:5432/cis
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  # Base de données PostgreSQL
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=cis
      - POSTGRES_USER=cis
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cis -d cis"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Cache Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  # Stockage fichiers MinIO
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    ports:
      - "9001:9001"  # Console MinIO (dev only)
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### 4.2 Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code application
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .

# Utilisateur non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3 Frontend Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 5. Sécurité

### 5.1 Authentification

```
┌──────────┐     1. Login      ┌──────────┐
│  Client  │ ─────────────────▶│  Backend │
│          │                   │          │
│          │◀───────────────── │          │
└──────────┘  2. JWT (access   └──────────┘
              + refresh token)

3. Requêtes avec header:
   Authorization: Bearer <access_token>

4. Refresh token en httpOnly cookie
```

### 5.2 Flux d'authentification

1. Login avec email/password
2. Backend vérifie credentials, génère tokens
3. Access token (15 min) retourné dans body
4. Refresh token (7 jours) en cookie httpOnly
5. Renouvellement automatique via /auth/refresh

### 5.3 Contrôle d'accès (RBAC)

```python
# Exemple de décorateur de permission
@router.get("/beneficiaries/{id}/medical")
@require_permissions(["read:medical"])
async def get_medical_data(id: int, current_user: User = Depends(get_current_user)):
    ...
```

### 5.4 Audit Trail

Toutes les actions sensibles sont loggées :
- Qui (user_id)
- Quoi (action, resource, resource_id)
- Quand (timestamp)
- Contexte (IP, user-agent)

---

## 6. API Design

### 6.1 Conventions REST

```
GET    /api/v1/beneficiaries          # Liste (paginée)
GET    /api/v1/beneficiaries/{id}     # Détail
POST   /api/v1/beneficiaries          # Création
PUT    /api/v1/beneficiaries/{id}     # Mise à jour complète
PATCH  /api/v1/beneficiaries/{id}     # Mise à jour partielle
DELETE /api/v1/beneficiaries/{id}     # Suppression
```

### 6.2 Pagination

```json
GET /api/v1/beneficiaries?page=1&size=20&sort=-created_at

Response:
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

### 6.3 Filtres

```
GET /api/v1/beneficiaries?status=active&unit_id=1&search=martin
GET /api/v1/journal?category=health,conflict&date_from=2024-01-01
```

### 6.4 Réponses d'erreur

```json
{
  "detail": "Beneficiary not found",
  "code": "NOT_FOUND",
  "status_code": 404
}
```

---

## 7. Environnements

### 7.1 Développement

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### 7.2 Production

```bash
# Build et démarrage
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Migrations
docker-compose exec backend alembic upgrade head

# Logs
docker-compose logs -f backend
```

### 7.3 Variables d'environnement

```bash
# .env.example
# Database
DB_PASSWORD=secure_password_here
DATABASE_URL=postgresql+asyncpg://cis:${DB_PASSWORD}@db:5432/cis

# Security
SECRET_KEY=your-256-bit-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# MinIO
MINIO_ACCESS_KEY=minio_access_key
MINIO_SECRET_KEY=minio_secret_key
MINIO_BUCKET=cis-documents

# Redis
REDIS_URL=redis://redis:6379/0

# Email (optionnel)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=email_password
```

---

## 8. Monitoring et Logs

### 8.1 Logs structurés

```python
# Configuration logging JSON
import structlog

logger = structlog.get_logger()
logger.info("beneficiary_created", beneficiary_id=123, user_id=1)
```

### 8.2 Healthchecks

```
GET /health          # Statut général
GET /health/db       # Connexion BDD
GET /health/redis    # Connexion Redis
```

### 8.3 Métriques Prometheus

```
GET /metrics

# Métriques exposées
http_requests_total
http_request_duration_seconds
db_connections_active
```
