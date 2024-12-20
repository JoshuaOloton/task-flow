from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.db.database import engine
from api.db.models import Base
from api.routes import api_version_one

import os
import uvicorn


app = FastAPI()

app.include_router(api_version_one)

# Define the origins that you want to allow
origins = [
    "http://localhost",  # Allow local development
    "http://localhost:8000",  # Allow the frontend app running on the same port
    "https://yourfrontenddomain.com",  # Allow a specific domain (e.g., for production)
]

# Add the middleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index():
    return {"message": "Hello world"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the details for debugging purposes
    print(f"Validation error on request {request.url}: {exc}")

     # Customize the response content
    errors = []
    for error in exc.errors():
        field = error["loc"][-1]
        message = error["msg"]
        errors.append({ "field": field, "message": message })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation Error",
            "errors": errors,
            "hint": "Check the data format and required fields."
        },
    )


Base.metadata.create_all(engine)
