from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.include_router(instruments.router, prefix="/api")
