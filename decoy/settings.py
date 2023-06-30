from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_file: str = Field(env="DECOY_DATABASE_FILE", default="decoy.duckdb")


settings = Settings()
