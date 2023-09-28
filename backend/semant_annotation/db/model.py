from semant_annotation.db import Base
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.types import String

from typing import List, Optional
import uuid
import datetime


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    disabled: Mapped[bool] = mapped_column(default=False)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    full_name: Mapped[str] = mapped_column(String(128), index=True)
    email: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    institution: Mapped[Optional[str]] = mapped_column(String(300))

    trusted: Mapped[int]
    hashed_password: Mapped[str]
    reset_password_token: Mapped[Optional[str]]


class News(Base):
    __tablename__ = 'news'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    short: Mapped[str] = mapped_column(String(3000), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    released_date: Mapped[datetime.datetime] = mapped_column(index=True, nullable=True)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    deleted: Mapped[bool] = mapped_column(default=False, nullable=False)


class Messages(Base):
    __tablename__ = 'messages'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    message: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    read: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)

    user: Mapped['User'] = relationship()
