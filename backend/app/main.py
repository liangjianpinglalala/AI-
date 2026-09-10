from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .db import Base, engine, get_db
from .models import Task, TaskStatus
from .pipeline.runner import run_pipeline

app = FastAPI(title="古诗成语动画生成 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    Path(settings.media_root).mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.media_root), name="media")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


class GenerateRequest(BaseModel):
    query: str


class TaskResponse(BaseModel):
    id: str
    query: str
    query_type: str | None
    status: TaskStatus
    error_message: str | None
    result_video_url: str | None

    class Config:
        from_attributes = True


@app.post("/generate", response_model=TaskResponse)
def generate(payload: GenerateRequest, db: Session = Depends(get_db)) -> Task:
    """Phase 1：同步执行完整流水线并返回最终状态（Phase 2 会改为提交任务立即返回，
    由前端轮询 /tasks/{id} 查看进度）。"""
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query 不能为空")

    cached = db.query(models.Work).filter(models.Work.query == query).first()
    task = Task(query=query)
    if cached:
        task.query_type = cached.query_type
        task.status = TaskStatus.completed
        task.result_video_url = cached.video_url
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    db.add(task)
    db.commit()
    db.refresh(task)

    task = run_pipeline(db, task)

    if task.status == TaskStatus.completed and task.result_video_url:
        work = models.Work(
            query=query,
            query_type=task.query_type,
            video_url=task.result_video_url,
        )
        db.add(work)
        db.commit()

    return task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
