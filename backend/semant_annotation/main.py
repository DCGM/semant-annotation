import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from semant_annotation.config import config
from semant_annotation.db import init_db, DBError
from semant_annotation.routes import user_route, news_route, task_route, time_tracking_route
from semant_annotation.authentication import authentication_route


tags_metadata = [
    {
        "name": "User",
        "description": "",
    },
    {
        "name": "News",
        "description": "",
    },
    {
        "name": "Task",
        "description": "",
    },
    {
        "name": "Authentication",
        "description": "",
    },
    {
        "name": "Time Tracking",
        "description": "",
    }
]

app = FastAPI(openapi_tags=tags_metadata)


@app.on_event("startup")
async def startup():
    await init_db()


app.include_router(user_route, prefix="/api/user")
app.include_router(authentication_route, prefix="/api")
app.include_router(authentication_route, prefix="")
app.include_router(news_route, prefix="/api/news")
app.include_router(task_route, prefix="/api/task")
app.include_router(time_tracking_route, prefix="/api/time_tracking")

if os.path.isdir("semant_annotation/static"):
    app.mount("/", StaticFiles(directory="semant_annotation/static", html=True), name="static")


@app.exception_handler(DBError)
async def unicorn_exception_handler(request: Request, exc: DBError):
    return JSONResponse(status_code=400, content={"message": str(exc)})


if config.PRODUCTION:
    logging.warning(f'PRODUCTION')
else:
    logging.warning(f'DEVELOPMENT')
    app.add_middleware(
         CORSMiddleware,
         allow_origins=["http://localhost:9001", "http://127.0.0.1:9001", "http://pchradis2.fit.vutbr.cz:9001"],
         allow_credentials=True,
         allow_methods=["*"],
         allow_headers=["*"],
     )
