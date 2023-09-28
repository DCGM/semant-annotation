from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from semant_annotation.schemas.auth_objects import TokenData
from semant_annotation.db import crud_user


def challenge_user_is_admin_with_forbidden_message(
       user_token: TokenData):
    if not user_token.trusted_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trusted users can create documents.",
            headers={"WWW-Authenticate": "Bearer"})

