"""
Тесты для конфигурации приложения (Settings).
Проверяет загрузку переменных окружения и значения по умолчанию.
"""
import pytest

from app.config import Settings


@pytest.fixture
def env_settings(tmp_path):
    """Создаёт временный .env файл с тестовыми переменными для БД."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DB_HOST=testhost\nDB_PORT=5433\nDB_USER=testuser\nDB_PASSWORD=testpass\nDB_NAME=testdb\n"
    )
    return env_file


def test_settings_default_values():
    """Проверяет что Settings инициализируется с корректными значениями по умолчанию."""
    settings = Settings()
    assert settings.db_host == ""
    assert settings.db_port == 5432
    assert settings.db_user == "postgres"
    assert settings.db_password == "postgres"
    assert settings.db_name == "moex"


def test_settings_loads_from_env(env_settings):
    """Проверяет что Settings загружает значения из .env файла."""
    settings = Settings(_env_file=env_settings)
    assert settings.db_host == "testhost"
    assert settings.db_port == 5433
    assert settings.db_user == "testuser"
    assert settings.db_password == "testpass"
    assert settings.db_name == "testdb"


def test_settings_env_port_type_conversion(env_settings):
    """Проверяет что порт из .env (строка) корректно преобразуется в int."""
    settings = Settings(_env_file=env_settings)
    assert isinstance(settings.db_port, int)
    assert settings.db_port == 5433
