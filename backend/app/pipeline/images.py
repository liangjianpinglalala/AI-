"""Step 4：画面生成。

MVP 阶段用 placeholder provider（本地用 PIL 画一张带文字的卡片），不依赖任何外部
API/Key，先把渲染流程跑通。真实的文生图效果需要接入付费 API（通义万相/Replicate 等），
接口已预留：新增一个 provider 函数，并在 config.image_provider 中切换即可，不用改动
调用方代码。
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..config import settings
from .schemas import Scene

WIDTH, HEIGHT = 1280, 720
BACKGROUND = (245, 240, 230)
BORDER = (120, 100, 80)
TEXT_COLOR = (60, 50, 40)

# PIL 的默认字体不含中文字形，会把汉字画成方块；这里显式加载系统已安装的中文字体
# （与 backend/Dockerfile 里安装的 fonts-wqy-zenhei 包对应）。
_CJK_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def _load_font(size: int) -> ImageFont.ImageFont:
    for path in _CJK_FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _generate_placeholder(prompt: str, scene_id: int, out_path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BACKGROUND)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, WIDTH - 40, HEIGHT - 40], outline=BORDER, width=4)

    title_font = _load_font(32)
    body_font = _load_font(26)

    title = f"场景 {scene_id}"
    body = prompt if len(prompt) <= 80 else prompt[:80] + "…"
    wrapped = "\n".join(body[i : i + 20] for i in range(0, len(body), 20))

    draw.text((80, 90), title, fill=TEXT_COLOR, font=title_font)
    draw.multiline_text((80, 160), wrapped, fill=TEXT_COLOR, font=body_font, spacing=16)
    img.save(out_path)


def generate_scene_image(scene: Scene, style_prefix: str, out_path: Path) -> Path:
    full_prompt = f"{style_prefix}；{scene.visual_prompt}"
    if settings.image_provider == "placeholder":
        _generate_placeholder(full_prompt, scene.scene_id, out_path)
    else:
        raise NotImplementedError(
            f"未知的 IMAGE_PROVIDER: {settings.image_provider}。"
            "Phase 1 仅内置 placeholder，接入真实文生图 API 时在此扩展。"
        )
    return out_path
