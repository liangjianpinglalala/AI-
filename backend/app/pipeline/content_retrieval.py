"""Step 1：内容检索与校验。

真实实现调用 Claude（需要 ANTHROPIC_API_KEY），并强制通过 tool-use 返回结构化 JSON，
避免自由文本解析出错。未配置 Key 时使用 mock provider，便于在没有密钥的环境里跑通
其余步骤（配音/画面/字幕/剪辑）。
"""

from anthropic import Anthropic

from ..config import settings
from .schemas import ContentInfo

SYSTEM_PROMPT = """你是一位严谨的中国古典文学与成语典故助手。给定用户输入的古诗名或成语，
请检索并整理出准确的知识信息，通过 submit_content_info 工具提交结构化结果。

要求：
- 判断输入类型是古诗（poem）还是成语（idiom）。
- 内容必须准确，不确定的史实/出处不要臆造，可在 background 字段中注明存疑。
- translation、background、meaning 需要通俗易懂，适合做成解说动画的文案素材。
"""

TOOL_SCHEMA = {
    "name": "submit_content_info",
    "description": "提交结构化的古诗/成语知识信息",
    "input_schema": ContentInfo.model_json_schema(),
}


def fetch_content_claude(query: str) -> ContentInfo:
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY 未配置，无法调用 Claude 进行内容检索。"
            "请在 backend/.env 中设置该变量，或将 CONTENT_PROVIDER 设为 mock 以使用示例数据调试。"
        )
    client = Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[TOOL_SCHEMA],
        tool_choice={"type": "tool", "name": "submit_content_info"},
        messages=[{"role": "user", "content": f"请检索并整理：{query}"}],
    )
    for block in message.content:
        if block.type == "tool_use" and block.name == "submit_content_info":
            return ContentInfo.model_validate(block.input)
    raise RuntimeError("Claude 未返回预期的结构化结果（submit_content_info）")


_MOCK_DB: dict[str, ContentInfo] = {
    "静夜思": ContentInfo(
        query_type="poem",
        title="静夜思",
        author="李白",
        dynasty="唐",
        original_text="床前明月光，疑是地上霜。举头望明月，低头思故乡。",
        translation="床前洒下皎洁的月光，恍然以为是地上结了一层霜。抬头望向天边的明月，低头不禁思念起遥远的故乡。",
        background="此诗相传作于李白客居他乡之时，是中国古典诗歌中流传最广的思乡之作之一。",
        meaning="借月光引发联想，表达游子在寂静深夜里对故乡深切的思念之情。",
        example_usage=None,
    ),
    "画蛇添足": ContentInfo(
        query_type="idiom",
        title="画蛇添足",
        author=None,
        dynasty=None,
        original_text="楚有祠者，赐其舍人卮酒。舍人相谓曰：‘数人饮之不足，一人饮之有余，请画地为蛇，先成者饮酒。’"
        "一人蛇先成，引酒且饮之，乃左手持卮，右手画蛇，曰：‘吾能为之足。’未成，一人之蛇成，夺其卮曰：‘蛇固无足，子安能为之足？’遂饮其酒。",
        translation="楚国有个主持祭祀的人，把一壶酒赏给门客们。门客们商量说：‘几个人喝这壶酒不够，一个人喝还有剩余，不如大家在地上画蛇，先画好的人喝酒。’"
        "有一个人先画好了蛇，正要拿酒来喝，却左手拿着酒壶，右手继续给蛇画脚，说：‘我还能再给它添上脚呢。’脚还没画完，另一个人的蛇画好了，"
        "夺过他的酒说：‘蛇本来就没有脚，你怎么能给它添上脚呢？’于是把酒喝了。",
        background="出自《战国策·齐策二》，讲述几位门客比赛画蛇取酒的故事。",
        meaning="比喻做了多余的事，非但无益，反而弄巧成拙、坏了整体效果。",
        example_usage="报告本来已经写得很完整了，非要再堆砌一堆无关数据，简直是画蛇添足。",
    ),
}


def fetch_content_mock(query: str) -> ContentInfo:
    if query in _MOCK_DB:
        return _MOCK_DB[query]
    return ContentInfo(
        query_type="idiom",
        title=query,
        original_text=query,
        translation=f"（示例数据）“{query}”的字面含义讲解。",
        background=f"（示例数据）“{query}”的出处与背景。正式接入 Claude API 后将替换为真实检索结果。",
        meaning=f"（示例数据）“{query}”的引申含义。",
    )


def fetch_content(query: str) -> ContentInfo:
    if settings.content_provider == "mock":
        return fetch_content_mock(query)
    return fetch_content_claude(query)
