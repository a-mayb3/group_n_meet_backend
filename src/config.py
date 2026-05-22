from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

  SESSION_SECRET_KEY: SecretStr = Field(default=SecretStr("CHANGE_ME_IMMEDIATELY"))
  GEMINI_API_KEY: SecretStr | None = Field(default=None)
  GEMINI_MODEL: str = Field(default="gemini-2.5-flash")

  POSTGRES_USER: str = Field(default="postgres")
  POSTGRES_PASSWORD: str = Field(default="postgres")
  POSTGRES_DB: str = Field(default="group_n_meet")
  POSTGRES_HOST: str = Field(default="postgres")
  POSTGRES_PORT: int = Field(default=5432)

  PORT: int = Field(default=8000)
  BIND_ADDRESS: str = Field(default="0.0.0.0")
  ROOT_PATH: str = Field(default="")