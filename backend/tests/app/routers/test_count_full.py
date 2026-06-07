"""
Тесты для эндпоинта GET /api/instruments/count/full — получение общего количества инструментов с учётом всех фильтров.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime


class TestGetCountFullEndpoint:
    """Тесты эндпоинта GET /api/instruments/count/full."""

    @patch("app.routers.instruments.get_connection")
    def test_count_full_no_filters(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет что count/full без фильтров возвращает общее количество."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (42,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert data["total"] == 42

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_type_filter(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтром по типу инструмента."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (10,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?type=stock")
        assert response.status_code == 200
        assert response.json()["total"] == 10

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_sector_filter(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтром по сектору."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (5,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?sector=finance")
        assert response.status_code == 200
        assert response.json()["total"] == 5

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_price_range(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтрацией по диапазону цен."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (3,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?min_price=100&max_price=300")
        assert response.status_code == 200
        assert response.json()["total"] == 3

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_yield_filter(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтрацией по доходности."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (7,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?min_yield=5&max_yield=15")
        assert response.status_code == 200
        assert response.json()["total"] == 7

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_maturity_filter(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтрацией по дате погашения."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (4,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?maturity_from=2025-01-01&maturity_to=2030-12-31")
        assert response.status_code == 200
        assert response.json()["total"] == 4

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_option_type_filter(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтром по типу опциона."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (2,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?option_type=C")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_strike_filter(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтрацией по страйку."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (1,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?min_strike=50&max_strike=200")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_volume_filter(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтрацией по объёму."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (8,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?min_volume=100000&max_volume=5000000")
        assert response.status_code == 200
        assert response.json()["total"] == 8

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_show_null_price_false(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с show_null_price=false."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (15,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?show_null_price=false")
        assert response.status_code == 200
        assert response.json()["total"] == 15

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_all_filters(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full со всеми фильтрами одновременно."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (1,)
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/count/full"
            "?type=stock"
            "&sector=finance"
            "&min_price=200"
            "&max_price=300"
            "&min_yield=10"
            "&max_yield=15"
            "&maturity_from=2025-01-01"
            "&maturity_to=2035-12-31"
            "&option_type=C"
            "&min_strike=50"
            "&max_strike=200"
            "&min_volume=100000"
            "&max_volume=5000000"
            "&show_null_price=false"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    @patch("app.routers.instruments.get_connection")
    def test_count_full_returns_zero_when_no_match(self, mock_get_connection, client):
        """Проверяет что count/full возвращает 0 когда нет совпадений."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = (0,)
        cursor.close = MagicMock()
        conn.cursor.return_value = cursor
        conn.close = MagicMock()
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?type=bond")
        assert response.status_code == 200
        assert response.json()["total"] == 0

    @patch("app.routers.instruments.get_connection")
    def test_count_full_response_has_total_key(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет что ответ содержит ключ 'total'."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (42,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full")
        data = response.json()
        assert "total" in data
        assert "count" not in data

    def test_count_full_with_invalid_type_returns_422(self, client):
        """Проверяет что невалидный тип возвращает 422."""
        response = client.get("/api/instruments/count/full?type=invalid")
        assert response.status_code == 422

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_min_max_volume(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтрацией по минимальному и максимальному объёму."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (12,)
        mock_get_connection.return_value = conn

        response = client.get("/api/instruments/count/full?min_volume=500000&max_volume=2000000")
        assert response.status_code == 200
        assert response.json()["total"] == 12

    @patch("app.routers.instruments.get_connection")
    def test_count_full_with_all_option_filters(self, mock_get_connection, mock_db_cursor, client):
        """Проверяет count/full с фильтрами для опционов (strike + option_type)."""
        conn, cursor = mock_db_cursor
        cursor.fetchone.return_value = (3,)
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/count/full"
            "?option_type=P"
            "&min_strike=100"
            "&max_strike=500"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 3
