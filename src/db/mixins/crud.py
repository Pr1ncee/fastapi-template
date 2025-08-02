import builtins
import math
from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Select, UnaryExpression, delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import expression
from sqlalchemy.testing.plugin.plugin_base import logging

from src.api.schema.pagination_schema import PaginatedData, PaginationParams
from src.db.db import Base
from src.db.models import BaseModel as DBBaseModel

logger = logging.getLogger(__name__)


class CRUDMixin:
    table: Base = DBBaseModel

    @classmethod
    async def create(
        cls,
        input_data: BaseModel,
        session: AsyncSession,
        http_exc_text: str = "Record with some unique data exists",
    ) -> table | HTTPException:
        try:
            obj = cls.table(**input_data.dict())
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(detail=http_exc_text, status_code=status.HTTP_400_BAD_REQUEST) from IntegrityError
        return obj

    @classmethod
    async def get_paginated_data(
        cls,
        params: PaginationParams,
        query: Select,
        session: AsyncSession,
        is_mapping: bool = False,
        order_by: UnaryExpression = None,
    ) -> PaginatedData | HTTPException:
        try:
            count_query = query.with_only_columns(func.count()).order_by(None)
            res = await session.execute(count_query)
        except Exception as e:
            logger.exception("Invalid input query!", extra={"e": e})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Query error, try again later",
            ) from e
        count = res.scalar()

        total_pages = math.ceil(count / params.size) if params.size else 1
        offset = params.size * (params.page - 1)

        try:
            data_query = query.limit(params.size).offset(offset)
            if order_by is not None:
                data_query = data_query.order_by(order_by)
            res = await session.execute(data_query)

            data = res.mappings().all() if is_mapping else res.scalars().all()
            return PaginatedData(
                items=data,
                page=params.page,
                pages=total_pages,
                size=params.size,
                total=count,
            )

        except Exception as e:
            logger.exception("Invalid input query!", extra={"e": e})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Query error, try again later",
            ) from e

    @classmethod
    async def retrieve(cls, pk: int, session: AsyncSession) -> table | HTTPException:
        query = select(cls.table).where(cls._get_pk_attr() == pk)
        res = await session.execute(query)
        obj = res.scalars().first()
        cls._check_object(obj)
        await session.refresh(obj)
        return obj

    @classmethod
    async def bulk_retrieve(
        cls,
        pks: builtins.list[int],
        session: AsyncSession,
    ) -> Sequence[table] | HTTPException:
        query = select(cls.table).where(cls._get_pk_attr().in_(pks))
        res = await session.execute(query)
        objs = res.scalars().all()
        [cls._check_object(obj) for obj in objs]
        [await session.refresh(obj) for obj in objs]
        return objs

    @classmethod
    async def update(
        cls,
        pk: int,
        input_data: BaseModel,
        session: AsyncSession,
        partial: bool = False,
    ) -> table | HTTPException:
        retrieved_obj = await cls.retrieve(pk, session)
        query = update(cls.table).where(cls._get_pk_attr() == pk).values(**input_data.dict(exclude_unset=partial))
        await cls._execute_commit(query, session)
        return retrieved_obj

    @classmethod
    async def bulk_update(
        cls,
        pks: builtins.list[int],
        input_data: BaseModel,
        session: AsyncSession,
        partial: bool = False,
    ) -> Sequence[table] or HTTPException:
        retrieved_objs = await cls.bulk_retrieve(pks, session)
        query = update(cls.table).where(cls._get_pk_attr().in_(pks)).values(**input_data.dict(exclude_unset=partial))
        await cls._execute_commit(query, session)
        return retrieved_objs

    @classmethod
    async def delete(cls, pk: int, session: AsyncSession, commit: bool = True) -> None:
        await cls.retrieve(pk, session)
        query = delete(cls.table).where(cls._get_pk_attr() == pk)
        await cls._execute_commit(query, session, commit)

    @classmethod
    async def _execute_commit(cls, query: expression, session: AsyncSession, commit: bool = True) -> None:
        await session.execute(query)
        if commit:
            await session.commit()

    @classmethod
    def _get_pk_attr(cls) -> str:
        return getattr(cls.table.__table__.c, cls.table.pk_name())

    @classmethod
    def _check_object(cls, obj: table) -> bool | HTTPException:
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
        return True
