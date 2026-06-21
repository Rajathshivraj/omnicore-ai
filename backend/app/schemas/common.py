from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiMessage(BaseModel):
    message: str


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


class BaseReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
