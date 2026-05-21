import requests
import psycopg2
import schedule
import time
from datetime import datetime
import os
from dotenv import load_dotenv

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


def fetch_instruments(instrument_type, url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

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
                    "volatility": None,  # считается отдельно по историческим данным
                    "strike_price": sec.get("STRIKE"),
                    "option_type": sec.get("OPTIONTYPE"),
                }
            )

        return instruments

    except requests.RequestException as e:
        print(f"[{datetime.now()}] Ошибка запроса {instrument_type}: {e}")
        return []
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка обработки {instrument_type}: {e}")
        return []


def save_to_db(instruments):
    if not instruments:
        return

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for item in instruments:
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
        print(f"[{datetime.now()}] Сохранено {len(instruments)} инструментов")

    except Exception as e:
        print(f"[{datetime.now()}] Ошибка записи в БД: {e}")


def collect():
    print(f"[{datetime.now()}] Запуск сбора данных...")
    total = 0
    for instrument_type, url in MOEX_ENDPOINTS.items():
        instruments = fetch_instruments(instrument_type, url)
        save_to_db(instruments)
        total += len(instruments)
    print(f"[{datetime.now()}] Готово. Всего обработано: {total}")


collect()

schedule.every(30).minutes.do(collect)

while True:
    schedule.run_pending()
    time.sleep(1)
