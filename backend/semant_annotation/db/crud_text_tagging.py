import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, or_, update, delete
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects
from datetime import datetime, timedelta
from uuid import UUID
import random


async def new_document(db: AsyncSession, document: base_objects.DocumentWithParagraphs):
    try:
        async with db.begin():
            db_document = model.Document(**document.model_dump())
            db.add(db_document)
            await db.flush()
            for i, paragraph in enumerate(document.paragraphs):
                paragraph.document_id = db_document.id
                paragraph.paragraph_number = i
                db_paragraph = model.Paragraph(**paragraph.model_dump())
                db.add(db_paragraph)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed storing document in database.')



async def get_random_next_document(db: AsyncSession) -> UUID:
    try:
        async with db.begin():
            offset = random.randint(0, 100)
            stmt = select(model.Document.id).order_by(model.Document.annotation_count.asc()).offset(offset).limit(1)
            result = await db.execute(stmt)
            db_document_id = result.scalar_one_or_none()
            return db_document_id
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching random document from database.')


async def get_document_with_paragraphs_and_tags(db: AsyncSession, document_id: UUID) -> base_objects.DocumentWithParagraphsAndTags:
    try:
        async with db.begin():
            stmt = select(model.Document).where(model.Document.id == document_id)
            result = await db.execute(stmt)
            db_document = result.scalar_one_or_none()
            if db_document is None:
                raise DBError(f'No document with id {document_id} found in database.')
            stmt = select(model.Paragraph).where(model.Paragraph.document_id == document_id)
            result = await db.execute(stmt)
            db_paragraphs = result.scalars().all()

            # get tags for all paragraphs
            stmt = select(model.Tag.id, model.Tag.name, model.ParagraphTag.paragraph_id, model.ParagraphTag.user_id).join(model.ParagraphTag).where(model.ParagraphTag.paragraph_id.in_([p.id for p in db_paragraphs]))
            tags = await db.execute(stmt)

            # TODO: MISSING CODE


    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching document with paragraphs and tags from database. Error: {str(e)}')


#await crud_text_tagging.delete_tag(db, paragraph_id, tag_id, user_token.user_id)
async def delete_tag(db: AsyncSession, paragraph_id: UUID, tag_id: UUID, user_id: UUID):
    try:
        async with db.begin():
            stmt = delete(model.ParagraphTag).where(model.ParagraphTag.paragraph_id == paragraph_id).where(model.ParagraphTag.tag_id == tag_id).where(model.ParagraphTag.user_id == user_id)
            await db.execute(stmt)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed deleting tag from database.')