from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.db.database import engine
from api.db.models import Base
from api.routes import api_version_one


app = FastAPI()

app.include_router(api_version_one)

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