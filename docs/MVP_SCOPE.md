# MVP Scope

## MVP Objective

The MVP of OmniCore AI should deliver a usable commerce operations platform for retailers with focused AI assistance. It must cover the daily workflows required to manage products, inventory, orders, fulfillment, analytics, forecasting, and decision intelligence without introducing unnecessary platform complexity.

The MVP must be built as a maintainable foundation for future expansion, not as a throwaway prototype.

## In-Scope Roles

### Customer

Capabilities:

- View available products where customer-facing product visibility is required.
- View own orders.
- View order status and fulfillment updates.
- Access basic account context if authentication is included in the current slice.

### Inventory Manager

Capabilities:

- Create, edit, archive, and view products.
- Manage SKUs, categories, and product attributes.
- View current inventory by SKU and location.
- Record stock adjustments.
- View inventory movement history.
- Set or review reorder thresholds.
- Review low-stock and stockout-risk alerts.
- Review demand forecasts and replenishment suggestions.

### Warehouse Manager

Capabilities:

- View fulfillment queues.
- Review orders ready for picking, packing, and shipping.
- Update fulfillment statuses.
- Record fulfillment exceptions.
- View order details needed for warehouse execution.
- Track operational workload and delayed fulfillment items.

### Admin

Capabilities:

- Manage users.
- Assign roles.
- View system-wide operational data.
- Manage platform-level settings required for the MVP.
- Access audit-relevant operational activity.

## Core MVP Modules

### Authentication And Authorization

Required:

- User login.
- Role-based access control.
- Backend-enforced permissions.
- Protected frontend routes.
- Basic user management for Admins.

Deferred:

- SSO.
- SCIM.
- Complex organization hierarchies.
- Fine-grained custom permission builder.

### Products

Required:

- Product list with search, filtering, and status.
- Product detail page.
- Product create and edit workflows.
- SKU support.
- Category or simple classification support.
- Active, inactive, and archived lifecycle states.

Deferred:

- Complex variant matrix tooling.
- Digital asset management.
- Rich merchandising workflows.
- Marketplace publishing.

### Inventory

Required:

- Inventory by SKU.
- Optional location or warehouse field if needed by fulfillment.
- Stock on hand.
- Reserved stock.
- Available stock.
- Manual stock adjustment with reason.
- Inventory movement history.
- Low-stock thresholds.
- Low-stock alert list.

Deferred:

- Cycle counting workflows.
- Lot, batch, and serial tracking.
- Complex inventory costing.
- Automated supplier purchase orders.

### Orders

Required:

- Order list with status filters.
- Order detail page.
- Order line items.
- Customer ownership.
- Order status lifecycle.
- Admin and operations visibility.
- Customer view restricted to own orders.

Deferred:

- Payment processing.
- Tax calculation.
- Fraud tooling.
- Returns.
- Subscriptions.

### Fulfillment

Required:

- Fulfillment queue.
- Pick, pack, ship status updates.
- Fulfillment exception state.
- Shipment or tracking reference field.
- Warehouse Manager workflow views.

Deferred:

- Carrier label purchasing.
- Warehouse device scanning.
- Route optimization.
- Robotics or hardware integrations.

### Analytics

Required:

- Dashboard summaries by role.
- Product count, low-stock count, open orders, fulfillment backlog.
- Sales/order trend placeholders or basic charts when data exists.
- Operational exceptions summary.

Deferred:

- Full BI builder.
- Custom report designer.
- Embedded semantic layer.
- Cross-channel attribution.

### Forecasting

Required:

- Historical demand input structure.
- Statistical forecasting pipeline with an adapter boundary for future LSTM replacement.
- Forecast output by SKU and period.
- Confidence or uncertainty field when available.
- Forecast generated timestamp and model version.
- Replenishment signal derived from forecast and current inventory.

Deferred:

- Automated model retraining interface.
- Advanced scenario simulation.
- Multi-model comparison UI.
- Supplier lead-time optimization beyond simple MVP assumptions.

### Decision Intelligence

Required:

- AI-generated recommendations for inventory and fulfillment risks.
- RAG question answering over operational knowledge and selected business data.
- Clear source references for RAG responses.
- Recommendation status: new, reviewed, accepted, dismissed.
- Audit trail for human review of recommendations.

Deferred:

- Autonomous write actions.
- Natural-language workflow execution.
- Complex policy engine.
- Multi-agent orchestration.

## Core Workflows

### Inventory Replenishment Review

1. Inventory Manager opens inventory dashboard.
2. System highlights low-stock and forecasted stockout risk.
3. Inventory Manager reviews forecast and supporting data.
4. AI recommendation explains why the SKU needs attention.
5. Inventory Manager marks recommendation as reviewed or accepted.

### Order Fulfillment

1. Warehouse Manager opens fulfillment queue.
2. System shows orders ready to pick, pack, or ship.
3. Warehouse Manager updates status as work progresses.
4. Exceptions are captured with reason and notes.
5. Dashboard reflects backlog and delayed items.

### Admin User Management

1. Admin views users.
2. Admin creates or updates a user.
3. Admin assigns one of the MVP roles.
4. Backend enforces role permissions immediately.

### Customer Order Tracking

1. Customer logs in.
2. Customer views their order history.
3. Customer opens an order detail page.
4. Customer sees current order and fulfillment status.

## MVP Data Entities

Initial entities:

- User
- Role
- Product
- SKU
- InventoryItem
- InventoryMovement
- Order
- OrderLine
- FulfillmentTask or FulfillmentRecord
- Forecast
- Recommendation
- KnowledgeDocument
- RetrievalChunk
- AuditEvent

## API Scope

The backend API should expose stable endpoints for:

- Authentication and current user context
- User and role management
- Product CRUD
- Inventory list, detail, adjustment, and movement history
- Order list, detail, and status updates
- Fulfillment queue and status updates
- Analytics summaries
- Forecast list and detail
- AI recommendations
- RAG question answering

API responses should be typed, predictable, paginated where needed, and documented as the backend matures.

## Non-Functional Requirements

### Maintainability

- Clear domain modules.
- Small service functions.
- Explicit request and response schemas.
- Reusable UI components.
- Minimal cross-module coupling.

### Security

- Backend-enforced RBAC.
- Secure handling of secrets.
- No privileged data in client bundles.
- Audit events for sensitive mutations.

### Performance

- Paginate large operational lists.
- Avoid loading entire datasets into dashboards.
- Use database indexes for list filters.
- Keep AI and forecasting calls asynchronous or isolated when they are slow.

### Reliability

- Core commerce workflows must work without AI availability.
- AI failures should produce visible, recoverable states.
- Forecast generation should record failure information for operators or admins.

## Explicitly Out Of Scope For MVP

- Microservices
- Distributed event streaming
- Multi-region deployment
- Native mobile apps
- Marketplace seller portal
- Payment gateway integration
- Supplier portal
- Purchase order automation
- Advanced WMS features
- ERP-grade accounting
- Complex tenant customization
- Fully autonomous AI actions

## MVP Release Criteria

The MVP is releasable when:

- All four roles can authenticate and access role-appropriate routes.
- Products, inventory, orders, and fulfillment have complete core workflows.
- Admins can manage users and roles.
- Dashboards show meaningful operational summaries.
- Forecasting outputs can be generated or loaded and reviewed.
- RAG-based question answering can retrieve from indexed operational knowledge.
- AI recommendations can be reviewed and tracked.
- Permissions are enforced on the backend.
- Frontend and backend can be built and deployed separately.
