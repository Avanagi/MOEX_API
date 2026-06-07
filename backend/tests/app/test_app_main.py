import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app


class TestAppMetadata:

    def test_app_title(self):
        assert app.title == "MOEX Instruments API"

    def test_app_version(self):
        assert app.version == "1.0.0"

    def test_app_description_not_empty(self):
        assert app.description is not None
        assert len(app.description) > 0

    def test_openapi_schema_exists(self):
        schema = app.openapi()
        assert "info" in schema
        assert "paths" in schema
        assert schema["info"]["title"] == "MOEX Instruments API"


class TestCORSMiddleware:

    def test_cors_allow_origins_star(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments/types",
            headers={"Origin": "https://any-domain.com"},
        )
        assert response.headers.get("access-control-allow-origin") == "*"

    def test_cors_allow_methods_contains_get(self):
        client = TestClient(app)
        response = client.options(
            "/api/instruments/types",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "GET" in allow_methods

    def test_cors_on_validation_error(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?type=invalid_type",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 422
        assert response.headers.get("access-control-allow-origin") == "*"

    def test_cors_on_404(self):
        client = TestClient(app)
        response = client.get(
            "/api/nonexistent",
            headers={"Origin": "https://example.com"},
        )
        assert response.status_code == 404
        assert response.headers.get("access-control-allow-origin") == "*"


class TestPydanticValidationHandler:

    def test_validation_error_has_custom_format(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?type=invalid",
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    def test_validation_error_type_field(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?type=invalid_type",
        )
        assert response.status_code == 422
        data = response.json()
        assert len(data["detail"]) > 0
        error = data["detail"][0]
        assert "type" in error.get("loc", []) or "type" in str(error.get("loc", []))

    def test_validation_error_limit_too_large(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?limit=300",
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_validation_error_limit_zero(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?limit=0",
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_validation_error_negative_offset(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?offset=-1",
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_validation_error_order_invalid(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?order=random",
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_validation_error_sort_by_invalid(self):
        client = TestClient(app)
        response = client.get(
            "/api/instruments?sort_by=invalid_column",
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_valid_request_no_validation_error(self):
        client = TestClient(app)
        with patch("app.routers.instruments.get_connection") as mock_get_conn:
            conn = MagicMock()
            cursor = MagicMock()
            cursor.fetchall.return_value = []
            cursor.fetchone.return_value = (0,)
            cursor.close = MagicMock()
            conn.cursor.return_value = cursor
            conn.close = MagicMock()
            mock_get_conn.return_value = conn

            response = client.get(
                "/api/instruments?type=stock&sort_by=price&order=asc&limit=10&offset=0",
            )
            assert response.status_code == 200

    @patch("app.routers.instruments.get_connection")
    def test_search_endpoint_accepts_long_query(self, mock_get_connection):
        client = TestClient(app)
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        conn.cursor.return_value = cursor
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/search?q=" + "a" * 101,
        )
        assert response.status_code == 200

    @patch("app.routers.instruments.get_connection")
    def test_search_endpoint_accepts_empty_query(self, mock_get_connection):
        client = TestClient(app)
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        conn.cursor.return_value = cursor
        mock_get_connection.return_value = conn

        response = client.get(
            "/api/instruments/search?q=",
        )
        assert response.status_code == 200


class TestAppRoutes:

    def test_instruments_router_registered(self):
        routes = [r.path for r in app.routes]
        assert "/api/instruments" in routes

    def test_health_router_registered(self):
        routes = [r.path for r in app.routes]
        assert "/api/health" in routes

    def test_instruments_search_router_registered(self):
        routes = [r.path for r in app.routes]
        assert "/api/instruments/search" in routes

    def test_instruments_count_router_registered(self):
        routes = [r.path for r in app.routes]
        assert "/api/instruments/count" in routes

    def test_instruments_types_router_registered(self):
        routes = [r.path for r in app.routes]
        assert "/api/instruments/types" in routes

    def test_openapi_schema_has_all_paths(self):
        schema = app.openapi()
        paths = schema.get("paths", {})
        assert "/api/instruments" in paths
        assert "/api/instruments/search" in paths
        assert "/api/instruments/types" in paths
        assert "/api/instruments/count" in paths
        assert "/api/health" in paths


class TestAppExceptionHandling:

    def test_unhandled_exception_returns_500(self):
        client = TestClient(app, raise_server_exceptions=False)

        with patch("app.routers.instruments.get_connection") as mock_get_conn:
            mock_get_conn.side_effect = Exception("unexpected error")

            response = client.get("/api/instruments")
            assert response.status_code == 500

    def test_validation_error_not_converted_to_500(self):
        client = TestClient(app)
        response = client.get("/api/instruments?type=bad")
        assert response.status_code == 422
        assert response.status_code != 500
