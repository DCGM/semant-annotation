from semant_annotation.db import Base
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.types import String

from typing import List, Optional
import uuid
import datetime
import random
from functools import partial
from semant_annotation.schemas import base_objects


max_random_number = 1000000000

class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    disabled: Mapped[bool] = mapped_column(default=False)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    full_name: Mapped[str] = mapped_column(String(128), index=True)
    email: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    institution: Mapped[Optional[str]] = mapped_column(String(300))
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)

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
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    released_date: Mapped[datetime.datetime] = mapped_column(index=True, nullable=True)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    deleted: Mapped[bool] = mapped_column(default=False, nullable=False)


class Messages(Base):
    __tablename__ = 'messages'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    message: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    read: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)

    user: Mapped['User'] = relationship()


class AnnotationTask(Base):
    __tablename__ = 'annotation_tasks'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str]
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=False, nullable=False)

    subtasks: Mapped[List['AnnotationSubtask']] = relationship( viewonly=True, lazy='joined')


class AnnotationSubtask(Base):
    __tablename__ = 'annotation_subtasks'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    annotation_task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('annotation_tasks.id'), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str]
    active: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)


class AnnotationTaskInstance(Base):
    __tablename__ = 'annotation_task_instances'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    annotation_task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('annotation_tasks.id'), index=True, nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    last_send_send_to_user: Mapped[datetime.datetime] = mapped_column(index=True, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    instance_metadata: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    result_count_new: Mapped[int] = mapped_column(default=0, nullable=False)
    result_count_correction: Mapped[int] = mapped_column(default=0, nullable=False)


    random_number: Mapped[int] = mapped_column(default=partial(random.randint, 0, max_random_number), nullable=False, index=True)


#  Mapped[base_objects.WorkState] = mapped_column(default=base_objects.WorkState.NEW, nullable=False)


class AnnotationTaskResult(Base):
    __tablename__ = 'annotation_task_results'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)
    annotation_task_instance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('annotation_task_instances.id'), index=True, nullable=False)
    result: Mapped[str]
    result_type: Mapped[base_objects.AnnotationResultType] = mapped_column(nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
    last_change: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True, nullable=False)
