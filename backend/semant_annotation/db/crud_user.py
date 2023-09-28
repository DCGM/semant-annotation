import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, delete, func, select
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.base_objects import UserInDB
from semant_annotation.schemas.auth_objects import TokenData
from uuid import UUID, uuid4

from typing import Union, List


async def get_user_by_name(db: AsyncSession, username: str) -> Union[UserInDB, None]:
    try:
        async with db.begin():
            result = await db.execute(select(model.User).filter(model.User.username == username))
            db_user = result.scalar_one_or_none()
            if not db_user:
                return None
            return base_objects.UserInDB.model_validate(db_user)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching user from database.')


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Union[UserInDB, None]:
    try:
        async with db.begin():
            result = await db.execute(select(model.User).filter(model.User.id == user_id))
            db_user = result.scalar_one_or_none()
            if db_user is None:
                return None
            return base_objects.UserInDB.model_validate(db_user)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching user from database.')


async def get_all_users(db: AsyncSession) -> Union[List[UserInDB]]:
    try:
        async with db.begin():
            db_users = await db.scalars(select(model.User))
            return [base_objects.UserInDB.model_validate(user) for user in db_users.all()]
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching users from database.')


async def find_users_by_name(db: AsyncSession, query: str, limit: int) -> Union[List[UserInDB]]:
    try:
        async with db.begin():
            db_users = await db.scalars(select(model.User).filter(model.User.username.like(f'%{query}%')))
            users = db_users.all()
            users = sorted(users, key=lambda u: len(u.username))
            users = users[:limit]
            return [base_objects.UserInDB.model_validate(user) for user in users]
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching users from database.')


def check_user_owner_of_document(db: AsyncSession, token: TokenData, document_id: UUID):
    try:
        db_document = db.query(model.Document).filter(model.Document.id == document_id).one_or_none()
        if db_document is None:
            return False
        return db_document.user_id == token.user_id
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching document from database.')




def check_user_owner_of_image(
        db: AsyncSession, token: TokenData, id: UUID):
    if token.trusted_user:
        return True
    result = db.query(model.Image.id).join(model.Document) \
        .filter(model.Document.user_id == token.user_id).filter(model.Image.id == id).one_or_none()
    return result is not None


def check_user_access_to_document(db: AsyncSession, token: TokenData, id: UUID):
    if token.trusted_user:
        return True
    if db.query(model.UserDocument.user_id)\
        .filter(model.UserDocument.user_id == token.user_id).filter(model.UserDocument.document_id == id).one_or_none():
        return True
    if db.query(model.Document.user_id) \
        .filter(model.Document.user_id == token.user_id).filter(model.UserDocument.document_id == id).one_or_none():
        return True
    return False


def check_user_access_to_image(db: AsyncSession, token: TokenData, id: UUID):
    if token.trusted_user:
        return True
    if db.query(model.UserDocument.user_id).join(model.Document).join(model.Image)\
        .filter(model.UserDocument.user_id == token.user_id).filter(model.Image.id == id).one_or_none():
        return True
    if db.query(model.Document.user_id).join(model.Image)\
        .filter(model.Document.user_id == token.user_id).filter(model.Image.id == id).one_or_none():
        return True
    return False


def check_user_access_to_text_region(db: AsyncSession, token: TokenData, id: UUID):
    if token.trusted_user:
        return True
    if db.query(model.UserDocument.user_id).join(model.Document).join(model.Image).join(model.TextRegion)\
        .filter(model.UserDocument.user_id == token.user_id).filter(model.TextRegion.id == id).one_or_none():
        return True
    if db.query(model.Document.user_id).join(model.Image).join(model.TextRegion)\
        .filter(model.Document.user_id == token.user_id).filter(model.TextRegion.id == id).one_or_none():
        return True
    return False


def check_user_access_to_text_line(db: AsyncSession, token: TokenData, id: UUID):
    if token.trusted_user:
        return True
    if db.query(model.UserDocument.user_id).join(model.Document).join(model.Image).join(model.TextRegion)\
            .join(model.TextLine)\
            .filter(model.UserDocument.user_id == token.user_id).filter(model.TextLine.id == id).one_or_none():
        return True
    if db.query(model.Document.user_id).join(model.Image).join(model.TextRegion) \
            .join(model.TextLine) \
            .filter(model.Document.user_id == token.user_id).filter(model.TextLine.id == id).one_or_none():
        return True
    return False


async def add_user(db: AsyncSession, user: UserInDB):
    try:
        async with db.begin():
            db.add(model.User(**user.model_dump()))
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed to add the user. User with the same user name or e-mail already exists.')


async def update_password(db: AsyncSession, user_id: UUID, password_hash):
    try:
        async with db.begin():
            db_user = await db.execute(select(model.User).where(model.User.id == user_id))
            db_user = db_user.scalar()
            db_user.hashed_password = password_hash
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed to change user password. Does the user exist?')


async def update_user(db: AsyncSession, user: base_objects.User):
    try:
        async with db.begin():
            db_user = await db.execute(select(model.User).where(model.User.id == user.id))
            db_user = db_user.scalar()
            # iterate over all fields and update them
            for field in user.model_fields_set - {'id'}:
                setattr(db_user, field, getattr(user, field))
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed to update user. Does the user exist?')
