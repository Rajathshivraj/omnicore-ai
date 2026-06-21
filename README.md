# OmniCore AI

OmniCore AI is a portfolio MVP for an AI-assisted commerce and operations platform. It uses a Next.js frontend and a FastAPI modular-monolith backend with PostgreSQL as the system of record.

This project is intended to be portfolio/interview ready, not production ready.

## Current Capabilities

- Customer and operations portals.
- JWT login through the backend.
- HttpOnly cookie auth proxy in the Next.js app.
- Role-aware operations navigation.
- Backend RBAC using seeded role permissions with static MVP fallback.
- Products, inventory, orders, fulfillment, forecasting, analytics, and AI insight APIs.
- Inventory reservation on order creation.
- Inventory release on order cancellation.
- Inventory movement ledger for adjustments, reservations, and releases.
- Baseline Alembic schema migration.
- Idempotent seed system for roles, demo users, demo product, and inventory.
- ChromaDB document indexing endpoint and RAG answer persistence through `AIInsight`.
- Statistical demand forecasting with honest model metadata.

## Demo Accounts

Seeded users use the password `Password123!`.

| Role | Email |
| --- | --- |
| Admin | `admin@omnicore.local` |
| Inventory Manager | `inventory@omnicore.local` |
| Warehouse Manager | `warehouse@omnicore.local` |
| Customer | `customer@omnicore.local` |

## Local Docker Setup

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/v1`
- ChromaDB: `http://localhost:8001`
- PostgreSQL: `localhost:5432`

The backend container runs:

```bash
backend/scripts/init-db.sh
backend/scripts/seed-db.sh
backend/scripts/start-backend.sh
```

See `docs/DEPLOYMENT.md` for the complete portable deployment workflow.

## Manual Backend Setup

From `backend/`:

```bash
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

Required environment variables are documented in `backend/.env.example`.

## Manual Frontend Setup

```bash
npm install
npm run dev
```

Set:

```bash
OMNICORE_API_BASE_URL=http://localhost:8000/api/v1
```

## Important Limitations

- Not production ready.
- Refresh tokens are JWT-based and not yet persisted/revocable.
- Forecasting is statistical Holt-style smoothing, not an LSTM model.
- RAG supports ChromaDB indexing and retrieval, but does not yet include a full document management UI.
- Analytics are MVP summaries, not a BI layer.
- Docker Compose is suitable for local/staging-style validation, not hardened AWS production.

## Recommended Checks

Frontend:

```bash
npm run lint
npm run build
```

Backend:

```bash
ruff check backend
pytest backend/tests
```

In this environment, `npm` and Python availability may depend on local PATH configuration.
