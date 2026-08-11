from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read from the DATABASE_URL environment variable (set by docker-compose).
    # The default is only a local fallback — real credentials live in .env.
    database_url: str = "postgresql+psycopg2://sentinel:sentinel@db:5432/sentinel"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
