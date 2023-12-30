import sys
from pathlib import Path

from loguru import logger
from pydantic import Field, field_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class HostPort(BaseModel):
    host: str
    port: int


class UserPass(BaseModel):
    username: str
    password: str


class Redis(HostPort):
    # password: str

    @property
    def url(self):
        return 'redis://{host}:{port}/0'.format(**self.model_dump())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).with_name('.env'),
        env_file_encoding='utf-8',
        extra='ignore',
        env_nested_delimiter='_',
    )

    project_folder: Path = '/app'
    storage_folder: Path = '/storage'

    redis: Redis

    @field_validator('project_folder', 'storage_folder')
    def check_folder(cls, v):
        assert v.exists()
        return v


settings = Settings()

logger.remove()
logger.add(sys.stdout, colorize=True, level="DEBUG")
