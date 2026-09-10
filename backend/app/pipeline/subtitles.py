"""Step 5：字幕与时间轴对齐。

按每个场景配音的真实时长顺序切分时间轴，生成标准 .srt 字幕文件。
"""

from pathlib import Path

from .schemas import Scene


def _format_timestamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(scenes: list[Scene], durations: list[float], out_path: Path) -> None:
    lines: list[str] = []
    cursor = 0.0
    for idx, (scene, duration) in enumerate(zip(scenes, durations), start=1):
        start, end = cursor, cursor + duration
        lines.append(str(idx))
        lines.append(f"{_format_timestamp(start)} --> {_format_timestamp(end)}")
        lines.append(scene.subtitle)
        lines.append("")
        cursor = end
    out_path.write_text("\n".join(lines), encoding="utf-8")
