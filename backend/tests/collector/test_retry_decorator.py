"""
Тесты для декоратора retry_on_connection_error (retry_decorator.py).
Проверяет повторные попытки при ошибках БД, Redis и сети.
"""
import pytest
from unittest.mock import patch, MagicMock
import time

import psycopg2
import redis

from collector.retry_decorator import retry_on_connection_error


class TestRetryOnDBErrors:
    """Тесты декоратора при ошибках PostgreSQL."""

    @patch("time.sleep")
    def test_succeeds_on_first_attempt(self, mock_sleep):
        """Проверяет что успешный вызов не делает повторных попыток."""
        call_count = [0]

        @retry_on_connection_error(max_retries=5, base_delay=0.01)
        def func():
            call_count[0] += 1
            return "success"

        result = func()
        assert result == "success"
        assert call_count[0] == 1
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_retries_on_db_operational_error(self, mock_sleep):
        """Проверяет что декоратор повторяет вызов при psycopg2.OperationalError."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise psycopg2.OperationalError("connection failed")
            return "recovered"

        result = func()
        assert result == "recovered"
        assert call_count[0] == 3

    @patch("time.sleep")
    def test_retries_on_db_interface_error(self, mock_sleep):
        """Проверяет что декоратор повторяет вызов при psycopg2.InterfaceError."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise psycopg2.InterfaceError("interface error")
            return "recovered"

        result = func()
        assert result == "recovered"
        assert call_count[0] == 2

    @patch("time.sleep")
    def test_raises_after_max_retries_db_error(self, mock_sleep):
        """Проверяет что после max_retries выбрасывается последняя ошибка."""
        call_count = [0]

        @retry_on_connection_error(max_retries=2, base_delay=0.01)
        def func():
            call_count[0] += 1
            raise psycopg2.OperationalError("persistent error")

        with pytest.raises(psycopg2.OperationalError, match="persistent error"):
            func()

        assert call_count[0] == 2

    @patch("time.sleep")
    def test_retries_on_interface_error_then_succeeds(self, mock_sleep):
        """Проверяет повтор при InterfaceError с успехом на 3-й попытке."""
        call_count = [0]

        @retry_on_connection_error(max_retries=5, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise psycopg2.InterfaceError("conn lost")
            return "ok"

        result = func()
        assert result == "ok"
        assert call_count[0] == 3


class TestRetryOnRedisErrors:
    """Тесты декоратора при ошибках Redis."""

    @patch("time.sleep")
    def test_retries_on_redis_connection_error(self, mock_sleep):
        """Проверяет повтор при redis.ConnectionError."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise redis.ConnectionError("redis down")
            return "redis up"

        result = func()
        assert result == "redis up"
        assert call_count[0] == 3

    @patch("time.sleep")
    def test_retries_on_redis_timeout_error(self, mock_sleep):
        """Проверяет повтор при redis.TimeoutError."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise redis.TimeoutError("redis timeout")
            return "ok"

        result = func()
        assert result == "ok"
        assert call_count[0] == 2

    @patch("time.sleep")
    def test_raises_after_max_retries_redis_error(self, mock_sleep):
        """Проверяет что после max_retries выбрасывается последняя redis-ошибка."""
        call_count = [0]

        @retry_on_connection_error(max_retries=2, base_delay=0.01)
        def func():
            call_count[0] += 1
            raise redis.ConnectionError("always down")

        with pytest.raises(redis.ConnectionError):
            func()

        assert call_count[0] == 2


class TestRetryOnNetworkErrors:
    """Тесты декоратора при сетевых ошибках."""

    @patch("time.sleep")
    def test_retries_on_connection_refused(self, mock_sleep):
        """Проверяет повтор при ConnectionRefusedError."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionRefusedError("connection refused")
            return "connected"

        result = func()
        assert result == "connected"
        assert call_count[0] == 2

    @patch("time.sleep")
    def test_retries_on_timeout_error(self, mock_sleep):
        """Проверяет повтор при TimeoutError."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise TimeoutError("timed out")
            return "ok"

        result = func()
        assert result == "ok"
        assert call_count[0] == 2

    @patch("time.sleep")
    def test_retries_on_os_error(self, mock_sleep):
        """Проверяет повтор при OSError."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise OSError("network error")
            return "ok"

        result = func()
        assert result == "ok"
        assert call_count[0] == 2


class TestRetryBehavior:
    """Тесты общего поведения декоратора."""

    @patch("collector.retry_decorator.time.sleep")
    def test_exponential_backoff_delays(self, mock_sleep):
        """Проверяет что задержка экспоненциально растёт."""
        call_count = [0]

        @retry_on_connection_error(max_retries=4, base_delay=0.01)
        def func():
            call_count[0] += 1
            raise psycopg2.OperationalError("err")

        with pytest.raises(psycopg2.OperationalError):
            func()

        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert len(sleep_calls) == 3
        assert sleep_calls[1] > sleep_calls[0]
        assert sleep_calls[2] > sleep_calls[1]

    @patch("time.sleep")
    def test_custom_max_retries(self, mock_sleep):
        """Проверяет что кастомный max_retries работает."""
        call_count = [0]

        @retry_on_connection_error(max_retries=10, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] < 5:
                raise psycopg2.OperationalError("err")
            return "ok"

        result = func()
        assert result == "ok"
        assert call_count[0] == 5

    @patch("collector.retry_decorator.time.sleep")
    def test_custom_base_delay(self, mock_sleep):
        """Проверяет что кастомная base_delay используется как начальная задержка."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.1)
        def func():
            call_count[0] += 1
            raise psycopg2.OperationalError("err")

        with pytest.raises(psycopg2.OperationalError):
            func()

        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert len(sleep_calls) == 2
        assert sleep_calls[0] >= 0.1

    def test_does_not_retry_non_connection_errors(self):
        """Проверяет что ValueError не вызывает повторных попыток."""
        call_count = [0]

        @retry_on_connection_error(max_retries=5, base_delay=0.01)
        def func():
            call_count[0] += 1
            raise ValueError("not a connection error")

        with pytest.raises(ValueError, match="not a connection error"):
            func()

        assert call_count[0] == 1

    def test_preserves_function_metadata(self):
        """Проверяет что декоратор сохраняет имя и docstring функции."""

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def my_test_function():
            """My docstring."""
            return 42

        assert my_test_function.__name__ == "my_test_function"
        assert my_test_function.__doc__ == "My docstring."
        assert my_test_function() == 42

    @patch("time.sleep")
    def test_passes_args_and_kwargs(self, mock_sleep):
        """Проверяет что аргументы и kwargs передаются корректно."""
        received_args = []
        received_kwargs = {}

        @retry_on_connection_error(max_retries=2, base_delay=0.01)
        def func(a, b, c=None):
            received_args.extend([a, b])
            received_kwargs["c"] = c
            return a + b + (c or 0)

        result = func(10, 20, c=30)
        assert result == 60
        assert received_args == [10, 20]
        assert received_kwargs["c"] == 30

    @patch("time.sleep")
    def test_single_retry_then_success(self, mock_sleep):
        """Проверяет сценарий: ошибка на 1-й попытке, успех на 2-й."""
        call_count = [0]

        @retry_on_connection_error(max_retries=5, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise redis.ConnectionError("first fail")
            return "success"

        result = func()
        assert result == "success"
        assert call_count[0] == 2

    @patch("time.sleep")
    def test_no_sleep_on_first_success(self, mock_sleep):
        """Проверяет что sleep не вызывается если первая попытка успешна."""

        @retry_on_connection_error(max_retries=5, base_delay=1.0)
        def func():
            return "ok"

        func()
        mock_sleep.assert_not_called()

    @patch("collector.retry_decorator.time.sleep")
    def test_raises_last_exception_on_failure(self, mock_sleep):
        """Проверяет что выбрасывается именно последняя ошибка."""
        call_count = [0]

        @retry_on_connection_error(max_retries=3, base_delay=0.01)
        def func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise psycopg2.OperationalError("first")
            elif call_count[0] == 2:
                raise redis.ConnectionError("second")
            else:
                raise OSError("last")

        try:
            func()
            assert False, "Should have raised"
        except OSError as exc:
            assert str(exc) == "last"
        except Exception as exc:
            assert False, f"Wrong exception type: {type(exc)}"

        assert call_count[0] == 3
