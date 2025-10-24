
import os

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)



class DBSettings(BaseModel):
    model_config = SettingsConfigDict(
        populate_by_name=True)

    user: str = ""
    password: str = ""
    ip: str = ""
    port: int = 0
    name: str = ""



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_nested_delimiter="_",
        extra="ignore"
    )

    db: DBSettings = DBSettings()

env_config = Settings()

if __name__ == "__main__":
    print(env_config.model_dump_json(indent=2))