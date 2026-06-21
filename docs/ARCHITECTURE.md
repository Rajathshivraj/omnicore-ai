# Architecture

## Architecture Summary

OmniCore AI uses a separated frontend and backend with a modular monolith backend.

The frontend is a Next.js 16 application responsible for presentation, routing, interaction, and calling backend APIs. The backend is a FastAPI application responsible for business rules, persistence, authorization, AI orchestration, forecasting, and integrations. PostgreSQL is the operational source of truth. ChromaDB supports retrieval augmented generation. Phi-3 and LSTM forecasting are integrated behind backend interfaces.

This architecture is intentionally conservative for the MVP. It avoids microservices while preserving clear module boundaries that can support future extraction only if real scale or organizational needs justify it.

## High-Level System

```text
User Browser
  |
  v
Next.js 16 Frontend
  |
  v
FastAPI Backend
  |
  +--> PostgreSQL
  +--> ChromaDB
  +--> Phi-3 Inference Runtime
  +--> Forecasting Runtime
```

## Key Decisions

### Modular Monolith Backend

Use one deployable FastAPI backend with domain modules. This keeps development velocity high, transactions simple, and operational overhead low for the MVP.

Do not split products, inventory, orders, fulfillment, analytics, forecasting, or AI into separate services during the MVP.

### Separate Frontend And Backend

The frontend and backend should be independent applications. The frontend should not directly connect to PostgreSQL, ChromaDB, or model runtimes. All privileged operations go through the backend API.

### PostgreSQL As Source Of Truth

PostgreSQL stores operational data including users, products, inventory, orders, fulfillment, forecasts, recommendations, and audit events.

### ChromaDB For Retrieval

ChromaDB stores embeddings and metadata for operational knowledge used by RAG. It is not the source of truth for transactional commerce data.

### AI Behind Interfaces

Phi-3, RAG, and forecasting are behind backend interfaces so core workflows are not tightly coupled to a specific runtime implementation. The current MVP uses statistical demand forecasting; an LSTM runtime can replace that adapter later when trained model artifacts exist.

## Frontend Architecture

### Framework

- Next.js 16
- App Router under `src/app`
- TypeScript with strict mode
- TailwindCSS
- shadcn/ui

### Next.js 16 Notes

Agents must read relevant local documentation in `node_modules/next/dist/docs/` before changing frontend code. This project uses Next.js 16.2.9, and its conventions may differ from older Next.js versions.

Important local docs:

- Project structure: `01-app/01-getting-started/02-project-structure.md`
- Server and Client Components: `01-app/01-getting-started/05-server-and-client-components.md`
- Fetching data: `01-app/01-getting-started/06-fetching-data.md`
- Route handlers: `01-app/01-getting-started/15-route-handlers.md`
- Deployment: `01-app/01-getting-started/17-deploying.md`

### Recommended Frontend Structure

```text
src/
  app/
    (auth)/
      login/
        page.tsx
    (dashboard)/
      dashboard/
        page.tsx
      products/
        page.tsx
        [productId]/
          page.tsx
      inventory/
        page.tsx
      orders/
        page.tsx
        [orderId]/
          page.tsx
      fulfillment/
        page.tsx
      analytics/
        page.tsx
      forecasting/
        page.tsx
      decision-intelligence/
        page.tsx
      layout.tsx
    layout.tsx
    page.tsx
  components/
    ui/
    layout/
    data-display/
    forms/
    feedback/
  features/
    products/
      components/
      hooks/
      types.ts
    inventory/
    orders/
    fulfillment/
    analytics/
    forecasting/
    decision-intelligence/
  lib/
    api/
      client.ts
      errors.ts
    auth/
    config/
    utils.ts
  types/
```

### Frontend Principles

- Server Components by default.
- Client Components only for state, events, effects, browser APIs, or client-only hooks.
- Small client boundaries.
- Typed API clients.
- Reusable table, filter, form, stat, and status components.
- Route groups for organization without changing URLs.
- Meaningful loading, empty, and error states.
- No secrets in client code.

### API Communication

The frontend should call the FastAPI backend through a typed API client. Backend base URLs should come from environment configuration.

Use consistent patterns for:

- Authentication headers or cookies
- Pagination
- Sorting
- Filtering
- Error mapping
- Request cancellation where relevant
- Typed response parsing

## Backend Architecture

### Framework

- FastAPI
- Python
- Pydantic for schemas
- SQLAlchemy or SQLModel for persistence when selected
- Alembic for migrations
- PostgreSQL driver appropriate to the ORM choice

### Recommended Backend Structure

```text
backend/
  pyproject.toml
  app/
    main.py
    core/
      config.py
      security.py
      logging.py
      errors.py
      permissions.py
    db/
      session.py
      base.py
      migrations/
    modules/
      auth/
        router.py
        schemas.py
        service.py
      users/
      products/
      inventory/
      orders/
      fulfillment/
      analytics/
      forecasting/
      decision_intelligence/
    ai/
      llm/
        phi3_client.py
        service.py
      rag/
        embeddings.py
        retrieval.py
        indexing.py
      forecasting/
        lstm.py
        service.py
    shared/
      pagination.py
      time.py
      identifiers.py
  tests/
```

### Backend Layering

Routers:

- Define HTTP endpoints.
- Validate request and response models.
- Delegate to services.
- Avoid business logic.

Services:

- Own business workflows.
- Enforce domain rules.
- Coordinate repositories and AI interfaces.
- Control transactions through explicit boundaries.

Repositories:

- Encapsulate persistence queries where useful.
- Keep query behavior reusable and testable.
- Avoid leaking ORM details across modules.

Schemas:

- Define API input and output contracts.
- Keep internal models separate from public response shapes when needed.

## Domain Modules

### Auth And Users

Responsibilities:

- Login and current user context
- Password or token strategy
- Role assignment
- Permission checks
- Admin user management

### Products

Responsibilities:

- Catalog records
- SKUs
- Categories
- Product lifecycle
- Search and filters

### Inventory

Responsibilities:

- Stock levels
- Reservations
- Adjustments
- Movement history
- Low-stock alerts
- Reorder threshold inputs

### Orders

Responsibilities:

- Order records
- Order lines
- Customer ownership
- Order lifecycle
- Status history

### Fulfillment

Responsibilities:

- Fulfillment queues
- Pick, pack, ship workflow
- Exceptions
- Shipment references
- Warehouse operational status

### Analytics

Responsibilities:

- Role dashboards
- Operational KPIs
- Trends
- Aggregated metrics

### Forecasting

Responsibilities:

- Historical demand preparation
- LSTM inference
- Forecast persistence
- Forecast review data
- Replenishment signals

### Decision Intelligence

Responsibilities:

- AI recommendations
- RAG question answering
- Recommendation lifecycle
- Retrieved source references
- Human review audit trail

## Data Architecture

### PostgreSQL

PostgreSQL stores:

- Users and roles
- Products and SKUs
- Inventory and movement history
- Orders and fulfillment records
- Forecast outputs
- Recommendations
- Knowledge document metadata
- Audit events

### ChromaDB

ChromaDB stores:

- Embeddings
- Chunk text
- Source references
- Metadata needed for retrieval

Transactional updates should not rely on ChromaDB. If ChromaDB is unavailable, core commerce workflows must still function.

### Data Modeling Rules

- Use stable identifiers.
- Include created and updated timestamps on persistent entities.
- Include status histories where workflow traceability matters.
- Add audit events for sensitive mutations.
- Use database constraints for uniqueness and referential integrity.
- Add indexes for common list filters and joins.

## AI Architecture

### RAG Flow

```text
Knowledge Source
  -> Chunking
  -> Embedding
  -> ChromaDB
  -> Retrieval
  -> Prompt Assembly
  -> Phi-3
  -> Response With Sources
```

RAG responses must preserve source references so users can inspect the basis for an answer.

### Forecasting Flow

```text
Historical Orders / Demand
  -> Feature Preparation
  -> Statistical Forecast Adapter
  -> Forecast Persistence
  -> Replenishment Signal
  -> Inventory Manager Review
```

Forecasting outputs should record:

- SKU
- Forecast period
- Predicted demand
- Confidence or uncertainty when available
- Model version
- Generated timestamp

The current implementation is not represented as an LSTM model. It uses deterministic Holt-style smoothing and stores model metadata as `statistical-demand-forecaster` / `holt-linear-v1`.

### Current Implementation Boundaries

- Alembic owns schema creation through a baseline migration.
- `python -m app.db.seed` seeds MVP roles, demo users, and minimal demo catalog data.
- Fulfillment is modeled as queue records linked to orders.
- RAG has document chunking and ChromaDB indexing through the backend. Full document management and advanced embedding governance remain future work.
- Refresh tokens are still stateless JWTs and must be persisted/revocable before production.

### Recommendation Flow

```text
Operational Signals
  -> Rule and Model Evaluation
  -> AI Explanation
  -> Recommendation Record
  -> Human Review
```

Recommendations should never silently mutate inventory, orders, or fulfillment data.

## Security Architecture

### Authentication

The specific authentication implementation can be chosen during backend implementation, but the backend must remain the source of truth for authenticated user context.

### Authorization

Use role-based access control for the MVP:

- Customer
- Inventory Manager
- Warehouse Manager
- Admin

Permissions must be enforced in backend endpoints and services. Frontend route guards improve UX but are not sufficient.

### Secrets

- Use environment variables.
- Never commit secrets.
- Do not expose backend secrets through `NEXT_PUBLIC_` variables.
- Keep model, database, and vector store credentials server-side.

## Deployment Architecture

### AWS MVP Target

Recommended MVP deployment:

- Next.js frontend as a Node.js service or container.
- FastAPI backend as a container.
- PostgreSQL using Amazon RDS.
- ChromaDB hosted as a containerized internal service or managed equivalent if selected.
- Model inference deployed according to cost and performance constraints.
- Object storage using S3 when file or document storage is introduced.

### Environments

Use at least:

- Local
- Staging
- Production

Each environment should have separate databases, secrets, and AI/vector resources.

## Observability

MVP observability should include:

- Structured backend logs.
- Request IDs or correlation IDs.
- Error logs for failed workflows.
- Forecast job status logs.
- AI request success and failure metrics.
- Basic frontend error reporting when selected.

Avoid complex observability platforms until the product needs them.

## Architecture Guardrails

Do:

- Keep modules clear and cohesive.
- Use typed contracts.
- Keep AI optional for core workflow continuity.
- Add tests around permissions and state transitions.
- Choose boring, proven infrastructure.

Do not:

- Introduce microservices.
- Add event streaming for MVP.
- Put business logic in React components.
- Put privileged logic in the frontend.
- Let AI directly mutate critical data.
- Add generic abstraction layers without immediate need.
