"""
Тесты производительности и edge cases — лимиты, большой payload, пустые ответы.
Проверяет что API корректно обрабатывает граничные условия нагрузки.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Фикстура для тестового клиента FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_db_cursor():
    """Фикстура для мока соединения и курсора БД."""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    cursor.close = MagicMock()
    conn.close = MagicMock()
    return conn, cursor


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


class TestPerformanceLimits:
    """Тесты граничных значений лимитов и пагинации."""

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_max_limit_allowed(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, client):
        """Проверяет что limit=200 (максимум) принимается."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = []
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments?limit=200")
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_limit_exceeds_max_returns_422(self, mock_get_connection, mock_cache_set, mock_cache_get, client):
        """Проверяет что limit > 200 возвращает 422."""
        response = client.get("/api/instruments?limit=201")
        assert response.status_code == 422

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_limit_zero_returns_422(self, mock_get_connection, mock_cache_set, mock_cache_get, client):
        """Проверяет что limit=0 возвращает 422 (должен быть >= 1)."""
        response = client.get("/api/instruments?limit=0")
        assert response.status_code == 422

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_large_offset_allowed(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, client):
        """Проверяет что большой offset (пагинация) не вызывает ошибок."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = []
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments?offset=10000")
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_negative_offset_returns_422(self, mock_get_connection, mock_cache_set, mock_cache_get, client):
        """Проверяет что отрицательный offset возвращает 422."""
        response = client.get("/api/instruments?offset=-1")
        assert response.status_code == 422


class TestEdgeCases:
    """Тесты edge cases — пустые данные, спецсимволы, дубликаты."""

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_empty_db_returns_empty_list(self, mock_get_connection, mock_cache_set, mock_cache_get, client):
        """Проверяет что пустая БД возвращает пустой список, а не null."""
        mock_cache_get.return_value = None
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None
        cursor.close = MagicMock()
        conn.cursor.return_value = cursor
        conn.close = MagicMock()
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.get_connection")
    def test_search_with_special_chars(self, mock_get_connection, mock_cache_get, client):
        """Проверяет что спецсимволы в поиске не ломают запрос."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        conn.cursor.return_value = cursor
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/search?q=%&'\"<>")
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.get_connection")
    def test_search_with_unicode(self, mock_get_connection, mock_cache_get, client):
        """Проверяет что поиск по кириллице не вызывает ошибок."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            ("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None),
        ]
        conn.cursor.return_value = cursor
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/search?q=Сбер")
        assert response.status_code == 200
        # Проверяем, что данные вернулись
        assert len(response.json()) > 0

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.get_connection")
    def test_search_with_spaces(self, mock_get_connection, mock_cache_get, client):
        """Проверяет что пробелы в поиске обрабатываются корректно."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        conn.cursor.return_value = cursor
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/search?q=Сбербанк России")
        assert response.status_code == 200

    @patch("app.routers.instruments.get_connection")
    def test_instrument_with_null_fields(self, mock_get_connection, client):
        """Проверяет что инструмент со всеми NULL-полями сериализуется корректно."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = ("TEST", "Тест", "stock", None, None, None, None, datetime.now(), None, None, None, None, None, None, None)
        conn.cursor.return_value = cursor
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/TEST")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "TEST"
        assert data["sector"] is None
        assert data["price"] is None

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_all_filters_combined(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, client):
        """Проверяет что все фильтры одновременно не ломают запрос."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = [("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)]
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments"
            "?type=stock"
            "&sector=finance"
            "&min_price=100"
            "&max_price=500"
            "&min_yield=5"
            "&max_yield=20"
            "&maturity_from=2025-01-01"
            "&maturity_to=2035-12-31"
            "&sort_by=price"
            "&order=desc"
            "&limit=10"
            "&offset=0"
        )
        assert response.status_code == 200

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.cache.set")
    @patch("app.routers.instruments.get_connection")
    def test_count_with_zero_results(self, mock_get_connection, mock_cache_set, mock_cache_get, mock_db_cursor, client):
        """Проверяет что count возвращает 0 когда нет инструментов."""
        mock_cache_get.return_value = None
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (0,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count?type=stock")
        assert response.status_code == 200
        assert response.json()["count"] == 0


class TestRateLimiting:
    """Тесты rate limiting — проверка что лимиты на запросы работают."""

    @patch("app.routers.instruments.cache.get")
    @patch("app.routers.instruments.get_connection")
    def test_search_hardcoded_limit_fifty(self, mock_get_connection, mock_cache_get, client):
        """Проверяет что поиск всегда имеет лимит 50 (нельзя увеличить)."""
        conn = MagicMock()
        cursor = MagicMock()
        
        # Мокаем execute так, чтобы он запоминал параметры
        actual_limit = None
        
        def mock_execute(sql, params):
            nonlocal actual_limit
            # Извлекаем LIMIT из SQL
            if "LIMIT" in sql:
                # Парсим LIMIT 50 или LIMIT %s
                import re
                match = re.search(r'LIMIT\s+(\d+)', sql)
                if match:
                    actual_limit = int(match.group(1))
        
        cursor.execute.side_effect = mock_execute
        
        # Возвращаем 60 записей (но реально БД вернёт только 50 из-за LIMIT)
        mock_records = [("SBER", "Сбербанк", "stock", "finance", 250.5, 1000000, "RUB", datetime.now(), 12.5, date(2030, 1, 1), 5000000000, "Сбербанк России", 15.3, None, None)] * 60
        cursor.fetchall.return_value = mock_records[:50]  # ← Обрезаем до 50, как сделала бы БД
        
        conn.cursor.return_value = cursor
        mock_get_connection.return_value = conn
        mock_cache_get.return_value = None

        response = client.get("/api/instruments/search?q=SBER")
        assert response.status_code == 200
        assert len(response.json()) <= 50
        assert actual_limit == 50, f"LIMIT должен быть 50, а не {actual_limit}"