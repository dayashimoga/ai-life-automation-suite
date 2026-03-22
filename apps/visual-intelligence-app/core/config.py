from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Visual Intelligence App"
    api_prefix: str = "/api/v1"
    event_threshold: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
