"""Aggregate ORM model imports for Alembic metadata discovery."""

from app.modules.copilot.models import AIInsight
from app.modules.forecasting.models import Forecast
from app.modules.fulfillment.models import FulfillmentRecord
from app.modules.inventory.models import Inventory, InventoryMovement
from app.modules.orders.models import Order, OrderItem
from app.modules.products.models import Category, Product
from app.modules.users.models import Role, User

__all__ = [
    "AIInsight",
    "Category",
    "Forecast",
    "FulfillmentRecord",
    "Inventory",
    "InventoryMovement",
    "Order",
    "OrderItem",
    "Product",
    "Role",
    "User",
]
