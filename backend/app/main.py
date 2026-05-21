from fastapi import FastAPI
from app.routers import instruments

app = FastAPI(
    title="MOEX Instruments API",
    description="API для поиска и фильтрации финансовых инструментов Московской биржи",
    version="1.0.0",
)

app.include_router(instruments.router, prefix="/api")
