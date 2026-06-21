from enum import StrEnum

from sqlalchemy import Enum as SQLEnum


def enum_type(enum_class: type[StrEnum], *, name: str, length: int = 32) -> SQLEnum:
    return SQLEnum(
        enum_class,
        name=name,
        native_enum=False,
        length=length,
        validate_strings=True,
        values_callable=lambda values: [item.value for item in values],
    )


class UserStatus(StrEnum):
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ProductStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class InventoryStatus(StrEnum):
    HEALTHY = "healthy"
    LOW_STOCK = "low_stock"
    STOCKOUT_RISK = "stockout_risk"
    OUT_OF_STOCK = "out_of_stock"


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class FulfillmentStatus(StrEnum):
    READY_TO_PICK = "ready_to_pick"
    PICKING = "picking"
    PACKED = "packed"
    SHIPPED = "shipped"
    EXCEPTION = "exception"


class PaymentStatus(StrEnum):
    UNPAID = "unpaid"
    AUTHORIZED = "authorized"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class ForecastStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AIInsightType(StrEnum):
    RECOMMENDATION = "recommendation"
    RAG_ANSWER = "rag_answer"
    ANOMALY = "anomaly"
    FORECAST_EXPLANATION = "forecast_explanation"


class ReviewStatus(StrEnum):
    NEW = "new"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
