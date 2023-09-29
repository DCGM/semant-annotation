from datetime import datetime, timedelta
from typing import Union, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from semant_annotation.db import crud_user
from semant_annotation.config import config
from semant_annotation.db.database import get_async_session
from semant_annotation.schemas.auth_objects import Token, TokenData
from semant_annotation.schemas.base_objects import UserInDB, User

import logging

from starlette.requests import Request
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED


class PERO_OAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            authorization = request.cookies.get("Authorization")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


authentication_route = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = PERO_OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await crud_user.get_user_by_name(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.HASH_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.HASH_ALGORITHM])
        user_id: str = payload.get("user_id")
        trusted_user: int = payload.get("trusted_user")
        if user_id is None or trusted_user is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, trusted_user=trusted_user)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_current_admin(user_token: TokenData = Depends(get_current_user)):
    if not user_token.trusted_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only available to admin users.",
            headers={"WWW-Authenticate": "Bearer"})
    return user_token


async def add_user(db: AsyncSession, user: User, password: str):
    data = user.model_dump()
    data["hashed_password"] = get_password_hash(password)
    data["created_date"] = datetime.now()
    data["last_change"] = data["created_date"]
    await crud_user.add_user(db, UserInDB(**data))


@authentication_route.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
    logging.error(f'{form_data.username}')
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": str(user.id), "trusted_user": user.trusted}, expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="Authorization", value=f"Bearer {access_token}",
                        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES*60)
    return response


@authentication_route.post("/token/renew", response_model=Token, tags=["Authentication"])
async def renew_access_token(user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    user: UserInDB = await crud_user.get_user_by_id(db, user_token.user_id)
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is disabled.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": str(user.id), "trusted_user": user.trusted},
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="Authorization", value=f"Bearer {access_token}",
                        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response


@authentication_route.get("/me", response_model=User, tags=["Authentication"])
async def read_users_me(user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    return await crud_user.get_user_by_id(db, user_token.user_id)
