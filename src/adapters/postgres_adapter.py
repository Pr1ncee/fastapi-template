import math
from collections.abc import Sequence
from typing import Generic, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Select, UnaryExpression, delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import expression
from sqlalchemy.testing.plugin.plugin_base import logging

from src.api.schema.pagination_schema import PaginatedData, PaginationParams

logger = logging.getLogger(__name__)

TModel = TypeVar("TModel")
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)


class PostgresAdapter(Generic[TModel, TCreate, TUpdate]):
    def __init__(self, session: AsyncSession, model: TModel) -> None:
        self.session = session
        self.model = model

    async def create(self, input_data: BaseModel) -> TModel | HTTPException:
        try:
            obj = self.model(**input_data.model_dump(exclude_unset=True))
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
        except IntegrityError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Record with some unique data exists",
            ) from e
        return obj

    async def get_paginated_data(
        self,
        params: PaginationParams,
        query: Select,
        is_mapping: bool = False,
        order_by: UnaryExpression = None,
    ) -> PaginatedData | HTTPException:
        try:
            count_query = query.with_only_columns(func.count()).order_by(None)
            res = await self.session.execute(count_query)
        except Exception as e:
            logger.exception("Invalid input query!", extra={"e": e})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Query error, try again later",
            ) from e
        count = res.scalar() if isinstance(res.scalar(), int) else 0

        total_pages = math.ceil(count / params.size) if params.size else 1
        offset = params.size * (params.page - 1)

        try:
            data_query = query.limit(params.size).offset(offset)
            if order_by is not None:
                data_query = data_query.order_by(order_by)
            res = await self.session.execute(data_query)

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

    async def retrieve(self, pk: int) -> TModel | HTTPException:
        query = select(self.model).where(self._get_pk_attr() == pk)
        res = await self.session.execute(query)
        obj = res.scalars().first()
        self._check_object(obj)
        await self.session.refresh(obj)
        return obj

    async def bulk_retrieve(self, pks: Sequence[int]) -> Sequence[TModel] | HTTPException:
        query = select(self.model).where(self._get_pk_attr().in_(pks))
        res = await self.session.execute(query)
        objs = res.scalars().all()
        [self._check_object(obj) for obj in objs]
        [await self.session.refresh(obj) for obj in objs]
        return objs

    async def update(
        self,
        pk: int,
        input_data: BaseModel,
        partial: bool = False,
    ) -> TModel | HTTPException:
        retrieved_obj = await self.retrieve(pk)
        query = update(self.model).where(self._get_pk_attr() == pk).values(**input_data.dict(exclude_unset=partial))
        await self._execute_commit(query)
        return retrieved_obj

    async def bulk_update(
        self,
        pks: Sequence[int],
        input_data: BaseModel,
        partial: bool = False,
    ) -> Sequence[TModel] or HTTPException:
        retrieved_objs = await self.bulk_retrieve(pks)
        query = update(self.model).where(self._get_pk_attr().in_(pks)).values(**input_data.dict(exclude_unset=partial))
        await self._execute_commit(query)
        return retrieved_objs

    async def delete(self, pk: int, commit: bool = True) -> None:
        await self.retrieve(pk)
        query = delete(self.model).where(self._get_pk_attr() == pk)
        await self._execute_commit(query, commit)

    async def _execute_commit(self, query: expression, commit: bool = True) -> None:
        await self.session.execute(query)
        if commit:
            await self.session.commit()

    def _get_pk_attr(self) -> str:
        return getattr(self.model.__table__.c, self.model.pk_name())

    def _check_object(self, obj: TModel) -> bool | HTTPException:
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
        return True
