from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.modules.admin.router import router as admin_router
from app.modules.analytics.router import router as analytics_router
from app.modules.auth.router import router as auth_router
from app.modules.copilot.router import router as copilot_router
from app.modules.forecasting.router import router as forecasting_router
from app.modules.fulfillment.router import router as fulfillment_router
from app.modules.inventory.router import router as inventory_router
from app.modules.orders.router import router as orders_router
from app.modules.products.router import router as products_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
api_router.include_router(inventory_router)
api_router.include_router(orders_router)
api_router.include_router(fulfillment_router)
api_router.include_router(analytics_router)
api_router.include_router(forecasting_router)
api_router.include_router(copilot_router)
api_router.include_router(admin_router)
