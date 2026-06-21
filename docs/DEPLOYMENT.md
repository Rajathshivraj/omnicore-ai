# Deployment Guide

OmniCore AI is packaged for portable container-based deployment. The default workflow targets local development and staging-style validation with Docker Compose.

## Prerequisites

- Docker Engine with Docker Compose v2.
- Git.
- Ports `3000`, `8000`, `8001`, and `5432` available, unless overridden in `.env`.

## Environment Setup

Copy the root environment template:

```bash
cp .env.example .env
```

For a default local run, no value must be changed. Before sharing a deployment or exposing it outside your machine, set a unique `OMNICORE_JWT_SECRET_KEY`.

Important variables:

| Variable | Purpose |
| --- | --- |
| `FRONTEND_PORT` | Host port for the Next.js frontend. |
| `BACKEND_PORT` | Host port for the FastAPI backend. |
| `POSTGRES_PORT` | Host port for PostgreSQL. |
| `OMNICORE_DATABASE_URL` | Backend database connection string. |
| `OMNICORE_JWT_SECRET_KEY` | JWT signing secret. |
| `OMNICORE_RUN_MIGRATIONS` | Runs Alembic migrations on backend startup when `true`. |
| `OMNICORE_SEED_DATABASE` | Runs the idempotent seed workflow on backend startup when `true`. |

## Start The Stack

```bash
docker compose up --build
```

Startup order:

1. PostgreSQL starts and passes `pg_isready`.
2. ChromaDB starts.
3. Backend runs migrations with `backend/scripts/init-db.sh`.
4. Backend seeds roles, demo users, and demo catalog data with `backend/scripts/seed-db.sh`.
5. Backend starts FastAPI and passes `/api/v1/health/readiness`.
6. Frontend starts after the backend is healthy.

## Access Points

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:3000` |
| Backend API | `http://localhost:8000/api/v1` |
| Backend health | `http://localhost:8000/api/v1/health` |
| Backend readiness | `http://localhost:8000/api/v1/health/readiness` |
| Frontend health | `http://localhost:3000/api/health` |
| ChromaDB | `http://localhost:8001` |
| PostgreSQL | `localhost:5432` |

PostgreSQL defaults:

```text
database: omnicore
user: omnicore
password: omnicore
```

## Demo Accounts

All seeded users use `Password123!`.

| Role | Email |
| --- | --- |
| Admin | `admin@omnicore.local` |
| Inventory Manager | `inventory@omnicore.local` |
| Warehouse Manager | `warehouse@omnicore.local` |
| Customer | `customer@omnicore.local` |

## Database Workflows

Run migrations manually:

```bash
docker compose run --rm backend /app/scripts/init-db.sh
```

Run seed data manually:

```bash
docker compose run --rm backend /app/scripts/seed-db.sh
```

Reset local data:

```bash
docker compose down -v
docker compose up --build
```

## Health Checks

Docker Compose defines healthchecks for:

- PostgreSQL: `pg_isready`.
- Backend: `GET /api/v1/health/readiness`, including a database connectivity check.
- Frontend: `GET /api/health`.

Inspect status:

```bash
docker compose ps
```

## Notes

- The Compose setup is portable and suitable for local or staging-style validation.
- It is not a hardened production deployment.
- ChromaDB and PostgreSQL use named Docker volumes.
- AI model inference depends on `OMNICORE_PHI3_ENDPOINT_URL` when a Phi-3 runtime is available.
