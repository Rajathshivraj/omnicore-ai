from enum import StrEnum


class RoleSlug(StrEnum):
    CUSTOMER = "customer"
    INVENTORY_MANAGER = "inventory_manager"
    WAREHOUSE_MANAGER = "warehouse_manager"
    ADMIN = "admin"


class Permission(StrEnum):
    VIEW_PRODUCTS = "products:view"
    MANAGE_PRODUCTS = "products:manage"
    VIEW_INVENTORY = "inventory:view"
    MANAGE_INVENTORY = "inventory:manage"
    CREATE_ORDERS = "orders:create"
    VIEW_OWN_ORDERS = "orders:view_own"
    VIEW_ALL_ORDERS = "orders:view_all"
    MANAGE_FULFILLMENT = "fulfillment:manage"
    VIEW_ANALYTICS = "analytics:view"
    VIEW_FORECASTS = "forecasts:view"
    REVIEW_FORECASTS = "forecasts:review"
    VIEW_AI_INSIGHTS = "ai_insights:view"
    REVIEW_AI_INSIGHTS = "ai_insights:review"
    MANAGE_USERS = "users:manage"
    FULL_ACCESS = "system:full_access"


ROLE_PERMISSIONS: dict[RoleSlug, set[Permission]] = {
    RoleSlug.CUSTOMER: {
        Permission.VIEW_PRODUCTS,
        Permission.CREATE_ORDERS,
        Permission.VIEW_OWN_ORDERS,
    },
    RoleSlug.INVENTORY_MANAGER: {
        Permission.VIEW_PRODUCTS,
        Permission.MANAGE_PRODUCTS,
        Permission.VIEW_INVENTORY,
        Permission.MANAGE_INVENTORY,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_FORECASTS,
        Permission.REVIEW_FORECASTS,
        Permission.VIEW_AI_INSIGHTS,
        Permission.REVIEW_AI_INSIGHTS,
    },
    RoleSlug.WAREHOUSE_MANAGER: {
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_ALL_ORDERS,
        Permission.MANAGE_FULFILLMENT,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_AI_INSIGHTS,
        Permission.REVIEW_AI_INSIGHTS,
    },
    RoleSlug.ADMIN: {Permission.FULL_ACCESS},
}
