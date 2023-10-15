from typing import List

from fastapi import Depends
import base64

from sqlalchemy.ext.asyncio import AsyncSession

from . import audio_route

from semant_annotation.authentication import get_current_user
from semant_annotation.db import get_async_session, crud_general
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData
from semant_annotation.db import model
from uuid import uuid4


# send audio blob to server and just store it in a file
@audio_route.post("/", tags=["Audio"])
async def new_audio(audio: base_objects.Audio):
    # audio.audio_base64 is a blob of audio data in base64 format with header "data:audio/webm;base64,"
    # we need to remove this header and decode base64 to get raw audio data
    audio_data = base64.b64decode(audio.audio_base64.split(',')[1])
    mime_type = audio.audio_base64.split(',')[0].split(':')[1].split(';')[0]
    if "audio" not in mime_type:
        raise Exception("Wrong mime type")

    extension = mime_type.split('/')[1]
    file_name = f"{uuid4()}.{extension}"
    with open(file_name, "wb") as f:
        f.write(audio_data)

    with open("texts.txt", "a", encoding="utf-8") as f:
        f.write(f"{file_name} {audio.text.strip()}\n")

