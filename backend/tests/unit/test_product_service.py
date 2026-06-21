from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import NotFoundError
from app.modules.products.service import ProductService


class FakeProductRepository:
    async def create(self, data: dict):
        return SimpleNamespace(id=uuid4(), **data)


class FakeCategoryRepository:
    def __init__(self, exists: bool) -> None:
        self.exists = exists

    async def get_by_id(self, category_id):
        if self.exists:
            return SimpleNamespace(id=category_id)
        return None


@pytest.mark.asyncio
async def test_create_product_requires_existing_category() -> None:
    service = ProductService(
        product_repository=FakeProductRepository(),
        category_repository=FakeCategoryRepository(exists=False),
    )

    with pytest.raises(NotFoundError):
        await service.create_product({"category_id": uuid4(), "sku": "SKU-1"})


@pytest.mark.asyncio
async def test_create_product_delegates_to_repository() -> None:
    category_id = uuid4()
    service = ProductService(
        product_repository=FakeProductRepository(),
        category_repository=FakeCategoryRepository(exists=True),
    )

    product = await service.create_product({"category_id": category_id, "sku": "SKU-1"})

    assert product.category_id == category_id
    assert product.sku == "SKU-1"
