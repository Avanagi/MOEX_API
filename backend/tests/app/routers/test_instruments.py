"""
Тесты для API-маршрутов (routers).
Проверяют все эндпоинты: получение списка инструментов, поиск, типы, счётчик, детальный просмотр, health-check.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_redis():
    """Автоматически мокает Redis для всех тестов в этом файле."""
    with patch("app.cache.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.ping.return_value = True
        mock_client.scan_iter.return_value = []
        mock_get_client.return_value = mock_client
        yield mock_get_client


class TestHealthEndpoint:
    """Тесты эндпоинта /api/health — проверка статуса подключения к БД и Redis."""

    @patch("app.routers.instruments.get_connection")
    @patch("app.routers.instruments.cache.get_client")
    def test_health_healthy(self, mock_get_client, mock_get_connection, mock_app_client):
        """Проверяет что health возвращает status=ok при работающих БД и Redis."""
        mock_get_connection.return_value = MagicMock()
        mock_get_client.return_value = MagicMock()

        response = mock_app_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["db"] == "connected"
        assert data["cache"] == "connected"

    @patch("app.routers.instruments.get_connection")
    @patch("app.routers.instruments.cache.get_client")
    def test_health_db_down(self, mock_get_client, mock_get_connection, mock_app_client):
        """Проверяет что health возвращает status=event при неработающей БД."""
        mock_get_connection.side_effect = Exception("DB error")
        mock_get_client.return_value = None

        response = mock_app_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["db"] == "disconnected"
        assert data["cache"] == "disconnected"


class TestGetInstrumentsEndpoint:
    """Тесты эндпоинта GET /api/instruments — получение списка инструментов с фильтрацией."""

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_returns_data(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет что эндпоинт возвращает данные из БД при отсутствии кэша."""
        mock_cache_get.return_value = None

        conn, cursor = mock_db_cursor
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["ticker"] == "SBER"
        assert data[1]["ticker"] == "GAZA"

    @patch("app.routers.instruments.cache.get")
    def test_get_instruments_returns_cached(self, mock_cache_get, client):
        """Проверяет что эндпоинт возвращает данные из кэша при наличии."""
        mock_cache_get.return_value = [{"ticker": "CACHED", "name": "Test", "type": "stock", "updated_at": datetime.now()}]

        response = client.get("/api/instruments")
        assert response.status_code == 200
        assert response.json()[0]["ticker"] == "CACHED"

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_with_type_filter(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет фильтрацию по типу инструмента (type=stock)."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments?type=stock")
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_with_price_filter(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет фильтрацию по диапазону цен (min_price, max_price)."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments?min_price=100&max_price=300")
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_with_sort(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет сортировку результатов (sort_by=price, order=desc)."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [
            ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None),
            ("GAZA", "Газпром", "stock", "energy", 180.0, 800000, "RUB", datetime.now(), 8.3, date(2028, 6, 15), 8000000000, "ПАО Газпром", 12.1, None, None),
        ]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments?sort_by=price&order=desc")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_pagination(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет пагинацию (limit=1, offset=0)."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [
            ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None),
        ]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments?limit=1&offset=0")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_invalid_type_returns_422(self, mock_get_connection, mock_cache_set, mock_cache_get, client):
        """Проверяет что невалидный тип возвращает 422 (ValidationError)."""
        response = client.get("/api/instruments?type=invalid")
        assert response.status_code == 422

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_with_sectors(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет фильтрацию по сектору экономики."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments?sector=finance")
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_with_yield_filter(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет фильтрацию по диапазону доходности."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments?min_yield=10&max_yield=15")
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_instruments_with_maturity_filter(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет фильтрацию по дате погашения."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments?maturity_from=2025-01-01&maturity_to=2035-12-31")
        assert response.status_code == 200


class TestSearchInstrumentsEndpoint:
    """Тесты эндпоинта GET /api/instruments/search — текстовый поиск по тикеру/названию."""

    @patch("app.routers.instruments.get_connection")
    def test_search_by_ticker(self, mock_get_connection, mock_db_cursor, mock_app_client):
        """Проверяет поиск по тикеру (q=SBER)."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [
            ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None),
        ]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/search?q=SBER")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["ticker"] == "SBER"

    @patch("app.routers.instruments.get_connection")
    def test_search_by_name(self, mock_get_connection, mock_db_cursor, mock_app_client):
        """Проверяет поиск по названию (q=Газпром)."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [
            ("GAZA", "Газпром", "stock", "energy", 180.0, 800000, "RUB", datetime.now(), 8.3, date(2028, 6, 15), 8000000000, "ПАО Газпром", 12.1, None, None),
        ]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/search?q=Газпром")
        assert response.status_code == 200

    @patch("app.routers.instruments.get_connection")
    def test_search_with_type_filter(self, mock_get_connection, mock_db_cursor, mock_app_client):
        """Проверяет поиск с фильтрацией по типу (q=SBER&type=bond)."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = []
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/search?q=SBER&type=bond")
        assert response.status_code == 200

    @patch("app.routers.instruments.get_connection")
    def test_search_no_results(self, mock_get_connection, mock_app_client):
        """Проверяет что поиск без результатов возвращает пустой список."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.close = MagicMock()
        conn.cursor.return_value = cursor
        conn.close = MagicMock()
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/search?q=NONEXISTENT")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.instruments.get_connection")
    def test_search_with_sort(self, mock_get_connection, mock_db_cursor, mock_app_client):
        """Проверяет поиск с сортировкой (sort_by=price, order=desc)."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [
            ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None),
        ]
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/search?q=Сбер&sort_by=price&order=desc")
        assert response.status_code == 200


class TestGetTypesEndpoint:
    """Тесты эндпоинта GET /api/instruments/types — получение списка доступных типов."""

    def test_get_types(self, client):
        """Проверяет что эндпоинт возвращает все 4 типа инструментов."""
        response = client.get("/api/instruments/types")
        assert response.status_code == 200
        data = response.json()
        assert set(data) == {"stock", "bond", "futures", "option"}


class TestGetCountEndpoint:
    """Тесты эндпоинта GET /api/instruments/count — получение количества инструментов."""

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_count_no_filter(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет получение общего количества без фильтрации."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (42,)
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/count")
        assert response.status_code == 200
        assert response.json()["count"] == 42

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_get_count_with_type_filter(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, mock_app_client):
        """Проверяет получение количества с фильтрацией по типу."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (10,)
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/count?type=stock")
        assert response.status_code == 200
        assert response.json()["count"] == 10

    @patch("app.routers.instruments.cache.get")
    def test_get_count_returns_cached(self, mock_cache_get, client):
        """Проверяет что эндпоинт возвращает данные из кэша."""
        mock_cache_get.return_value = {"count": 999}

        response = client.get("/api/instruments/count")
        assert response.status_code == 200
        assert response.json()["count"] == 999


class TestGetInstrumentEndpoint:
    """Тесты эндпоинта GET /api/instruments/{ticker} — получение детальной информации об инструменте."""

    @patch("app.routers.instruments.get_connection")
    def test_get_instrument_found(self, mock_get_connection, mock_db_cursor, mock_app_client):
        """Проверяет получение существующего инструмента по тикеру."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/SBER")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "SBER"

    @patch("app.routers.instruments.get_connection")
    def test_get_instrument_not_found(self, mock_get_connection, mock_app_client):
        """Проверяет что несуществующий инструмент возвращает 404."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        cursor.close = MagicMock()
        conn.cursor.return_value = cursor
        conn.close = MagicMock()
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/NOTEXIST")
        assert response.status_code == 404

    @patch("app.routers.instruments.get_connection")
    def test_get_instrument_case_insensitive(self, mock_get_connection, mock_db_cursor, mock_app_client):
        """Проверяет что поиск по тикеру не чувствителен к регистру."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/sber")
        assert response.status_code == 200
        assert response.json()["ticker"] == "SBER"

    @patch("app.routers.instruments.get_connection")
    def test_get_instrument_returns_all_fields(self, mock_get_connection, mock_db_cursor, mock_app_client):
        """Проверяет что ответ содержит все ожидаемые поля."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)
        mock_get_connection.return_value = conn

        response = mock_app_client.get("/api/instruments/SBER")
        assert response.status_code == 200
        data = response.json()
        assert "ticker" in data
        assert "name" in data
        assert "type" in data
        assert "price" in data
        assert "volume" in data
