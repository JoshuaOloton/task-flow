from fastapi import APIRouter

from api.routes.tasks import task_router
from api.routes.user import user_router

api_version_one = APIRouter(prefix='/api/v1')


api_version_one.include_router(task_router)
api_version_one.include_router(user_router)