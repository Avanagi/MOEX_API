"""
Тесты для коллектора данных MOEX (moex_collector.py).
Проверяет парсинг API-ответа, сохранение в БД и оркестрацию сбора данных.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from collector.moex_collector import fetch_instruments, save_to_db, collect, MOEX_ENDPOINTS


class TestFetchInstruments:
    """Тесты функции fetch_instruments — парсинг данных с API MOEX."""

    @pytest.mark.asyncio
    async def test_fetch_instruments_parses_response(self):
        """Проверяет корректный парсинг полного ответа API MOEX для всех полей."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()

        mock_response.json = AsyncMock(return_value={
            "securities": {
                "columns": ["SECID", "SECNAME", "SHORTNAME", "SECTYPENAME", "CURRENCYID", "STRIKE", "OPTIONTYPE"],
                "data": [
                    ["SBER", "Сбербанк", "Sberbank", "finance", "RUB", 100, "CALL"],
                    ["GAZA", "Газпром", "Gazprom", "energy", "RUB", None, None],
                ],
            },
            "marketdata": {
                "columns": ["SECID", "LAST", "VOLTODAY", "YIELD", "ISSUECAPITALIZATION"],
                "data": [
                    ["SBER", 250.5, 1000000, 12.5, 5000000000],
                    ["GAZA", 180.0, 800000, 8.3, 8000000000],
                ],
            },
        })
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {}

        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        result = await fetch_instruments(mock_session, "stock", "https://example.com")

        assert len(result) == 2
        assert result[0]["ticker"] == "SBER"
        assert result[0]["name"] == "Сбербанк"
        assert result[0]["type"] == "stock"
        assert result[0]["price"] == 250.5
        assert result[0]["volume"] == 1000000
        assert result[0]["currency"] == "RUB"
        assert result[0]["yield"] == 12.5
        assert result[0]["market_cap"] == 5000000000
        assert result[0]["strike_price"] == 100
        assert result[0]["option_type"] == "CALL"

        assert result[1]["ticker"] == "GAZA"
        assert result[1]["price"] == 180.0
        assert result[1]["market_cap"] == 8000000000

    @pytest.mark.asyncio
    async def test_fetch_instruments_empty_response(self):
        """Проверяет обработку пустого ответа API (нет инструментов)."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()

        mock_response.json = AsyncMock(return_value={
            "securities": {"columns": [], "data": []},
            "marketdata": {"columns": [], "data": []},
        })
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {}

        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        result = await fetch_instruments(mock_session, "stock", "https://example.com")
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_instruments_without_marketdata(self):
        """Проверяет обработку ответа без marketdata (цена будет None)."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()

        mock_response.json = AsyncMock(return_value={
            "securities": {
                "columns": ["SECID", "SECNAME", "SHORTNAME"],
                "data": [["SBER", "Сбербанк", "Sberbank"]],
            },
            "marketdata": {},
        })
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {}

        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        result = await fetch_instruments(mock_session, "stock", "https://example.com")
        assert len(result) == 1
        assert result[0]["ticker"] == "SBER"
        assert result[0]["price"] is None

    @pytest.mark.asyncio
    async def test_fetch_instruments_with_maturity_date(self):
        """Проверяет корректный парсинг даты погашения (MATDATE)."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()

        mock_response.json = AsyncMock(return_value={
            "securities": {
                "columns": ["SECID", "SECNAME", "MATDATE"],
                "data": [["BOND1", "Облигация 1", "2030-06-15"]],
            },
            "marketdata": {
                "columns": ["SECID"],
                "data": [["BOND1"]],
            },
        })
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {}

        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        result = await fetch_instruments(mock_session, "bond", "https://example.com")
        assert result[0]["maturity_date"] == datetime.strptime("2030-06-15", "%Y-%m-%d").date()

    @pytest.mark.asyncio
    async def test_fetch_instruments_invalid_maturity_date(self):
        """Проверяет что невалидная дата погашения (0000-00-00)转为 None."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()

        mock_response.json = AsyncMock(return_value={
            "securities": {
                "columns": ["SECID", "SECNAME", "MATDATE"],
                "data": [["BOND1", "Облигация 1", "0000-00-00"]],
            },
            "marketdata": {
                "columns": ["SECID"],
                "data": [["BOND1"]],
            },
        })
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {}

        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        result = await fetch_instruments(mock_session, "bond", "https://example.com")
        assert result[0]["maturity_date"] is None

    @pytest.mark.asyncio
    async def test_fetch_instruments_http_error(self):
        """Проверяет что HTTP-ошибка возвращает пустой список без исключения."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()

        mock_response.raise_for_status = MagicMock(side_effect=Exception("HTTP Error"))
        mock_response.headers = {}

        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        result = await fetch_instruments(mock_session, "stock", "https://example.com")
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_instruments_missing_secid_skipped(self):
        """Проверяет что инструменты без SECID пропускаются."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()

        mock_response.json = AsyncMock(return_value={
            "securities": {
                "columns": ["SECID", "SECNAME"],
                "data": [[None, "Без тикера"], ["SBER", "Сбербанк"]],
            },
            "marketdata": {
                "columns": ["SECID"],
                "data": [],
            },
        })
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {}

        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        result = await fetch_instruments(mock_session, "stock", "https://example.com")
        assert len(result) == 1
        assert result[0]["ticker"] == "SBER"


class TestSaveToDb:
    """Тесты функции save_to_db — сохранение инструментов в PostgreSQL."""

    @patch("collector.moex_collector.psycopg2.connect")
    def test_save_to_db_inserts_records(self, mock_connect):
        """Проверяет что save_to_db формирует корректные SQL-запросы (DELETE + INSERT)."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.commit = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn

        instruments = [
            {"ticker": "SBER", "name": "Сбербанк", "type": "stock", "sector": "finance"},
            {"ticker": "GAZA", "name": "Газпром", "type": "stock", "sector": "energy"},
        ]

        save_to_db(instruments)

        mock_cursor.execute.assert_called()
        assert mock_cursor.execute.call_count == 3  # DELETE + 2 INSERTs
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("collector.moex_collector.psycopg2.connect")
    def test_save_to_db_empty_list(self, mock_connect):
        """Проверяет что пустой список не инициирует подключение к БД."""
        save_to_db([])
        mock_connect.assert_not_called()

    @patch("collector.moex_collector.psycopg2.connect")
    def test_save_to_db_none_list(self, mock_connect):
        """Проверяет что None не инициирует подключение к БД."""
        save_to_db(None)
        mock_connect.assert_not_called()

    @patch("collector.moex_collector.psycopg2.connect")
    def test_save_to_db_error_handling(self, mock_connect):
        """Проверяет что ошибка подключения не выбрасывает исключение наружу."""
        mock_connect.side_effect = Exception("DB error")

        instruments = [{"ticker": "SBER", "name": "Сбербанк", "type": "stock", "sector": "finance"}]
        save_to_db(instruments)

        mock_connect.assert_called_once()


class TestCollect:
    """Тесты функции collect() — оркестрация сбора данных со всех эндпоинтов MOEX."""

    @pytest.mark.asyncio
    async def test_collect_gathers_all_types(self):
        """Проверяет что collect собирает данные для всех 4 типов инструментов."""
        with patch("collector.moex_collector.fetch_instruments") as mock_fetch, \
             patch("collector.moex_collector.save_to_db") as mock_save:

            async def side_effect(session, itype, url):
                return [
                    {"ticker": f"{itype.upper()}_1", "type": itype},
                    {"ticker": f"{itype.upper()}_2", "type": itype},
                ]

            mock_fetch.side_effect = side_effect

            await collect()

            assert mock_save.called
            saved_data = mock_save.call_args[0][0]
            assert len(saved_data) == 8

    @pytest.mark.asyncio
    async def test_collect_handles_empty_results(self):
        """Проверяет что collect корректно обрабатывает пустые результаты."""
        with patch("collector.moex_collector.fetch_instruments") as mock_fetch, \
             patch("collector.moex_collector.save_to_db") as mock_save:

            mock_fetch.return_value = []

            await collect()

            mock_save.assert_called_once()
            assert mock_save.call_args[0][0] == []
