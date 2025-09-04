import sys
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_api_key: str | None = None
    model_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # <-- allow extra env vars without error

settings = Settings()

# --- Debug logging ---
print("[CONFIG] Loaded settings:")
print("Base URL:", settings.model_base_url)
print("Model Name:", settings.model_name)
if not settings.model_api_key:
    print("[CONFIG ERROR] MODEL_API_KEY is missing! Did you set it in .env?")
    sys.exit(1)
else:
    print("API Key prefix:", settings.model_api_key[:8], "... (hidden)")
