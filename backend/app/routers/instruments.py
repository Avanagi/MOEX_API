from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.instrument import InstrumentOut, InstrumentFilter, InstrumentSearch
from app.database import get_connection

router = APIRouter()

COLUMNS = [
    "ticker",
    "name",
    "type",
    "sector",
    "price",
    "volume",
    "currency",
    "updated_at",
    "yield",
    "maturity_date",
    "market_cap",
    "issuer",
]


@router.get("/instruments", response_model=List[InstrumentOut])
async def get_instruments(filters: InstrumentFilter = Depends()):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT ticker, name, type, sector, price, volume, currency,
               updated_at, yield, maturity_date, market_cap, issuer
        FROM instruments WHERE 1=1
    """
    params = []

    if filters.type:
        query += " AND type = %s"
        params.append(filters.type)

    if filters.sector:
        query += " AND sector = %s"
        params.append(filters.sector)

    if filters.min_price is not None:
        query += " AND price >= %s"
        params.append(filters.min_price)

    if filters.max_price is not None:
        query += " AND price <= %s"
        params.append(filters.max_price)

    query += f" ORDER BY {filters.sort_by} {filters.order}"
    query += " LIMIT %s OFFSET %s"
    params.extend([filters.limit, filters.offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [dict(zip(COLUMNS, row)) for row in rows]


@router.get("/instruments/search", response_model=List[InstrumentOut])
async def search_instruments(q: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ticker, name, type, sector, price, volume, currency,
               updated_at, yield, maturity_date, market_cap, issuer
        FROM instruments
        WHERE name ILIKE %s OR ticker ILIKE %s
        LIMIT 50
    """,
        [f"%{q}%", f"%{q}%"],
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [dict(zip(COLUMNS, row)) for row in rows]


@router.get("/instruments/types")
async def get_types():
    return ["stock", "bond", "futures", "option"]


@router.get("/instruments/{ticker}", response_model=InstrumentOut)
async def get_instrument(ticker: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ticker, name, type, sector, price, volume, currency,
               updated_at, yield, maturity_date, market_cap, issuer
        FROM instruments WHERE ticker = %s
    """,
        [ticker.upper()],
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Инструмент не найден")

    return dict(zip(COLUMNS, row))


@router.get("/health")
async def health():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "error", "db": "disconnected"}
