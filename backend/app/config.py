from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator


class Settings(BaseSettings):
    db_host: Optional[str] = None
    db_port: int = 5432
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None

    model_config = SettingsConfigDict(env_file=None, env_file_encoding="utf-8")

    @field_validator("db_port", mode="before")
    @classmethod
    def validate_db_port(cls, v):
        if v is None or v == "" or v == 0:
            return 5432
        return v

    @model_validator(mode="after")
    def set_defaults(self):
        if self.db_host is None:
            self.db_host = ""
        if self.db_user is None:
            self.db_user = "postgres"
        if self.db_password is None:
            self.db_password = "postgres"
        if self.db_name is None:
            self.db_name = "moex"
        return self
