import math
from typing import List, TypeVar, Union

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import delete, desc, select, update, func, Select, UnaryExpression
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import expression
from sqlalchemy.testing.plugin.plugin_base import logging

from src.api.schema.pagination_schema import PaginatedData, Params
from src.db.db import Base

logger = logging.getLogger(__name__)

TableType = TypeVar("TableType", bound=Base)
CreateBaseSchema = TypeVar("CreateBaseSchema", bound=BaseModel)
UpdateBaseSchema = TypeVar("UpdateBaseSchema", bound=BaseModel)


class CRUDMixin:
    table: TableType = None  # type: ignore
    create_scheme: CreateBaseSchema = None  # type: ignore
    update_scheme: UpdateBaseSchema = None  # type: ignore

    @classmethod
    async def _execute_commit(cls, query: expression, session: AsyncSession, commit: bool = True):
        await session.execute(query)
        if commit:
            await session.commit()

    @classmethod
    async def create(
        cls,
        input_data: create_scheme,
        session: AsyncSession,
        http_exc_text: str = "Record with some unique data exists",
    ):
        try:
            obj = cls.table(**input_data.dict())
            session.add(obj)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(detail=http_exc_text, status_code=status.HTTP_400_BAD_REQUEST)
        await session.refresh(obj)
        return obj

    @classmethod
    def get_pk_attr(cls):
        return getattr(cls.table.__table__.c, cls.table.pk_name())

    @classmethod
    async def get_first(cls, session: AsyncSession):
        query = select(cls.table)
        res = await session.execute(query)
        return res.scalars().first()

    @classmethod
    def _check_object(cls, obj: table) -> Union[bool, HTTPException]:
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
        return True

    @classmethod
    async def list(cls, session: AsyncSession) -> table:
        query = select(cls.table).order_by(cls.table.id)
        objects = await session.execute(query)
        return objects.scalars().all()

    @classmethod
    async def retrieve(cls, pk: int, session: AsyncSession) -> Union[table, HTTPException]:
        query = select(cls.table).where(cls.get_pk_attr() == pk)
        res = await session.execute(query)
        obj = res.scalars().first()
        cls._check_object(obj)
        await session.refresh(obj)
        return obj

    @classmethod
    async def bulk_retrieve(cls, pks: List[int], session: AsyncSession) -> List[table] or HTTPException:
        query = select(cls.table).where(cls.get_pk_attr().in_(pks))
        res = await session.execute(query)
        objs = res.scalars().all()
        [cls._check_object(obj) for obj in objs]
        [await session.refresh(obj) for obj in objs]
        return objs

    @classmethod
    async def update(
        cls,
        pk: int,
        input_data: update_scheme,
        session: AsyncSession,
        partial: bool = False,
    ) -> Union[table, HTTPException]:
        retrieved_obj = await cls.retrieve(pk, session)
        query = update(cls.table).where(cls.get_pk_attr() == pk).values(**input_data.dict(exclude_unset=partial))
        await cls._execute_commit(query, session)
        return retrieved_obj

    @classmethod
    async def bulk_update(
        cls,
        pks: List[int],
        input_data: update_scheme,
        session: AsyncSession,
        partial: bool = False,
    ) -> List[table] or HTTPException:
        retrieved_objs = await cls.bulk_retrieve(pks, session)
        query = update(cls.table).where(cls.get_pk_attr().in_(pks)).values(**input_data.dict(exclude_unset=partial))
        await cls._execute_commit(query, session)
        return retrieved_objs

    @classmethod
    async def delete(cls, pk: int, session: AsyncSession, commit: bool = True) -> dict or HTTPException:
        await cls.retrieve(pk, session)
        query = delete(cls.table).where(cls.get_pk_attr() == pk)
        await cls._execute_commit(query, session, commit)
        return {"status": "Success"}

    @classmethod
    async def delete_all(cls, session: AsyncSession):
        query = delete(cls.table)
        await cls._execute_commit(query, session)
        return {"status": "Success"}

    @classmethod
    async def get_first_by_filter(cls, filters: dict, session: AsyncSession):
        query = select(cls.table).filter_by(**filters)
        res = await session.execute(query)
        return res.scalars().first()

    @classmethod
    async def get_last_by_filter(cls, filters: dict, session: AsyncSession):
        query = select(cls.table).filter_by(**filters).order_by(desc("id"))
        res = await session.execute(query)
        return res.scalars().first()

    @classmethod
    async def get_or_create(cls, input_data: create_scheme, session: AsyncSession):
        res = await cls.get_first_by_filter(input_data.dict(), session)
        if res:
            return res
        return await cls.create(input_data, session)

    @classmethod
    async def get_by_ids(cls, ids: [int], session: AsyncSession):
        query = select(
            [cls.table],
            cls.table.id.in_(ids),
        )
        res = await session.execute(query)
        return res.scalars().all()

    @classmethod
    async def update_with_dict(
        cls,
        pk: int,
        input_data: dict,
        session: AsyncSession,
    ) -> Union[table, HTTPException]:
        retrieved_obj = await cls.retrieve(pk, session)
        query = update(cls.table).where(cls.get_pk_attr() == pk).values(**input_data)
        await cls._execute_commit(query, session)
        return retrieved_obj

    @classmethod
    async def get_paginated_data(
            cls,
            params: Params,
            query: Select,
            session: AsyncSession,
            is_mapping: bool = False,
            order_by: UnaryExpression = None
    ) -> PaginatedData:
        try:
            count_query = query.with_only_columns(func.count()).order_by(None)
            res = await session.execute(count_query)
        except Exception as e:
            logger.error(f"Invalid input query! {e}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Query error, try again later")
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
                total=count
            )

        except Exception as e:
            logger.error(f"Invalid data query! {e}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Query error, try again later")
