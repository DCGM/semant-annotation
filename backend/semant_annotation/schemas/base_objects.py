from pydantic import BaseModel
from typing import List, NamedTuple, Union, Optional
from uuid import UUID
from datetime import datetime

import enum


class User(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str
    institution: str
    disabled: bool = False
    trusted: int

    class Config:
        from_attributes = True


class UserWithPasswd(User):
    password: str


class UserInDB(User):
    hashed_password: str
    reset_password_token: Optional[str] = None


class NewsUpdate(BaseModel):
    id: UUID
    title: str
    short: str
    content: str
    deleted: bool = False
    released_date: Union[datetime, None] = None

    class Config:
        from_attributes = True


class News(NewsUpdate):
    created_date: datetime
    last_change: datetime

    class Config:
        from_attributes = True