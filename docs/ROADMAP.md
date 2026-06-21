# Roadmap

## Roadmap Philosophy

OmniCore AI should grow from a focused, reliable MVP into a broader commerce operations intelligence platform. Each phase should add operational value without compromising maintainability.

The roadmap is intentionally staged:

1. Establish the foundation.
2. Deliver core MVP workflows.
3. Add practical intelligence.
4. Harden for production.
5. Expand only after usage proves the need.

## Phase 0: Foundation

Goal: Create the project foundation and align implementation around a clear architecture.

Deliverables:

- Product vision documentation.
- MVP scope documentation.
- Architecture documentation.
- UI guidelines.
- Agent manual.
- Initial frontend structure.
- Initial backend structure.
- Environment configuration strategy.
- Local development workflow.

Exit criteria:

- Future agents and engineers can understand what to build and what to avoid.
- Frontend and backend boundaries are clear.
- MVP constraints are documented.

## Phase 1: Application Shell And Auth

Goal: Create the secure application shell and role-aware navigation.

Deliverables:

- Next.js app shell.
- Login flow.
- Authenticated layout.
- Role-aware navigation.
- Protected frontend routes.
- FastAPI app bootstrap.
- User model.
- Role model.
- Backend authentication.
- Backend RBAC enforcement.
- Admin user management basics.

Exit criteria:

- All MVP roles can authenticate.
- Users can access only role-appropriate routes.
- Backend rejects unauthorized actions.

## Phase 2: Core Commerce Data

Goal: Implement product, inventory, and order foundations.

Deliverables:

- Product CRUD.
- SKU support.
- Product list and detail pages.
- Inventory list.
- Inventory detail.
- Stock adjustment workflow.
- Inventory movement history.
- Order list.
- Order detail.
- Order status lifecycle.
- Customer order visibility restrictions.

Exit criteria:

- Inventory Managers can manage product and inventory basics.
- Customers can view their own orders.
- Admins can oversee operational records.
- Data is persisted in PostgreSQL with migrations.

## Phase 3: Fulfillment Operations

Goal: Support warehouse execution workflows.

Deliverables:

- Fulfillment queue.
- Pick, pack, ship status transitions.
- Fulfillment exception handling.
- Warehouse Manager dashboard.
- Fulfillment status history.
- Basic fulfillment analytics.

Exit criteria:

- Warehouse Managers can run daily fulfillment queues.
- Operational exceptions are visible and trackable.
- Order and fulfillment statuses remain consistent.

## Phase 4: Analytics MVP

Goal: Provide role-specific operational visibility.

Deliverables:

- Admin dashboard.
- Inventory dashboard.
- Warehouse dashboard.
- Customer order summary.
- KPI cards.
- Status distribution charts.
- Low-stock and backlog summaries.
- Basic trend visualizations.

Exit criteria:

- Each role has a useful landing dashboard.
- Operational teams can identify priority work without exporting data.

## Phase 5: Forecasting MVP

Goal: Introduce demand forecasting and replenishment signals.

Deliverables:

- Historical demand data pipeline.
- Statistical forecasting interface with a documented future LSTM replacement path.
- Forecast generation job.
- Forecast persistence.
- Forecast list and detail views.
- Forecast versus inventory comparison.
- Replenishment signal generation.
- Forecast job status tracking.

Exit criteria:

- Inventory Managers can review SKU-level forecasts.
- Forecast outputs include model version and generation time.
- Forecasting failures are visible and do not break core workflows.

## Phase 6: Decision Intelligence MVP

Goal: Add AI-assisted recommendations and RAG question answering.

Deliverables:

- Knowledge document ingestion path.
- Chunking and embedding pipeline.
- ChromaDB retrieval.
- Phi-3-backed RAG response generation.
- Source references in AI answers.
- AI recommendations for stockout risk and fulfillment exceptions.
- Recommendation review workflow.
- Recommendation audit history.

Exit criteria:

- Users can ask operational questions and inspect sources.
- Inventory Managers can review AI replenishment recommendations.
- AI features fail gracefully when unavailable.

## Phase 7: Production Hardening

Goal: Prepare the MVP for controlled production use.

Deliverables:

- Improved test coverage.
- Permission and state transition tests.
- API error consistency.
- Request logging and correlation IDs.
- Deployment pipelines.
- Staging environment.
- Production environment.
- Backup and restore plan.
- Security review.
- Performance review for core list pages.

Exit criteria:

- The system can be deployed to AWS.
- Critical workflows are tested.
- Operational risks are documented.
- MVP can support pilot users.

## Post-MVP Expansion

Potential future investments:

- Purchase order workflows.
- Supplier management.
- Returns and reverse logistics.
- Multi-warehouse balancing.
- Ecommerce platform integrations.
- Carrier integrations.
- Advanced forecasting models.
- Forecast scenario planning.
- Anomaly detection.
- More granular permissions.
- Tenant management if multi-tenant needs are validated.
- Advanced analytics exports.
- Saved reports.
- AI-assisted workflow drafting with human approval.

## Deferred Until Proven Necessary

Avoid these until product usage clearly justifies them:

- Microservices.
- Distributed event streaming.
- Kubernetes-first architecture.
- Complex plugin systems.
- Full workflow automation engine.
- Custom BI builder.
- Multi-region architecture.
- Fine-grained user-defined permission matrices.
- Autonomous AI mutation of operational data.

## Roadmap Success Metrics

Track progress through operational value:

- Time to identify stockout risk.
- Time to process fulfillment queue.
- Number of unresolved fulfillment exceptions.
- Inventory adjustment accuracy.
- Forecast review adoption.
- AI recommendation review rate.
- Reduction in manual reporting.
- Role-specific daily active usage.
