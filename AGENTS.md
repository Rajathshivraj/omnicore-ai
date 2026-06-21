# OmniCore AI Agent Manual

This file is the permanent instruction manual for coding agents working on OmniCore AI.

<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes - APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Product Context

OmniCore AI is an AI-powered Commerce & Operations Intelligence Platform for retailers. The platform helps teams manage products, inventory, orders, fulfillment, analytics, forecasting, and decision intelligence.

The MVP serves four roles:

- Customer
- Inventory Manager
- Warehouse Manager
- Admin

Every implementation decision must support the MVP before future platform expansion.

## Non-Negotiable Constraints

- Build the MVP first.
- Do not over-engineer.
- Do not introduce microservices.
- Use a modular monolith architecture for the backend.
- Keep frontend and backend separate.
- Prioritize maintainability, readability, and predictable behavior.
- Prefer reusable components and shared primitives over repeated one-off UI.
- Use strict TypeScript.
- Use production-grade folder structures.
- Keep security, authorization, validation, and observability in the first implementation, but avoid enterprise complexity until it is needed.

## Required Stack

Frontend:

- Next.js 16
- TypeScript
- TailwindCSS
- shadcn/ui
- lucide-react for icons

Backend:

- FastAPI
- Python
- Modular monolith package layout

Database:

- PostgreSQL

AI:

- Phi-3 for local or hosted LLM inference
- Retrieval augmented generation using ChromaDB
- Statistical demand forecasting for the MVP with a clear LSTM extension path

Deployment:

- AWS
- Prefer containerized services for the frontend and backend.
- Prefer managed PostgreSQL for production.

## Documentation To Read Before Coding

Before changing frontend code, read the relevant local Next.js 16 guide under `node_modules/next/dist/docs/`. At minimum:

- Project structure: `node_modules/next/dist/docs/01-app/01-getting-started/02-project-structure.md`
- Server and Client Components: `node_modules/next/dist/docs/01-app/01-getting-started/05-server-and-client-components.md`
- Data fetching: `node_modules/next/dist/docs/01-app/01-getting-started/06-fetching-data.md`
- Route handlers: `node_modules/next/dist/docs/01-app/01-getting-started/15-route-handlers.md`
- Deployment: `node_modules/next/dist/docs/01-app/01-getting-started/17-deploying.md`

Read more specific docs when touching metadata, images, caching, forms, authentication, routing, or navigation behavior.

## Architecture Direction

Use a separated frontend and backend:

- Frontend owns presentation, interaction, client-side UX state, and calls backend APIs.
- Backend owns business rules, authorization, persistence, AI orchestration, forecasting jobs, and integrations.
- PostgreSQL is the source of truth for commerce and operations data.
- ChromaDB stores embeddings and retrieved operational knowledge.
- AI features must be optional from the perspective of core workflows. Product, inventory, order, and fulfillment workflows must remain usable if AI inference is degraded.

Use a modular monolith backend organized by domain modules, not by technical layers alone. Modules should include products, inventory, orders, fulfillment, analytics, forecasting, decision intelligence, users, auth, and shared platform concerns.

Do not create microservices, event buses, distributed sagas, or complex platform abstractions for the MVP.

## Frontend Rules

- Use the App Router under `src/app`.
- Keep route files focused on routing, data loading, metadata, and composition.
- Put shared UI in `src/components`.
- Put shadcn primitives in `src/components/ui`.
- Put feature-level components in `src/features/<feature>`.
- Put shared utilities in `src/lib`.
- Use Server Components by default.
- Add `"use client"` only for components that need state, event handlers, effects, browser APIs, or client-only hooks.
- Keep client component boundaries small to avoid unnecessary JavaScript.
- Pass only serializable props from Server Components to Client Components.
- Do not put secrets, database clients, or privileged API logic in client components.
- Use `server-only` for server-only frontend modules when secrets or privileged server logic are present.
- Use route groups for organization when they do not affect URLs.
- Do not place a `route.ts` file at the same segment level as a `page.tsx`.
- Use `loading.tsx`, `error.tsx`, and meaningful empty states for operational workflows.
- Keep strict TypeScript types. Avoid `any` unless a short comment explains why it is unavoidable.
- Use zod or an equivalent schema validator at API boundaries when added to the project.

Recommended frontend structure:

```text
src/
  app/
    (auth)/
    (dashboard)/
    api/
    layout.tsx
    page.tsx
  components/
    ui/
    layout/
    data-display/
    forms/
  features/
    products/
    inventory/
    orders/
    fulfillment/
    analytics/
    forecasting/
    decision-intelligence/
  hooks/
  lib/
    api/
    auth/
    config/
    utils.ts
  types/
```

## Backend Rules

Use FastAPI as a modular monolith. Keep modules cohesive and explicit.

Recommended backend structure:

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      logging.py
      errors.py
    db/
      session.py
      migrations/
    modules/
      auth/
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
      rag/
      forecasting/
    shared/
      schemas/
      pagination.py
      permissions.py
  tests/
```

Backend expectations:

- Keep business logic out of route handlers.
- Use service classes or use-case functions for domain workflows.
- Use repository/data-access boundaries where they reduce duplication or protect business logic from persistence details.
- Validate all request payloads with Pydantic models.
- Enforce authorization in backend APIs, not only in the UI.
- Use database transactions around multi-step writes.
- Keep AI orchestration behind backend interfaces.
- Return stable, typed API contracts for the frontend.
- Avoid background infrastructure until required; use simple scheduled jobs or worker processes for MVP forecasting and indexing.

## Domain Boundaries

Products:

- Product catalog, SKUs, categories, attributes, pricing metadata, and active/inactive lifecycle.

Inventory:

- Stock levels, reservations, reorder thresholds, movements, adjustments, and low-stock alerts.

Orders:

- Customer orders, order lines, status transitions, payment status metadata, and order history.

Fulfillment:

- Pick, pack, ship, warehouse assignment, shipment status, and exception handling.

Analytics:

- Operational KPIs, dashboards, trends, and role-specific summaries.

Forecasting:

- Demand history, statistical forecasting outputs, confidence intervals, replenishment signals, and forecast review.

Decision Intelligence:

- AI recommendations, RAG answers, anomaly explanations, action suggestions, and decision audit trail.

## Security And Permissions

The MVP must support role-based access control:

- Customer: view own orders and customer-facing product/order information.
- Inventory Manager: manage products, inventory counts, stock movements, and replenishment workflows.
- Warehouse Manager: manage fulfillment queues, picking, packing, shipping, and warehouse exceptions.
- Admin: manage users, roles, system settings, and all operational data.

Rules:

- Never trust role or ownership information from the client.
- Enforce permissions on every backend route.
- Keep audit fields for sensitive operational mutations.
- Do not log secrets, tokens, credentials, or full customer personal data.
- Use environment variables for configuration and secrets.
- Do not commit `.env` files.

## AI Implementation Rules

- AI must assist operational decisions; it must not silently mutate critical business data.
- Store AI recommendations with source inputs, confidence when available, timestamp, and review status.
- RAG responses must cite or expose the retrieved operational sources used to produce an answer.
- Forecasting outputs must include model version and generation time.
- Keep deterministic fallbacks for core screens when AI systems are unavailable.
- Avoid premature model platform abstractions. Implement the simplest interface that can support Phi-3, ChromaDB retrieval, and future LSTM forecasts.

## UI And UX Direction

OmniCore AI is an operational SaaS product. It should feel calm, dense, legible, and efficient.

- Favor dashboard layouts, tables, filters, drawers, tabs, and concise detail pages.
- Avoid marketing-style hero sections inside the application.
- Avoid decorative gradients, oversized cards, and purely ornamental visuals.
- Use icons for recognizable actions.
- Use clear loading, empty, error, and success states.
- Make role-specific workflows fast to scan and safe to execute.
- Design for repeated daily usage by operations teams.

See `docs/UI_GUIDELINES.md` for the detailed product UI guidance.

## Testing And Quality

Before completing a code change, run the most relevant checks available:

- `npm run lint` for frontend linting.
- `npm run build` for production frontend build validation when frontend behavior changes.
- Backend tests once the backend exists.
- Type checks and unit tests for modules with business rules.

Add focused tests for:

- Permission-sensitive behavior.
- Inventory and order state transitions.
- Forecasting data transformations.
- AI recommendation persistence and source handling.
- API contract behavior used by the frontend.

## Implementation Style

- Make small, coherent changes.
- Prefer explicit names over clever abstractions.
- Keep functions short enough to read without jumping across many files.
- Do not add libraries unless they solve a real current problem.
- Do not introduce shared frameworks before two or more modules need the same pattern.
- Preserve existing user changes in the working tree.
- Update documentation when architecture, workflows, or public contracts change.

## Definition Of Done

A task is done when:

- It satisfies the requested behavior.
- It respects the architecture and MVP constraints.
- It has appropriate validation, error handling, and permissions.
- It passes the relevant local checks, or any skipped checks are clearly explained.
- The code is readable enough for the next agent or engineer to continue safely.
