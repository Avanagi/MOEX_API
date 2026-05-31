from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.routers import instruments

app = FastAPI(
    title="MOEX Instruments API",
    description="API для поиска и фильтрации финансовых инструментов Московской биржи",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    errors = exc.errors(include_url=False, include_context=False)
    return JSONResponse(status_code=422, content={"detail": errors})


app.include_router(instruments.router, prefix="/api")
