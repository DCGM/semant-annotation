import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from semant_annotation.config import config
from semant_annotation.db import init_db, DBError
from semant_annotation.routes import user_route, news_route
from semant_annotation.authentication import authentication_route


tags_metadata = [
]

app = FastAPI(openapi_tags=tags_metadata)


@app.on_event("startup")
async def startup():
    await init_db()


app.include_router(user_route, prefix="/api/user")
app.include_router(authentication_route, prefix="/api")
app.include_router(authentication_route, prefix="")
app.include_router(news_route, prefix="/api/news")


@app.exception_handler(DBError)
async def unicorn_exception_handler(request: Request, exc: DBError):
    return JSONResponse(status_code=400, content={"message": str(exc)})


if config.PRODUCTION:
    logging.warning(f'PRODUCTION')
else:
    logging.warning(f'DEVELOPMENT')
    app.add_middleware(
         CORSMiddleware,
         allow_origins=["http://localhost:9000", "http://127.0.0.1:9000"],
         allow_credentials=True,
         allow_methods=["*"],
         allow_headers=["*"],
     )
