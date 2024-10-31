from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import text_tagging_route

from semant_annotation.authentication import get_current_admin, get_current_user
from semant_annotation.db import get_async_session, crud_general, crud_text_tagging
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData
from semant_annotation.db import model
from semant_annotation.db.database import DBError
from uuid import UUID
import datetime
from semant_annotation.config import config




@text_tagging_route.get("/document", response_model=List[base_objects.Document], tags=["Text tagging"])
async def get_task(
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    return await crud_general.get_all(db, base_objects.Document, model.Document)


@text_tagging_route.get("/document/{document_id}", response_model=base_objects.DocumentWithParagraphsAndTags, tags=["Text tagging"])
async def get_task_by_id(document_id: UUID,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    return await crud_text_tagging.get_document_with_paragraphs_and_tags(db, document_id)


@text_tagging_route.post("/document", tags=["Text tagging"])
async def add_document(document: base_objects.DocumentWithParagraphs,
                    user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_text_tagging.new_document(db, document)


@text_tagging_route.post("/tag/{paragraph_id}/{tag_id}", tags=["Text tagging"])
async def add_tag(paragraph_id: UUID, tag_id: UUID,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):

    tag = base_objects.ParagraphTag(
        id=UUID.uuid4(), paragraph_id=paragraph_id, tag_id=tag_id, user_id=user_token.user_id,
        timestamp=datetime.datetime.utcnow())

    await crud_general.new(db, tag, model.ParagraphTag)


@text_tagging_route.delete("/tag/{paragraph_id}/{tag_id}", tags=["Text tagging"])
async def delete_tag(paragraph_id: UUID, tag_id: UUID,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):

    await crud_text_tagging.delete_tag(db, paragraph_id, tag_id, user_token.user_id)


text_tagging_route.get("/next_document", response_model=base_objects.DocumentWithParagraphsAndTags, tags=["Text tagging"])
async def get_next_document(
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):

    document_id = await crud_text_tagging.get_random_next_doucment(db)

    return await crud_text_tagging.get_next_document_with_paragraphs_and_tags(db, document_id)