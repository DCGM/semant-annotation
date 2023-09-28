from sqlalchemy.orm import DeclarativeBase
from uuid import UUID


class Base(DeclarativeBase):
    pass


from semant_annotation.db.database import init_db, get_async_session, DBError


def validate_uuid(val):
    if is_valid_uuid(val):
        return UUID(str(val))
    else:
        return None


def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


