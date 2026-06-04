"""
Тесты для кэш-модуля (cache.py).
Проверяет генерацию ключей, чтение/запись кэша, инвалидацию и поведение при недоступности Redis.
"""
import pytest
from unittest.mock import patch, MagicMock

from app import cache


class TestMakeKey:
    """Тесты функции make_key — генерация детерминированных ключей кэша."""

    def test_empty_params(self):
        """Проверяет что пустые параметры дают суффикс 'all'."""
        key = cache.make_key("instruments")
        assert key == "moex:instruments:all"

    def test_single_param(self):
        """Проверяет генерацию ключа с одним параметром."""
        key = cache.make_key("instruments", type="stock")
        assert key == "moex:instruments:type=stock"

    def test_multiple_params_sorted(self):
        """Проверяет что параметры сортируются по алфавиту."""
        key = cache.make_key("instruments", type="stock", sector="finance")
        assert key == "moex:instruments:sector=finance&type=stock"

    def test_none_params_excluded(self):
        """Проверяет что None-параметры исключаются из ключа."""
        key = cache.make_key("instruments", type=None, sector="finance")
        assert key == "moex:instruments:sector=finance"

    def test_none_and_value_params(self):
        """Проверяет генерацию ключа при смешанных None и значениях."""
        key = cache.make_key("instruments", min_price=None, max_price=100)
        assert key == "moex:instruments:max_price=100"

    def test_numeric_params(self):
        """Проверяет корректную генерацию ключа с числовыми параметрами."""
        key = cache.make_key("instruments", min_price=10, max_price=100)
        assert key == "moex:instruments:max_price=100&min_price=10"

    def test_namespace_prefix(self):
        """Проверяет что ключи всегда начинаются с namespace 'moex'."""
        key = cache.make_key("count", type="bond")
        assert key.startswith("moex:count:")

    def test_date_param(self):
        """Проверяет корректную генерацию ключа с датой."""
        key = cache.make_key("instruments", maturity_from="2024-01-01")
        assert "maturity_from=2024-01-01" in key


class TestCacheGetSet:
    """Тесты функций get() и set() кэша."""

    @patch("app.cache.get_client")
    def test_get_returns_cached_data(self, mock_get_client):
        """Проверяет что get() возвращает данные из Redis при наличии."""
        mock_client = MagicMock()
        import json
        mock_client.get.return_value = json.dumps({"count": 42})
        mock_get_client.return_value = mock_client

        result = cache.get("moex:count:all")
        assert result == {"count": 42}

    @patch("app.cache.get_client")
    def test_get_returns_none_on_miss(self, mock_get_client):
        """Проверяет что get() возвращает None при отсутствии ключа."""
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_get_client.return_value = mock_client

        result = cache.get("moex:count:missing")
        assert result is None

    @patch("app.cache.get_client")
    def test_get_returns_none_when_redis_unavailable(self, mock_get_client):
        """Проверяет что get() возвращает None при недоступном Redis."""
        mock_get_client.return_value = None

        result = cache.get("moex:count:all")
        assert result is None

    @patch("app.cache.get_client")
    def test_set_stores_data(self, mock_get_client):
        """Проверяет что set() записывает данные в Redis с указанным TTL."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        cache.set("moex:test", {"key": "value"}, ttl=60)
        mock_client.set.assert_called_once()
        call_args = mock_client.set.call_args
        assert call_args[0][0] == "moex:test"
        assert "key" in call_args[0][1]
        assert call_args[1]["ex"] == 60

    @patch("app.cache.get_client")
    def test_set_does_nothing_when_redis_unavailable(self, mock_get_client):
        """Проверяет что set() не вызывает ошибок при недоступном Redis."""
        mock_get_client.return_value = None

        cache.set("moex:test", {"key": "value"})
        assert mock_get_client.called
        # No exception should be raised


class TestCacheFlush:
    """Тесты функции flush() — инвалидация всех ключей кэша."""

    @patch("app.cache.get_client")
    def test_flush_returns_key_count(self, mock_get_client):
        """Проверяет что flush() возвращает количество удалённых ключей."""
        mock_client = MagicMock()
        mock_client.scan_iter.return_value = ["a", "b", "c"]
        mock_get_client.return_value = mock_client

        result = cache.flush()
        assert result == 3
        mock_client.delete.assert_called_once()

    @patch("app.cache.get_client")
    def test_flush_returns_zero_when_no_keys(self, mock_get_client):
        """Проверяет что flush() возвращает 0 когда ключей нет."""
        mock_client = MagicMock()
        mock_client.scan_iter.return_value = []
        mock_get_client.return_value = mock_client

        result = cache.flush()
        assert result == 0
        mock_client.delete.assert_not_called()

    @patch("app.cache.get_client")
    def test_flush_returns_zero_when_redis_unavailable(self, mock_get_client):
        """Проверяет что flush() возвращает 0 при недоступном Redis."""
        mock_get_client.return_value = None

        result = cache.flush()
        assert result == 0


class TestGetClient:
    """Тесты функции get_client() — инициализация и кэширование Redis-клиента."""

    def test_get_client_returns_none_when_redis_down(self):
        """Проверяет что get_client() возвращает None при недоступном Redis."""
        # Сбрасываем глобальный кэш перед тестом
        original_client = cache._client
        cache._client = None
        
        try:
            with patch("app.cache.redis") as mock_redis:
                mock_redis.Redis.side_effect = Exception("Connection refused")

                result = cache.get_client()
                assert result is None
        finally:
            cache._client = original_client

    def test_get_client_returns_client_when_connected(self):
        """Проверяет что get_client() возвращает клиент при успешном подключении."""
        # Сбрасываем глобальный кэш перед тестом
        original_client = cache._client
        cache._client = None
        
        try:
            with patch("app.cache.redis") as mock_redis:
                mock_client = MagicMock()
                mock_client.ping.return_value = True
                mock_redis.Redis.return_value = mock_client

                result = cache.get_client()
                assert result is mock_client
        finally:
            cache._client = original_client

    def test_get_client_caches_singleton(self):
        """Проверяет что get_client() возвращает один и тот же экземпляр (синглтон)."""
        # Сбрасываем глобальный кэш перед тестом
        original_client = cache._client
        cache._client = None
        
        try:
            with patch("app.cache.redis") as mock_redis:
                mock_client = MagicMock()
                mock_client.ping.return_value = True
                mock_redis.Redis.return_value = mock_client

                result1 = cache.get_client()
                result2 = cache.get_client()
                assert result1 is result2
        finally:
            cache._client = original_client
