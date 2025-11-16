import sqlalchemy as sa

from src.models import BaseModel
from src.models.enums.user_role_enum import UserRoleEnum


class User(BaseModel):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String(64), nullable=False)
    last_name = sa.Column(sa.String(64), nullable=False)
    email = sa.Column(sa.String(length=256), nullable=False)
    phone_number = sa.Column(sa.String(length=64), nullable=False)
    user_role = sa.Column(sa.Enum(UserRoleEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    password = sa.Column(sa.String(length=128))
