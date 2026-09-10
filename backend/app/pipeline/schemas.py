from typing import Literal

from pydantic import BaseModel, Field


class ContentInfo(BaseModel):
    """content_retrieval 步骤的结构化输出。"""

    query_type: Literal["poem", "idiom"]
    title: str
    author: str | None = None
    dynasty: str | None = None
    original_text: str
    translation: str
    background: str
    meaning: str
    example_usage: str | None = None


class Scene(BaseModel):
    scene_id: int
    narration: str
    subtitle: str
    visual_prompt: str
    duration_hint_sec: float = 6.0
    transition: Literal["fade", "cut", "dissolve"] = "fade"


class Script(BaseModel):
    """script_generation 步骤的结构化输出：驱动配音/画面/字幕/剪辑。"""

    style_prefix: str = Field(description="统一画风描述，会拼接到每个场景的 visual_prompt 前面")
    scenes: list[Scene]
