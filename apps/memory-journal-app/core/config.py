from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Memory Journal App"
    api_prefix: str = "/api/v1"

    model_config = {"env_file": ".env"}


settings = Settings()
