import asyncio
import aiohttp
import psycopg2
import time
from datetime import datetime
import os
from dotenv import load_dotenv

import sys

sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "dbname": os.getenv("DB_NAME", "moex"),
}

MOEX_ENDPOINTS = {
    "stock": "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json",
    "bond": "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities.json",
    "futures": "https://iss.moex.com/iss/engines/futures/markets/forts/boards/RFUD/securities.json",
    "option": "https://iss.moex.com/iss/engines/futures/markets/options/boards/ROPD/securities.json",
}


async def fetch_instruments(session, instrument_type, url):
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)

        securities = data.get("securities", {})
        marketdata = data.get("marketdata", {})

        sec_columns = securities.get("columns", [])
        sec_rows = securities.get("data", [])
        mkt_columns = marketdata.get("columns", [])
        mkt_rows = marketdata.get("data", [])

        sec_list = [dict(zip(sec_columns, row)) for row in sec_rows]
        mkt_list = [dict(zip(mkt_columns, row)) for row in mkt_rows]
        mkt_by_ticker = {row["SECID"]: row for row in mkt_list if "SECID" in row}

        instruments = []
        for sec in sec_list:
            ticker = sec.get("SECID")
            if not ticker:
                continue

            mkt = mkt_by_ticker.get(ticker, {})

            maturity_raw = sec.get("MATDATE")
            maturity_date = None
            if maturity_raw and maturity_raw != "0000-00-00":
                try:
                    maturity_date = datetime.strptime(maturity_raw, "%Y-%m-%d").date()
                except ValueError:
                    maturity_date = None

            instruments.append(
                {
                    "ticker": ticker,
                    "name": sec.get("SECNAME") or sec.get("SHORTNAME"),
                    "type": instrument_type,
                    "sector": sec.get("SECTYPENAME"),
                    "price": mkt.get("LAST") or mkt.get("MARKETPRICE"),
                    "volume": mkt.get("VOLTODAY"),
                    "currency": sec.get("CURRENCYID", "RUB"),
                    "yield": mkt.get("YIELD"),
                    "maturity_date": maturity_date,
                    "market_cap": mkt.get("ISSUECAPITALIZATION")
                    or sec.get("ISSUECAPITALIZATION"),
                    "issuer": sec.get("EMITENTNAME") or sec.get("SHORTNAME"),
                    "volatility": None,
                    "strike_price": sec.get("STRIKE"),
                    "option_type": sec.get("OPTIONTYPE"),
                }
            )

        print(
            f"[{datetime.now()}] Получено {len(instruments)} инструментов ({instrument_type})"
        )
        return instruments

    except Exception as e:
        print(f"[{datetime.now()}] Ошибка {instrument_type}: {e}")
        return []


def save_to_db(all_instruments):
    if not all_instruments:
        return

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # удаляем старые данные по этому типу перед вставкой
        instrument_type = all_instruments[0]["type"]
        # удаляем все старые данные перед вставкой
        cursor.execute("DELETE FROM instruments")

        for item in all_instruments:
            cursor.execute(
                """
                INSERT INTO instruments (
                    ticker, name, type, sector, price, volume, currency,
                    yield, maturity_date, market_cap, issuer,
                    volatility, strike_price, option_type, updated_at
                )
                VALUES (
                    %(ticker)s, %(name)s, %(type)s, %(sector)s, %(price)s,
                    %(volume)s, %(currency)s, %(yield)s, %(maturity_date)s,
                    %(market_cap)s, %(issuer)s, %(volatility)s, %(strike_price)s,
                    %(option_type)s, NOW()
                )
                ON CONFLICT (ticker) DO UPDATE SET
                    name          = EXCLUDED.name,
                    type          = EXCLUDED.type,
                    sector        = EXCLUDED.sector,
                    price         = EXCLUDED.price,
                    volume        = EXCLUDED.volume,
                    currency      = EXCLUDED.currency,
                    yield         = EXCLUDED.yield,
                    maturity_date = EXCLUDED.maturity_date,
                    market_cap    = EXCLUDED.market_cap,
                    issuer        = EXCLUDED.issuer,
                    volatility    = EXCLUDED.volatility,
                    strike_price  = EXCLUDED.strike_price,
                    option_type   = EXCLUDED.option_type,
                    updated_at    = NOW()
            """,
                item,
            )

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{datetime.now()}] Сохранено {len(all_instruments)} инструментов в БД")

    except Exception as e:
        print(f"[{datetime.now()}] Ошибка записи в БД: {e}")


async def collect():
    print(f"[{datetime.now()}] Запуск сбора данных...")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_instruments(session, itype, url)
            for itype, url in MOEX_ENDPOINTS.items()
        ]
        results = await asyncio.gather(*tasks)

    all_instruments = [item for sublist in results for item in sublist]
    save_to_db(all_instruments)

    elapsed = time.time() - start
    print(
        f"[{datetime.now()}] Готово. Всего: {len(all_instruments)} инструментов за {elapsed:.1f} сек"
    )


async def main():

    await collect()

    while True:
        await asyncio.sleep(30 * 60)
        await collect()


if __name__ == "__main__":
    asyncio.run(main())
