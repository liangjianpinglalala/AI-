"""Step 3：配音（TTS）。

默认使用 edge-tts（微软 Edge 内置语音，免费，无需 API Key），需要能访问
speech.platform.bing.com 的 WebSocket 服务；部分受限网络环境（如某些代理沙箱）
不支持 WebSocket 升级，此时可将 TTS_PROVIDER 设为 silent，生成等时长的静音占位音频，
用于在没有网络的环境下验证画面/字幕/剪辑等其余步骤。
"""

import asyncio
import subprocess
from pathlib import Path

import edge_tts

from ..config import settings

VOICE = "zh-CN-XiaoxiaoNeural"
CHARS_PER_SECOND = 4.5  # 中文语速的粗略经验值，仅用于 silent provider 估算时长


async def _synthesize_edge(text: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(out_path))


def _synthesize_silent(text: str, out_path: Path) -> None:
    duration = max(2.0, len(text) / CHARS_PER_SECOND)
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", f"{duration:.2f}",
            "-c:a", "libmp3lame",
            str(out_path),
        ],
        check=True,
        capture_output=True,
    )


def get_audio_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def synthesize_scene_audio(text: str, out_path: Path) -> float:
    """合成一段配音，返回实际音频时长（秒），供后续画面/字幕按真实时长对齐。"""
    if settings.tts_provider == "silent":
        _synthesize_silent(text, out_path)
    else:
        asyncio.run(_synthesize_edge(text, out_path))
    return get_audio_duration(out_path)
