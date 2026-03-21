"""Configuration settings using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    toolbox_timeout_default: int = 30
    toolbox_shell_enabled: bool = True
    toolbox_log_level: str = "INFO"
    toolbox_max_output_size: int = 1048576  # 1MB
    toolbox_port: int = 8080
    toolbox_workspace: str = "/workspace"

    class Config:
        env_prefix = ""
        env_file = ".env"


settings = Settings()
