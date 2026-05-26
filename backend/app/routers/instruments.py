from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
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
    "volatility",
    "strike_price",
    "option_type",
]


@router.get("/instruments", response_model=List[InstrumentOut])
async def get_instruments(filters: InstrumentFilter = Depends()):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT ticker, name, type, sector, price, volume, currency,
           updated_at, yield, maturity_date, market_cap, issuer,
           volatility, strike_price, option_type
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

    if filters.min_yield is not None:
        query += " AND yield >= %s"
        params.append(filters.min_yield)

    if filters.max_yield is not None:
        query += " AND yield <= %s"
        params.append(filters.max_yield)

    if filters.maturity_from is not None:
        query += " AND maturity_date >= %s"
        params.append(filters.maturity_from)

    if filters.maturity_to is not None:
        query += " AND maturity_date <= %s"
        params.append(filters.maturity_to)

    query += f" ORDER BY CASE WHEN price IS NULL THEN 1 ELSE 0 END, {filters.sort_by} {filters.order}"
    query += " LIMIT %s OFFSET %s"
    params.extend([filters.limit, filters.offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [dict(zip(COLUMNS, row)) for row in rows]


@router.get("/instruments/search", response_model=List[InstrumentOut])
async def search_instruments(q: str, type: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT ticker, name, type, sector, price, volume, currency,
        updated_at, yield, maturity_date, market_cap, issuer,
        volatility, strike_price, option_type
        FROM instruments
        WHERE (ticker ILIKE %s OR name ILIKE %s)
    """
    params = [f"%{q}%", f"%{q}%"]

    if type:
        query += " AND type = %s"
        params.append(type)

    query += " ORDER BY CASE WHEN ticker ILIKE %s THEN 0 ELSE 1 END LIMIT 50"
    params.append(q)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [dict(zip(COLUMNS, row)) for row in rows]


@router.get("/instruments/types")
async def get_types():
    return ["stock", "bond", "futures", "option"]


@router.get("/instruments/count")
async def get_count(type: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if type:
        cursor.execute("SELECT COUNT(*) FROM instruments WHERE type = %s", [type])
    else:
        cursor.execute("SELECT COUNT(*) FROM instruments")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"count": count}


@router.get("/instruments/{ticker}", response_model=InstrumentOut)
async def get_instrument(ticker: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ticker, name, type, sector, price, volume, currency,
        updated_at, yield, maturity_date, market_cap, issuer,
        volatility, strike_price, option_type
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
