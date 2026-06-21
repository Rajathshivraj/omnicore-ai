from pydantic import BaseModel


class KpiResponse(BaseModel):
    label: str
    value: str
    change: str | None = None


class AnalyticsSummaryResponse(BaseModel):
    product_count: int
    inventory_records: int
    low_stock_count: int
    order_count: int
    open_order_count: int
    fulfillment_backlog_count: int
    revenue_total: str
    forecasted_demand: int
