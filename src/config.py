import os

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings

# SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "changeme")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# BIND_ADDRESS = "0.0.0.0"
# PORT = 8000

class Settings(BaseSettings):

  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

  SESSION_SECRET_KEY: str = Field(default="changeme")

  # Postgres connection settings (migrated from environment usage)
  POSTGRES_USER: str = Field(default="postgres")
  POSTGRES_PASSWORD: str = Field(default="postgres")
  POSTGRES_DB: str = Field(default="group_n_meet")
  POSTGRES_HOST: str = Field(default="postgres")
  POSTGRES_PORT: int = Field(default=5432)

  PORT : int = Field(default=8000)
  BIND_ADDRESS: str = Field(default="0.0.0.0")


## TODO: migrate to pydantic-settings