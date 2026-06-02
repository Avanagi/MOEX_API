from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = ""
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "moex"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
