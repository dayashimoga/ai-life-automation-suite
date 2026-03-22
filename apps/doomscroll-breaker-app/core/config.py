from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Doomscroll Breaker App"
    api_prefix: str = "/api/v1"
    usage_threshold_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
