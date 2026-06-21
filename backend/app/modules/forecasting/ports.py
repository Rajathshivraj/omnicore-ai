from typing import Protocol
from uuid import UUID


class ForecastProvider(Protocol):
    async def generate_for_product(self, product_id: UUID) -> object:
        """Generate a forecast result for a product through a future AI adapter."""
