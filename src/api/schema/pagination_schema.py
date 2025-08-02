from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from pydantic.generics import GenericModel

ModelItem = TypeVar("ModelItem")


class PaginatedData(GenericModel, Generic[ModelItem]):
    items: list[ModelItem]
    page: int
    pages: int
    size: int
    total: int


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=100, description="Page size")
