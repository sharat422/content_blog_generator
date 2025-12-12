from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(extra="allow")  # <-- accept extra env vars

    MODEL_API_KEY: str | None = None
    VITE_API_URL: str | None = None
    MODEL_NAME: str | None = None
    VITE_SUPABASE_URL: str | None = None
    VITE_SUPABASE_ANON_KEY: str | None = None
    XAI_API_KEY: str | None = None
    XAI_API_BASE: str | None = None

    # 🔥 Add these bridge properties so llm.py works:
    @property
    def model_name(self) -> str | None:
        return self.MODEL_NAME

    @property
    def model_api_key(self) -> str | None:
        return self.MODEL_API_KEY

    @property
    def model_base_url(self) -> str | None:
        # use a BASE_URL env if present, otherwise VITE_API_URL
        return getattr(self, "BASE_URL", None) or self.VITE_API_URL


settings = Settings()

CREDIT_COSTS = {
    "text": 5,
    "image": 20,
    "video_script": 8,
    "outline": 3,
    "video_render": 100
}

def get_cost(action_type: str):
    return CREDIT_COSTS.get(action_type, 5)


