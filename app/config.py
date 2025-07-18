from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Discord settings
    discord_bot_token: str = ""
    discord_admin_role: str = "Admin"
    admin_api_token: str = ""
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings() 