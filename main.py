from fastapi import FastAPI
from api.db.database import engine
from api.db.models import Base
from api.routes.tasks import task_router

app = FastAPI()
app.include_router(task_router)

@app.get('/')
def index():
    return {"message": "Hello world"}


Base.metadata.create_all(engine)