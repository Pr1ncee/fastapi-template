from sqlalchemy import Column, DateTime
from sqlalchemy.sql.functions import now, current_timestamp

from src.db.db import Base


class BaseModel(Base):
    __abstract__ = True

    created_at = Column("created_at", DateTime, server_default=now())
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=now(),
        onupdate=current_timestamp(),
    )

    @classmethod
    def pk_name(cls):
        """Pick"""
        return cls.__mapper__.primary_key[0].name

    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
