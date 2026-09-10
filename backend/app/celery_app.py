"""Celery 应用入口。启动 worker：`celery -A app.celery_app worker --loglevel=info`。

worker 是独立进程，不会经过 FastAPI 的 startup 事件，所以这里在导入 models（保证
Base.metadata 已经注册所有表）之后主动建表，保证 worker 单独启动时数据库也是就绪的。
"""

from celery import Celery

from . import models  # noqa: F401  确保表结构在 create_all 前完成注册
from .config import settings
from .db import Base, engine

celery_app = Celery(
    "poem_animator",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

Base.metadata.create_all(bind=engine)

from . import tasks  # noqa: F401  导入以注册 Celery 任务
