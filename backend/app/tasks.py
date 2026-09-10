"""Celery 任务：把同步的 run_pipeline 包装成异步任务，供 /generate 接口投递。"""

from . import models
from .celery_app import celery_app
from .db import SessionLocal
from .models import Task, TaskStatus
from .pipeline.runner import run_pipeline


@celery_app.task(name="generate_video")
def generate_video_task(task_id: str) -> None:
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return

        try:
            run_pipeline(db, task)
        except Exception:  # noqa: BLE001  run_pipeline 内部已把 failed 状态和 error_message 落库，Celery 任务本身无需再抛出/重试
            return

        if task.status == TaskStatus.completed and task.result_video_url:
            exists = db.query(models.Work).filter(models.Work.query == task.query).first()
            if not exists:
                db.add(
                    models.Work(
                        query=task.query,
                        query_type=task.query_type,
                        video_url=task.result_video_url,
                    )
                )
                db.commit()
    finally:
        db.close()
