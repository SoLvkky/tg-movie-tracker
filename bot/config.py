from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    TMDB_APIKEY: str
    DATABASE_URL: str
    DATABASE_SYNC_URL: str

    class Config:
        env_file = ".env"

settings = Settings()