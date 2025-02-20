from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    PASS_DB_HOST: str
    PASS_DB_PORT: int
    PASS_DB_NAME: str
    PASS_DB_USER: str
    PASS_DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).absolute().parent.joinpath(".env")
    )


config = Config()


def get_pass_db_url():
    return (f"postgresql+asyncpg://{config.PASS_DB_USER}:{config.PASS_DB_PASSWORD}@"
            f"{config.PASS_DB_HOST}:{config.PASS_DB_PORT}/{config.PASS_DB_NAME}")


def get_auth_data():
    return {"secret_key": config.SECRET_KEY, "algorithm": config.ALGORITHM}
