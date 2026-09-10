"""Step 6：剪辑合成。用 ffmpeg 把每个场景的图片+音频拼成带 Ken Burns 效果的短片，
再拼接为完整视频并烧录字幕。
"""

import subprocess
from pathlib import Path

FPS = 25
SUBTITLE_FONT = "WenQuanYi Zen Hei"


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 命令失败: {' '.join(cmd)}\n{result.stderr[-4000:]}")


def render_scene_clip(image_path: Path, audio_path: Path, duration: float, out_path: Path) -> None:
    """单场景：静态图 + Ken Burns 缓慢缩放 + 首尾淡入淡出，时长与配音对齐。"""
    frames = max(1, int(duration * FPS))
    fade_out_start = max(duration - 0.4, 0.0)
    vf = (
        "scale=1600:900,"
        f"zoompan=z='min(zoom+0.0006,1.2)':d={frames}:s=1280x720:fps={FPS},"
        f"fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_start:.2f}:d=0.4"
    )
    _run(
        [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(image_path),
            "-i", str(audio_path),
            "-vf", vf,
            "-t", f"{duration:.2f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            str(out_path),
        ]
    )


def concat_clips(clip_paths: list[Path], out_path: Path) -> None:
    """用绝对路径写 concat 列表，避免相对路径在 cwd 切换后被错误地二次拼接。"""
    list_file = out_path.parent / "concat_list.txt"
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in clip_paths), encoding="utf-8"
    )
    _run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file.resolve()),
            "-c", "copy",
            str(out_path.resolve()),
        ]
    )


def burn_subtitles(video_path: Path, srt_path: Path, out_path: Path) -> None:
    """subtitles 滤镜的参数用 ':' 分隔，Windows 风格路径里的盘符冒号会被误判为分隔符；
    这里改用 cwd + 相对文件名规避转义问题，视频输入/输出仍用绝对路径，不依赖三者同目录。"""
    style = f"FontName={SUBTITLE_FONT},FontSize=20,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=1,MarginV=30"
    _run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path.resolve()),
            "-vf", f"subtitles={srt_path.name}:force_style='{style}'",
            "-c:a", "copy",
            str(out_path.resolve()),
        ],
        cwd=srt_path.parent,
    )


def render_final_video(
    images: list[Path],
    audios: list[Path],
    durations: list[float],
    srt_path: Path,
    work_dir: Path,
    out_path: Path,
) -> None:
    clip_paths = []
    for idx, (image, audio, duration) in enumerate(zip(images, audios, durations)):
        clip_path = work_dir / f"clip_{idx:02d}.mp4"
        render_scene_clip(image, audio, duration, clip_path)
        clip_paths.append(clip_path)

    merged_path = work_dir / "merged.mp4"
    concat_clips(clip_paths, merged_path)
    burn_subtitles(merged_path, srt_path, out_path)
