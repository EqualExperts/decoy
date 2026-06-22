from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_file: str = Field(default="decoy.duckdb", validation_alias="DECOY_DATABASE_FILE")


settings = Settings()
