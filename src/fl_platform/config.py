from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FL_")

    # App
    app_name: str = "FL-AgentPlatform"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fl_platform"

    # LLM
    default_llm_provider: str = "stub"  # "stub" | "claude" | "openai"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_llm_model: str = "claude-sonnet-4-20250514"

    # FAL.AI
    fal_api_key: str = ""
    default_fal_image_model: str = "fal-ai/flux/dev"
    default_fal_video_model: str = "fal-ai/minimax/video-01-live"

    # Artifacts
    artifacts_dir: str = "./artifacts"
