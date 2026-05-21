from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

  SESSION_SECRET_KEY: SecretStr = Field()
  OPENAI_API_TOKEN: SecretStr | None = Field(default=None)

  POSTGRES_USER: str = Field(default="postgres")
  POSTGRES_PASSWORD: str = Field(default="postgres")
  POSTGRES_DB: str = Field(default="group_n_meet")
  POSTGRES_HOST: str = Field(default="postgres")
  POSTGRES_PORT: int = Field(default=5432)

  PORT: int = Field(default=8000)
  BIND_ADDRESS: str = Field(default="0.0.0.0")