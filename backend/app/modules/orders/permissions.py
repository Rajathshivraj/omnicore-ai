from app.modules.shared.permissions import Permission

REQUIRED_PERMISSIONS = {
    "create_orders": Permission.CREATE_ORDERS,
    "view_own_orders": Permission.VIEW_OWN_ORDERS,
    "view_all_orders": Permission.VIEW_ALL_ORDERS,
    "manage_fulfillment": Permission.MANAGE_FULFILLMENT,
}
