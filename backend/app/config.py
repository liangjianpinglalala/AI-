from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5"

    # Phase 1 各步骤的 provider 开关，便于在没有 API Key/网络受限的环境中调试：
    # content_provider: claude(真实调用) | mock(示例数据，跳过 Claude 依赖，脚本生成同样受此开关影响)
    # tts_provider: edge(edge-tts，免费但需正常公网访问) | silent(静音占位音频，用于离线调试渲染流程)
    # image_provider: placeholder(本地生成占位图，Phase 1 唯一实现)
    content_provider: str = "claude"
    tts_provider: str = "edge"
    image_provider: str = "placeholder"

    media_root: str = "media"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
