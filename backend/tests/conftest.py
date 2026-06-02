import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.models.instrument import InstrumentOut, InstrumentFilter, InstrumentSearch


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_cursor():
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None),
        ("GAZA", "Газпром", "stock", "energy", 180.0, 800000, "RUB", datetime.now(), 8.3, date(2028, 6, 15), 8000000000, "ПАО Газпром", 12.1, None, None),
    ]
    cursor.fetchone.return_value = ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)
    cursor.close = MagicMock()

    conn = MagicMock()
    conn.cursor.return_value = cursor
    conn.close = MagicMock()

    return conn, cursor


@pytest.fixture
def mock_redis_client():
    with patch("app.cache.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.ping.return_value = True
        mock_client.scan_iter.return_value = []
        mock_get_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_instrument_data():
    return {
        "ticker": "SBER",
        "name": "Сбербанк",
        "type": "stock",
        "sector": "finance",
        "price": 250.5,
        "volume": 1000000,
        "currency": "RUB",
        "updated_at": datetime.now(),
        "yield": 12.5,
        "maturity_date": date(2030, 1, 1),
        "market_cap": 5000000000,
        "issuer": "Сбербанк России",
        "volatility": 15.3,
        "strike_price": None,
        "option_type": None,
    }


@pytest.fixture
def mock_app_client():
    return TestClient(app)
