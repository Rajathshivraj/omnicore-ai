# UI Guidelines

## Product UI Direction

OmniCore AI is an operations-focused SaaS application for retail teams. The interface should feel calm, dense, structured, trustworthy, and fast to scan. It should prioritize repeated daily workflows over visual spectacle.

This is not a marketing site. The application should open into useful work surfaces: dashboards, queues, tables, forms, filters, details, and decision panels.

## Design Principles

### Clarity Over Decoration

Use layout, typography, spacing, and status color to clarify operational meaning. Avoid decorative visuals that do not help users make decisions.

### Dense But Legible

Retail operations teams need to scan many products, orders, and alerts. Use compact spacing thoughtfully, but preserve readable typography and clear hierarchy.

### Role-Relevant

Each role should see the information most relevant to their work:

- Customers need order and account clarity.
- Inventory Managers need stock, forecast, and replenishment visibility.
- Warehouse Managers need queue and exception clarity.
- Admins need control, configuration, and oversight.

### Actionable Intelligence

AI recommendations should be presented with context, confidence when available, source references, and clear review actions.

### Safe Operations

Destructive or high-impact actions must be explicit, confirmed when appropriate, and recoverable where possible.

## Visual System

### Tone

The UI should feel:

- Professional
- Practical
- Focused
- Reliable
- Modern but restrained

Avoid:

- Oversized hero sections in authenticated app screens
- Decorative gradient backgrounds
- Excessive card nesting
- One-note color palettes
- Flashy AI visual treatments
- Marketing-style copy inside operational workflows

### Color

Use a neutral base with purposeful accents.

Recommended usage:

- Neutral backgrounds for application surfaces.
- Subtle borders for separation.
- Blue or teal for primary actions and informational states.
- Green for healthy inventory, completed fulfillment, and positive outcomes.
- Amber for warning states such as low stock or delayed fulfillment.
- Red for errors, stockout risk, failed jobs, or destructive actions.
- Purple should be used sparingly for AI-specific affordances if used at all.

Do not let the application become dominated by a single hue family.

### Typography

Use typography to support scanning:

- Page titles should be clear and direct.
- Section headings should be compact.
- Table text should be readable at operational density.
- Avoid display-scale typography inside dashboards and work queues.
- Do not use negative letter spacing.
- Do not scale font size directly with viewport width.

### Spacing And Layout

- Use consistent spacing tokens.
- Use full-width application bands and constrained inner content.
- Avoid putting cards inside cards.
- Use cards for repeated items, compact summaries, and contained tools.
- Prefer tables and split-pane details for operational records.
- Keep filters close to the data they affect.
- Keep primary actions in predictable positions.

## Component Guidelines

### Navigation

Use role-aware navigation. MVP navigation should include only routes relevant to the signed-in role.

Recommended app sections:

- Dashboard
- Products
- Inventory
- Orders
- Fulfillment
- Analytics
- Forecasting
- Decision Intelligence
- Admin

Navigation should make the current section obvious.

### Dashboards

Dashboards should be operational summaries, not decorative overview pages.

Use:

- KPI strips
- Alert lists
- Trend charts
- Work queues
- Exceptions
- AI recommendation summaries

Avoid:

- Large hero copy
- Generic welcome sections
- Empty decorative panels

### Tables

Tables are primary UI for products, inventory, orders, fulfillment queues, forecasts, and recommendations.

Tables should support:

- Search when useful
- Filters
- Sorting where expected
- Pagination
- Status badges
- Row actions
- Empty states
- Loading skeletons

Columns should be chosen for decision-making, not raw data dumping.

### Forms

Forms should be direct and predictable.

Use:

- Clear labels
- Field-level validation
- Helpful error messages
- Required field indicators
- Save and cancel actions
- Confirmation for risky changes

Avoid:

- Multi-step forms unless the workflow truly needs them.
- Hidden validation rules.
- Overly conversational form copy.

### Status Badges

Use status badges consistently.

Examples:

- Product: Active, Inactive, Archived
- Inventory: Healthy, Low Stock, Stockout Risk, Out of Stock
- Order: Pending, Confirmed, Processing, Fulfilled, Cancelled
- Fulfillment: Ready to Pick, Picking, Packed, Shipped, Exception
- Recommendation: New, Reviewed, Accepted, Dismissed
- Forecast Job: Pending, Running, Completed, Failed

### AI Panels

AI surfaces should be useful and accountable.

AI recommendation panels should show:

- Recommendation title
- Operational impact
- Suggested action
- Supporting signals
- Source references for RAG answers
- Confidence or uncertainty when available
- Human review actions

Do not present AI output as unquestionable truth.

### Charts

Use charts for trends and comparisons that are easier to understand visually.

Good chart use cases:

- Demand over time
- Forecast versus actual demand
- Fulfillment backlog trend
- Low-stock count by category
- Orders by status

Avoid chart clutter. If a table communicates the answer better, use a table.

## Interaction Guidelines

### Loading States

Use skeletons for tables, dashboards, and panels. Loading states should preserve layout stability.

### Empty States

Empty states should explain what is absent and provide the next useful action when appropriate.

Examples:

- No products found after filters.
- No fulfillment exceptions.
- No forecasts generated yet.
- No AI recommendations pending review.

### Error States

Errors should be specific and recoverable.

Show:

- What failed.
- Whether data may be stale.
- A retry action when useful.
- A safe fallback view when possible.

### Confirmation

Require confirmation for:

- Archiving products.
- Cancelling orders.
- Large inventory adjustments.
- Dismissing important AI recommendations.
- Role or permission changes.

## Accessibility

MVP UI must include:

- Semantic HTML.
- Keyboard-accessible controls.
- Visible focus states.
- Sufficient color contrast.
- Labels for inputs.
- ARIA only when semantic HTML is insufficient.
- Icons paired with accessible labels or tooltips where meaning is not obvious.

Do not rely on color alone for operational status.

## Responsive Behavior

The primary target is desktop and laptop operations usage, but screens must remain usable on tablets and mobile widths.

Guidelines:

- Tables may become horizontally scrollable when necessary.
- Important actions should remain reachable.
- Summary cards can collapse into a single column.
- Filters can move into drawers on smaller screens.
- Text must not overflow controls or overlap adjacent content.

## shadcn/ui Usage

Use shadcn/ui as the component foundation. Keep primitives consistent and compose feature-specific components from them.

Expected primitives:

- Button
- Input
- Select
- Checkbox
- Dialog
- Sheet
- Tabs
- Table
- Badge
- Dropdown Menu
- Toast or Sonner
- Tooltip
- Card for repeated summaries only

Use lucide-react icons for recognizable actions.

## Role-Specific UI Priorities

### Customer

Prioritize:

- Order history
- Order status
- Simple product/order details

Avoid exposing internal operations details.

### Inventory Manager

Prioritize:

- Inventory health
- Low-stock alerts
- Product/SKU accuracy
- Forecast review
- Replenishment recommendations

### Warehouse Manager

Prioritize:

- Fulfillment queue
- Delayed items
- Exceptions
- Fast status updates
- Order detail needed for execution

### Admin

Prioritize:

- User management
- Role assignment
- System-level visibility
- Audit-sensitive actions

## Copy Guidelines

Use clear operational language.

Prefer:

- "Low stock"
- "Ready to pick"
- "Forecasted demand"
- "Review recommendation"
- "Inventory adjustment"

Avoid:

- Vague AI language like "magic insights"
- Marketing claims
- Long instructional text inside workflows
- Cute or overly casual microcopy for critical operations

## UI Definition Of Done

A UI change is complete when:

- It supports the relevant role workflow.
- It is responsive enough for supported viewports.
- Loading, empty, and error states are handled.
- Text does not overflow or overlap.
- Actions are accessible by keyboard.
- Visual styling matches the operational SaaS direction.
- Reusable components are used where appropriate.

