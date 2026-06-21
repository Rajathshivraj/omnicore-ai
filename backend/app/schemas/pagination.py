from typing import Generic, TypeVar

from pydantic import BaseModel, Field

ItemT = TypeVar("ItemT")


class PageMeta(BaseModel):
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    count: int = Field(ge=0)


class PaginatedResponse(BaseModel, Generic[ItemT]):
    items: list[ItemT]
    meta: PageMeta
