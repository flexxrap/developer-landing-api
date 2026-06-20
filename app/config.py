from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    owner_email: str = ""
    openrouter_api_key: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
