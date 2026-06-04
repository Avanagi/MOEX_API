from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.instrument import InstrumentOut, InstrumentFilter
from app.database import get_connection
from app import cache

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

SELECT_FIELDS = """
    ticker, name, type, sector, price, volume, currency,
    updated_at, yield, maturity_date, market_cap, issuer,
    volatility, strike_price, option_type
"""


@router.get("/instruments", response_model=List[InstrumentOut])
async def get_instruments(filters: InstrumentFilter = Depends()):

    cache_key = cache.make_key(
        "instruments",
        type=filters.type,
        sector=filters.sector,
        min_price=filters.min_price,
        max_price=filters.max_price,
        min_yield=filters.min_yield,
        max_yield=filters.max_yield,
        maturity_from=filters.maturity_from,
        maturity_to=filters.maturity_to,
        sort_by=filters.sort_by,
        order=filters.order,
        limit=filters.limit,
        offset=filters.offset,
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_connection()
    cursor = conn.cursor()

    query = f"SELECT {SELECT_FIELDS} FROM instruments WHERE 1=1"
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

    result = [dict(zip(COLUMNS, row)) for row in rows]
    cache.set(cache_key, result)
    return result


@router.get("/instruments/search", response_model=List[InstrumentOut])
async def search_instruments(
    q: str,
    type: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
):

    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT {SELECT_FIELDS}
        FROM instruments
        WHERE (ticker ILIKE %s OR name ILIKE %s)
    """
    params = [f"%{q}%", f"%{q}%"]

    if type:
        query += " AND type = %s"
        params.append(type)

    if sort_by and sort_by in {"ticker", "price", "volume", "name", "market_cap"}:
        sort_order = "DESC" if order == "desc" else "ASC"
        query += f" ORDER BY CASE WHEN price IS NULL THEN 1 ELSE 0 END, {sort_by} {sort_order}"
    else:
        query += " ORDER BY CASE WHEN ticker ILIKE %s THEN 0 ELSE 1 END"
        params.append(q)

    query += " LIMIT 50"

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

    cache_key = cache.make_key("count", type=type)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_connection()
    cursor = conn.cursor()
    if type:
        cursor.execute("SELECT COUNT(*) FROM instruments WHERE type = %s", [type])
    else:
        cursor.execute("SELECT COUNT(*) FROM instruments")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    result = {"count": count}
    cache.set(cache_key, result)
    return result


@router.get("/instruments/{ticker}", response_model=InstrumentOut)
async def get_instrument(ticker: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT {SELECT_FIELDS} FROM instruments WHERE ticker = %s",
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
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    cache_status = "connected" if cache.get_client() is not None else "disconnected"

    status = "ok" if db_status == "connected" else "error"
    return {"status": status, "db": db_status, "cache": cache_status}
