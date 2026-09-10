import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, String, Text

from .db import Base


class QueryType(str, enum.Enum):
    poem = "poem"
    idiom = "idiom"


class TaskStatus(str, enum.Enum):
    pending = "pending"
    fetching_content = "fetching_content"
    generating_script = "generating_script"
    synthesizing_audio = "synthesizing_audio"
    generating_images = "generating_images"
    building_subtitles = "building_subtitles"
    rendering_video = "rendering_video"
    completed = "completed"
    failed = "failed"


class Task(Base):
    """一次“输入 -> 视频”生成请求的状态记录，驱动 Agent 流水线的进度展示。"""

    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String, nullable=False)
    query_type = Column(Enum(QueryType), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False)
    error_message = Column(Text, nullable=True)
    result_video_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Work(Base):
    """已完成的生成结果缓存，同一诗词/成语命中缓存时直接复用，不重复调用各类生成API。"""

    __tablename__ = "works"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String, unique=True, nullable=False, index=True)
    query_type = Column(Enum(QueryType), nullable=False)
    video_url = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
