from decimal import Decimal

from app.db.enums import FulfillmentStatus, InventoryStatus, OrderStatus
from app.modules.forecasting.repository import ForecastRepository
from app.modules.inventory.repository import InventoryRepository
from app.modules.orders.repository import OrderRepository
from app.modules.products.repository import ProductRepository


class AnalyticsService:
    """Coordinates role-specific dashboards and operational KPI summaries."""

    def __init__(
        self,
        *,
        product_repository: ProductRepository,
        inventory_repository: InventoryRepository,
        order_repository: OrderRepository,
        forecast_repository: ForecastRepository,
    ) -> None:
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
        self.order_repository = order_repository
        self.forecast_repository = forecast_repository

    async def get_summary(self) -> dict[str, int | str]:
        products = await self.product_repository.list_filtered(limit=100)
        inventory = await self.inventory_repository.list_filtered(limit=100)
        orders = await self.order_repository.list_filtered(limit=100)
        forecasts = await self.forecast_repository.list_filtered(limit=100)

        low_stock_statuses = {
            InventoryStatus.LOW_STOCK,
            InventoryStatus.STOCKOUT_RISK,
            InventoryStatus.OUT_OF_STOCK,
        }
        open_statuses = {
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
        }
        backlog_statuses = {
            FulfillmentStatus.READY_TO_PICK,
            FulfillmentStatus.PICKING,
            FulfillmentStatus.EXCEPTION,
        }
        revenue_total = sum((order.total_amount for order in orders), Decimal("0.00"))

        return {
            "product_count": len(products),
            "inventory_records": len(inventory),
            "low_stock_count": sum(
                1
                for item in inventory
                if InventoryStatus(item.inventory_status) in low_stock_statuses
            ),
            "order_count": len(orders),
            "open_order_count": sum(
                1 for order in orders if OrderStatus(order.status) in open_statuses
            ),
            "fulfillment_backlog_count": sum(
                1
                for order in orders
                if FulfillmentStatus(order.fulfillment_status) in backlog_statuses
            ),
            "revenue_total": str(revenue_total),
            "forecasted_demand": sum(forecast.predicted_demand for forecast in forecasts),
        }
