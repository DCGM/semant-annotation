from pydantic import BaseModel
from typing import List, NamedTuple, Union, Optional
from uuid import UUID
from datetime import date, datetime

import enum


class AnnotationResultType(enum.Enum):
    NEW = 'new'
    CORRECTION = 'correction'
    REJECTED = 'rejected'


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
    created_date: datetime
    last_change: datetime


class NewsUpdate(BaseModel):
    id: UUID
    title: str
    short: str
    content: str
    deleted: bool = False
    released_date: Union[datetime, None] = None


class News(NewsUpdate):
    created_date: datetime
    last_change: datetime

    class Config:
        from_attributes = True


class AnnotationSubtaskUpdate(BaseModel):
    id: UUID
    annotation_task_id: UUID
    name: str
    description: str
    active: bool = False


class AnnotationSubtask(AnnotationSubtaskUpdate):
    created_date: datetime
    last_change: datetime

    class Config:
        from_attributes = True


class AnnotationTaskUpdate(BaseModel):
    id: UUID
    name: str
    description: str
    active: bool = False


class AnnotationTask(AnnotationTaskUpdate):
    created_date: datetime
    last_change: datetime
    subtasks: List[AnnotationSubtask] = []

    class Config:
        from_attributes = True


class AnnotationTaskInstanceUpdate(BaseModel):
    id: UUID
    annotation_task_id: UUID
    image: str
    text: str
    instance_metadata: str
    active: bool


class AnnotationTaskInstance(AnnotationTaskInstanceUpdate):
    created_date: datetime
    last_change: datetime
    result_count: int = 0

    class Config:
        from_attributes = True


class SimplifiedAnnotationTaskResult(BaseModel):
    start_time: datetime
    end_time: datetime
    user_id: UUID
    subtasks: List[AnnotationSubtask] = []

    class Config:
        from_attributes = True


class AnnotationTaskResultUpdate(BaseModel):
    id: UUID
    user_id: UUID
    annotation_task_instance_id: UUID
    start_time: datetime
    end_time: datetime
    result: str
    result_type: AnnotationResultType


class AnnotationTaskResult(AnnotationTaskResultUpdate):
    created_date: datetime
    last_change: datetime

    class Config:
        from_attributes = True


class AnnotationTaskResultQuery(BaseModel):
    annotation_task_id: UUID
    page: int
    page_size: int 
    from_date: date = None
    to_date: date = None
    user_id: UUID = None


class TimeTrackingItemNew(BaseModel):
    id: UUID
    user_id: UUID
    start_time: datetime
    end_time: datetime
    task: str
    description: str


class TimeTrackingItem(TimeTrackingItemNew):
    created_date: datetime
    deleted: bool

    class Config:
        from_attributes = True

