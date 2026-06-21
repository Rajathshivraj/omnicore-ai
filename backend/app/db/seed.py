from __future__ import annotations

import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.password import hash_password
from app.db.enums import InventoryStatus, ProductStatus, UserStatus
from app.db.session import async_session_factory
from app.modules.inventory.models import Inventory
from app.modules.products.models import Category, Product
from app.modules.shared.permissions import ROLE_PERMISSIONS, RoleSlug
from app.modules.users.models import Role, User

DEMO_PASSWORD = "Password123!"


ROLE_DESCRIPTIONS = {
    RoleSlug.CUSTOMER: "Customer portal access for product browsing and own orders.",
    RoleSlug.INVENTORY_MANAGER: "Manages products, inventory, forecasts, and AI insights.",
    RoleSlug.WAREHOUSE_MANAGER: "Manages fulfillment queues and warehouse exceptions.",
    RoleSlug.ADMIN: "System administrator with full access.",
}

DEMO_USERS = [
    ("customer@omnicore.local", "Aarav Customer", RoleSlug.CUSTOMER),
    ("inventory@omnicore.local", "Isha Inventory", RoleSlug.INVENTORY_MANAGER),
    ("warehouse@omnicore.local", "Kabir Warehouse", RoleSlug.WAREHOUSE_MANAGER),
    ("admin@omnicore.local", "Priya Admin", RoleSlug.ADMIN),
]


async def seed_database() -> None:
    async with async_session_factory() as session:
        roles: dict[RoleSlug, Role] = {}
        for role_slug in RoleSlug:
            result = await session.execute(select(Role).where(Role.slug == role_slug.value))
            role = result.scalar_one_or_none()
            permissions = [permission.value for permission in ROLE_PERMISSIONS[role_slug]]
            if role is None:
                role = Role(
                    name=role_slug.value.replace("_", " ").title(),
                    slug=role_slug.value,
                    description=ROLE_DESCRIPTIONS[role_slug],
                    permissions={"permissions": permissions},
                    is_system=True,
                )
                session.add(role)
                await session.flush()
            else:
                role.permissions = {"permissions": permissions}
                role.description = ROLE_DESCRIPTIONS[role_slug]
                role.is_system = True
            roles[role_slug] = role

        for email, full_name, role_slug in DEMO_USERS:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user is None:
                session.add(
                    User(
                        role_id=roles[role_slug].id,
                        email=email,
                        password_hash=hash_password(DEMO_PASSWORD),
                        full_name=full_name,
                        status=UserStatus.ACTIVE,
                        profile_metadata={},
                    )
                )
            else:
                user.role_id = roles[role_slug].id
                user.status = UserStatus.ACTIVE

        category_result = await session.execute(select(Category).where(Category.slug == "core"))
        category = category_result.scalar_one_or_none()
        if category is None:
            category = Category(
                name="Core",
                slug="core",
                description="Demo operational catalog category.",
                sort_order=0,
                status=ProductStatus.ACTIVE,
            )
            session.add(category)
            await session.flush()

        product_result = await session.execute(
            select(Product).where(Product.sku == "CORE-SHOE-001")
        )
        product = product_result.scalar_one_or_none()
        if product is None:
            product = Product(
                category_id=category.id,
                sku="CORE-SHOE-001",
                name="CoreFlex Running Shoe",
                slug="coreflex-running-shoe",
                description="Demo product used for inventory and forecasting workflows.",
                status=ProductStatus.ACTIVE,
                price_amount=Decimal("89.00"),
                currency="USD",
                cost_amount=Decimal("38.00"),
                image_url=None,
                attributes={"color": "black", "size_run": "standard"},
            )
            session.add(product)
            await session.flush()

        inventory_result = await session.execute(
            select(Inventory).where(
                Inventory.product_id == product.id,
                Inventory.location_code == "default",
            )
        )
        inventory = inventory_result.scalar_one_or_none()
        if inventory is None:
            session.add(
                Inventory(
                    product_id=product.id,
                    location_code="default",
                    stock_on_hand=120,
                    stock_reserved=0,
                    stock_available=120,
                    reorder_point=40,
                    reorder_quantity=60,
                    inventory_status=InventoryStatus.HEALTHY,
                )
            )

        await session.commit()


def main() -> None:
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
