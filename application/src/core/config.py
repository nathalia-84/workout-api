from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_uri: str
    mongo_db_name: str
    jwt_secret: str
    jwt_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
