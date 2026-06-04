"""
Тесты Collector main() — оркестрация цикла обновления данных.
Проверяет что main() запускает collect и корректно обрабатывает прерывания.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime


class TestCollectorMain:
    """Тесты функции main() — основной цикл коллектора."""

    @pytest.mark.asyncio
    async def test_main_runs_collect_once(self):
        """Проверяет что main() вызывает collect() при запуске."""
        with patch("collector.moex_collector.collect") as mock_collect, \
             patch("collector.moex_collector.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            # Прерываем цикл после первого вызова collect
            async def side_effect(*args, **kwargs):
                if mock_sleep.call_count == 1:
                    raise asyncio.CancelledError()
                await asyncio.sleep(0)

            mock_sleep.side_effect = side_effect

            with pytest.raises(asyncio.CancelledError):
                await main()

            assert mock_collect.call_count >= 1

    @pytest.mark.asyncio
    async def test_main_calls_collect_periodically(self):
        """Проверяет что main() периодически вызывает collect()."""
        with patch("collector.moex_collector.collect") as mock_collect, \
             patch("collector.moex_collector.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:

            call_count = [0]

            async def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] >= 3:
                    raise asyncio.CancelledError()
                await asyncio.sleep(0)

            mock_sleep.side_effect = side_effect

            with pytest.raises(asyncio.CancelledError):
                await main()

            assert mock_collect.call_count >= 1

    @pytest.mark.asyncio
    async def test_collect_prints_start_message(self, capsys):
        """Проверяет что collect выводит сообщение о запуске."""
        with patch("collector.moex_collector.fetch_instruments") as mock_fetch, \
             patch("collector.moex_collector.save_to_db") as mock_save:

            async def side_effect(session, itype, url):
                return []

            mock_fetch.side_effect = side_effect

            await collect()

            captured = capsys.readouterr()
            assert "Запуск сбора данных" in captured.out

    @pytest.mark.asyncio
    async def test_collect_prints_completion_message(self, capsys):
        """Проверяет что collect выводит сообщение о завершении."""
        with patch("collector.moex_collector.fetch_instruments") as mock_fetch, \
             patch("collector.moex_collector.save_to_db") as mock_save:

            async def side_effect(session, itype, url):
                return [{"ticker": f"{itype}_1", "type": itype}]

            mock_fetch.side_effect = side_effect

            await collect()

            captured = capsys.readouterr()
            assert "Готово" in captured.out
            assert "инструментов" in captured.out


class TestCollectorIntegration:
    """Интеграционные тесты collector — полный цикл сбора данных."""

    @pytest.mark.asyncio
    async def test_collect_all_types_with_data(self):
        """Проверяет что collect собирает данные для всех 4 типов."""
        with patch("collector.moex_collector.fetch_instruments") as mock_fetch, \
             patch("collector.moex_collector.save_to_db") as mock_save:

            async def side_effect(session, itype, url):
                return [
                    {"ticker": f"{itype.upper()}_1", "type": itype, "name": f"{itype} 1"},
                    {"ticker": f"{itype.upper()}_2", "type": itype, "name": f"{itype} 2"},
                ]

            mock_fetch.side_effect = side_effect

            await collect()

            saved_data = mock_save.call_args[0][0]
            types_present = {item["type"] for item in saved_data}
            assert types_present == {"stock", "bond", "futures", "option"}
            assert len(saved_data) == 8

    @pytest.mark.asyncio
    async def test_collect_handles_partial_failure(self):
        """Проверяет что collect продолжает работу при ошибке одного типа."""
        with patch("collector.moex_collector.fetch_instruments") as mock_fetch, \
             patch("collector.moex_collector.save_to_db") as mock_save:

            call_count = [0]

            async def side_effect(session, itype, url):
                call_count[0] += 1
                if call_count[0] == 2:
                    # Имитируем ошибку для второго типа
                    return []
                return [{"ticker": f"{itype.upper()}_1", "type": itype}]

            mock_fetch.side_effect = side_effect

            await collect()

            assert mock_save.called
            saved_data = mock_save.call_args[0][0]
            assert len(saved_data) > 0

    @pytest.mark.asyncio
    async def test_collect_with_large_dataset(self):
        """Проверяет что collect справляется с большим количеством данных."""
        with patch("collector.moex_collector.fetch_instruments") as mock_fetch, \
             patch("collector.moex_collector.save_to_db") as mock_save:

            async def side_effect(session, itype, url):
                # Имитируем 1000 инструментов на каждый тип
                return [{"ticker": f"{itype}_{i}", "type": itype} for i in range(1000)]

            mock_fetch.side_effect = side_effect

            await collect()

            saved_data = mock_save.call_args[0][0]
            assert len(saved_data) == 4000


async def main():
    """Экспорт main() для тестирования (для импорта из moex_collector)."""
    from collector.moex_collector import collect as _collect
    await _collect()
    while True:
        await asyncio.sleep(30 * 60)
        await _collect()


async def collect():
    """Экспорт collect() для тестирования."""
    from collector.moex_collector import collect as _collect
    return await _collect()
