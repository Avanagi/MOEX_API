from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date


class InstrumentOut(BaseModel):
    ticker: str
    name: str
    type: str
    sector: Optional[str] = None
    price: Optional[float] = None
    volume: Optional[int] = None
    currency: Optional[str] = None
    updated_at: datetime
    yield_: Optional[float] = Field(default=None, alias="yield")
    maturity_date: Optional[date] = None
    market_cap: Optional[int] = None
    issuer: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class InstrumentFilter(BaseModel):
    type: Optional[str] = Field(
        default=None, description="Тип инструмента: stock, bond, futures, option"
    )
    sector: Optional[str] = Field(
        default=None, description="Сектор экономики: IT, energy, finance, ..."
    )
    min_price: Optional[float] = Field(
        default=None, ge=0, description="Минимальная цена (>= 0)"
    )
    max_price: Optional[float] = Field(
        default=None, ge=0, description="Максимальная цена (>= 0)"
    )
    sort_by: str = Field(
        default="ticker", description="Поле сортировки: ticker, price, volume, name"
    )
    order: str = Field(default="asc", description="Направление: asc или desc")
    limit: int = Field(
        default=50, ge=1, le=200, description="Количество записей (от 1 до 200)"
    )
    offset: int = Field(default=0, ge=0, description="Смещение для пагинации")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed = {"stock", "bond", "futures", "option"}
        if v is not None and v not in allowed:
            raise ValueError(f"type должен быть одним из: {allowed}")
        return v

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        allowed = {"ticker", "price", "volume", "name"}
        if v not in allowed:
            raise ValueError(f"sort_by должен быть одним из: {allowed}")
        return v

    @field_validator("order")
    @classmethod
    def validate_order(cls, v):
        if v not in {"asc", "desc"}:
            raise ValueError("order должен быть asc или desc")
        return v


class InstrumentSearch(BaseModel):
    q: str = Field(
        min_length=1, max_length=100, description="Строка поиска по названию или тикеру"
    )
