from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_file: str = Field(env="DECOY_DATABASE_FILE", default="decoy.duckdb")


settings = Settings()
