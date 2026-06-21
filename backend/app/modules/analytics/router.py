from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession
from app.modules.analytics.schemas import AnalyticsSummaryResponse
from app.modules.analytics.service import AnalyticsService
from app.modules.auth.dependencies import require_permissions
from app.modules.forecasting.repository import ForecastRepository
from app.modules.inventory.repository import InventoryRepository
from app.modules.orders.repository import OrderRepository
from app.modules.products.repository import ProductRepository
from app.modules.shared.permissions import Permission
from app.modules.users.models import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def get_analytics_service(session: DbSession) -> AnalyticsService:
    return AnalyticsService(
        product_repository=ProductRepository(session),
        inventory_repository=InventoryRepository(session),
        order_repository=OrderRepository(session),
        forecast_repository=ForecastRepository(session),
    )


AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]


@router.get("/summary", response_model=AnalyticsSummaryResponse, summary="Get analytics summary")
async def get_summary(
    service: AnalyticsServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_ANALYTICS))],
) -> dict[str, int | str]:
    return await service.get_summary()
