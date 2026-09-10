"""Step 7 / 总控：把 content_retrieval -> script_generation -> tts -> images ->
subtitles -> render 串成一条流水线，驱动 Task 状态机（Phase 1 为同步执行；Phase 2
会把它包装进 Celery 任务，接口不变）。
"""

from pathlib import Path

from sqlalchemy.orm import Session

from ..config import settings
from ..models import Task, TaskStatus
from . import content_retrieval, images, render, script_generation, subtitles, tts


def _set_status(db: Session, task: Task, status: TaskStatus) -> None:
    task.status = status
    db.add(task)
    db.commit()
    db.refresh(task)


def run_pipeline(db: Session, task: Task) -> Task:
    task_dir = Path(settings.media_root) / task.id
    task_dir.mkdir(parents=True, exist_ok=True)

    try:
        _set_status(db, task, TaskStatus.fetching_content)
        content = content_retrieval.fetch_content(task.query)
        task.query_type = content.query_type
        db.add(task)
        db.commit()

        _set_status(db, task, TaskStatus.generating_script)
        script = script_generation.generate_script(content)

        _set_status(db, task, TaskStatus.synthesizing_audio)
        audio_paths: list[Path] = []
        durations: list[float] = []
        for scene in script.scenes:
            audio_path = task_dir / f"scene_{scene.scene_id:02d}.mp3"
            duration = tts.synthesize_scene_audio(scene.narration, audio_path)
            audio_paths.append(audio_path)
            durations.append(duration)

        _set_status(db, task, TaskStatus.generating_images)
        image_paths: list[Path] = []
        for scene in script.scenes:
            image_path = task_dir / f"scene_{scene.scene_id:02d}.png"
            images.generate_scene_image(scene, script.style_prefix, image_path)
            image_paths.append(image_path)

        _set_status(db, task, TaskStatus.building_subtitles)
        srt_path = task_dir / "subtitles.srt"
        subtitles.build_srt(script.scenes, durations, srt_path)

        _set_status(db, task, TaskStatus.rendering_video)
        out_path = task_dir / "final.mp4"
        render.render_final_video(
            images=image_paths,
            audios=audio_paths,
            durations=durations,
            srt_path=srt_path,
            work_dir=task_dir,
            out_path=out_path,
        )

        task.result_video_url = f"/media/{task.id}/final.mp4"
        _set_status(db, task, TaskStatus.completed)
        return task

    except Exception as exc:  # 流水线任意一步失败都要落库记录原因，供前端展示/排查
        task.error_message = str(exc)
        _set_status(db, task, TaskStatus.failed)
        raise
