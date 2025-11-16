from collections.abc import Sequence
from typing import Any

from fastapi import Query
from pydantic import BaseModel
from pydantic.generics import GenericModel


class PaginatedData(BaseModel):
    items: Sequence[Any]
    page: int
    pages: int
    size: int
    total: int


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=100, description="Page size")
