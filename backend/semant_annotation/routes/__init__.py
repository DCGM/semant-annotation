from fastapi import APIRouter

user_route = APIRouter()
news_route = APIRouter()
task_route = APIRouter()

from .user_routes import user_route
from .news_routes import news_route
from .task_routes import task_route
