from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, ClassVar, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Reusable async SQLAlchemy repository helpers.

    Repositories intentionally contain persistence mechanics only. Business
    rules, permission decisions, and workflow state transitions belong in
    services.
    """

    model_class: ClassVar[type[Any]]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def base_statement(self, *, include_deleted: bool = False) -> Select[tuple[ModelT]]:
        statement = select(self.model_class)
        if not include_deleted and hasattr(self.model_class, "deleted_at"):
            statement = statement.where(self.model_class.deleted_at.is_(None))
        return statement

    async def get_by_id(
        self,
        entity_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ModelT | None:
        statement = self.base_statement(include_deleted=include_deleted).where(
            self.model_class.id == entity_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[ModelT]:
        statement = (
            self.base_statement(include_deleted=include_deleted)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def count(self, *, include_deleted: bool = False) -> int:
        return await self.count_for_statement(
            self.base_statement(include_deleted=include_deleted)
        )

    async def count_for_statement(self, statement: Select[tuple[ModelT]]) -> int:
        statement = select(func.count()).select_from(
            statement.order_by(None).limit(None).offset(None).subquery()
        )
        result = await self.session.execute(statement)
        return int(result.scalar_one())

    async def create(self, data: dict[str, Any]) -> ModelT:
        entity = self.model_class(**data)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT, data: dict[str, Any]) -> ModelT:
        for field, value in data.items():
            setattr(entity, field, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def soft_delete(
        self,
        entity: ModelT,
        *,
        deleted_by_id: UUID | None = None,
    ) -> ModelT:
        if hasattr(entity, "deleted_at"):
            setattr(entity, "deleted_at", datetime.now(UTC))
        if hasattr(entity, "deleted_by_id"):
            setattr(entity, "deleted_by_id", deleted_by_id)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def hard_delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()
