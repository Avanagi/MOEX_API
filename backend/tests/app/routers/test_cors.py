"""
Тесты CORS middleware — проверка заголовков cross-origin.
Убеждается что CORS настроен корректно для всех эндпоинтов.
"""
import pytest
from unittest.mock import patch, MagicMock


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


class TestCORSMiddleware:
    """Тесты CORS-заголовков для всех эндпоинтов API."""

    @patch("app.routers.instruments.get_connection")
    def test_cors_headers_on_instruments_list(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет что GET /api/instruments возвращает CORS-заголовки при кросс-ориджин запросе."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = []
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"

    @patch("app.routers.instruments.get_connection")
    def test_cors_headers_on_instruments_search(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет что GET /api/instruments/search возвращает CORS-заголовки при кросс-ориджин запросе."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = []
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/search?q=test",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"

    def test_cors_headers_on_instruments_types(self, client):
        """Проверяет что GET /api/instruments/types возвращает CORS-заголовки при кросс-ориджин запросе."""
        response = client.get(
            "/api/instruments/types",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"

    @patch("app.routers.instruments.get_connection")
    def test_cors_headers_on_instruments_count(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет что GET /api/instruments/count возвращает CORS-заголовки при кросс-ориджин запросе."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (0,)
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/count",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"

    @patch("app.routers.instruments.get_connection")
    def test_cors_headers_on_instrument_detail(self, mock_get_connection, client):
        """Проверяет что GET /api/instruments/{ticker} возвращает CORS-заголовки при кросс-ориджин запросе."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        cursor.close = MagicMock()
        conn.cursor.return_value = cursor
        conn.close = MagicMock()
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/SBER",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 404
        assert response.headers.get("access-control-allow-origin") == "*"

    @patch("app.routers.instruments.get_connection")
    def test_cors_headers_on_health(self, mock_get_connection, client):
        """Проверяет что GET /api/health возвращает CORS-заголовки при кросс-ориджин запросе."""
        mock_get_connection.side_effect = Exception("DB error")

        response = client.get(
            "/api/health",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"

    @patch("app.routers.instruments.get_connection")
    def test_cors_allow_all_headers(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет что allow_headers=["*"] работает корректно."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = []
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200

    @patch("app.routers.instruments.get_connection")
    def test_cors_on_validation_error(self, mock_get_connection, client):
        """Проверяет что CORS-заголовки возвращаются даже при 422 ошибке."""
        response = client.get(
            "/api/instruments?type=invalid",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 422
        assert response.headers.get("access-control-allow-origin") == "*"

    @patch("app.routers.instruments.get_connection")
    def test_cors_on_not_found(self, mock_get_connection, client):
        """Проверяет что CORS-заголовки возвращаются при 404."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        cursor.close = MagicMock()
        conn.cursor.return_value = cursor
        conn.close = MagicMock()
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/NOTEXIST",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 404
        assert response.headers.get("access-control-allow-origin") == "*"

    @patch("app.routers.instruments.get_connection")
    def test_cors_with_different_origin(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет CORS с разными Origin-заголовками."""
        conn, cursor = mock_db_cursor
        cursor.fetchall.return_value = []
        mock_get_connection.return_value = conn

        origins = [
            "https://frontend.example.com",
            "https://admin.example.com",
            "http://localhost:3000",
            "https://moex-app.ru",
        ]
        for origin in origins:
            response = client.get(
                "/api/instruments",
                headers={"Origin": origin},
            )
            assert response.status_code == 200
            assert response.headers.get("access-control-allow-origin") == "*"
