"""Step 2：分镜脚本生成，把结构化知识转成驱动配音/画面/字幕的 Script。"""

from anthropic import Anthropic

from ..config import settings
from .schemas import ContentInfo, Scene, Script

SYSTEM_PROMPT = """你是一位擅长将古诗/成语知识改编成解说动画分镜脚本的编剧。
给定结构化的知识信息，请设计 5-8 个场景，通过 submit_script 工具提交结构化分镜脚本。

要求：
- style_prefix 统一整体画风（如“中国水墨风格，工笔重彩，古风人物”），会自动拼接到每个场景的画面 prompt 前面。
- 节奏建议：开场引入 -> 逐句/逐层解析原文 -> 背景典故 -> 寓意/情感总结。
- narration 是旁白文案（可稍长），subtitle 是屏幕字幕（更简短精炼，便于阅读）。
- 同一人物反复出现时，visual_prompt 中的外貌描述要保持一致，避免画面人物“跳变”。
- duration_hint_sec 给出合理的预估时长（秒），仅供参考，最终时长以配音实际时长为准。
"""

TOOL_SCHEMA = {
    "name": "submit_script",
    "description": "提交结构化的分镜脚本",
    "input_schema": Script.model_json_schema(),
}


def generate_script_claude(content: ContentInfo) -> Script:
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY 未配置，无法调用 Claude 生成分镜脚本。"
            "请在 backend/.env 中设置该变量，或将 CONTENT_PROVIDER 设为 mock 以使用示例数据调试。"
        )
    client = Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        tools=[TOOL_SCHEMA],
        tool_choice={"type": "tool", "name": "submit_script"},
        messages=[{"role": "user", "content": content.model_dump_json(indent=2)}],
    )
    for block in message.content:
        if block.type == "tool_use" and block.name == "submit_script":
            return Script.model_validate(block.input)
    raise RuntimeError("Claude 未返回预期的结构化结果（submit_script）")


def generate_script_mock(content: ContentInfo) -> Script:
    scenes = [
        Scene(
            scene_id=1,
            narration=f"今天我们来讲一讲{'这首诗' if content.query_type == 'poem' else '这个成语'}——{content.title}。",
            subtitle=content.title,
            visual_prompt=f"古风开场画面，书卷缓缓展开，写着“{content.title}”几个大字",
            duration_hint_sec=4,
            transition="fade",
        ),
        Scene(
            scene_id=2,
            narration=content.original_text,
            subtitle=content.original_text,
            visual_prompt="古风水墨场景，呼应原文意境",
            duration_hint_sec=6,
            transition="fade",
        ),
        Scene(
            scene_id=3,
            narration=content.translation,
            subtitle=content.translation,
            visual_prompt="古风水墨场景，呼应译文画面",
            duration_hint_sec=6,
            transition="fade",
        ),
        Scene(
            scene_id=4,
            narration=content.background,
            subtitle="背景与出处",
            visual_prompt="古风水墨场景，展现历史背景",
            duration_hint_sec=6,
            transition="fade",
        ),
        Scene(
            scene_id=5,
            narration=content.meaning,
            subtitle="寓意与感悟",
            visual_prompt="古风水墨场景，象征寓意升华",
            duration_hint_sec=6,
            transition="fade",
        ),
    ]
    return Script(style_prefix="中国水墨风格，工笔重彩，古风意境", scenes=scenes)


def generate_script(content: ContentInfo) -> Script:
    if settings.content_provider == "mock":
        return generate_script_mock(content)
    return generate_script_claude(content)
