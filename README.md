# 诗成动画

输入一个古诗名或成语，全自动（零人工干预）生成讲解动画视频：Agent 自主完成脚本、配音、画面、字幕、剪辑、导出全流程。

详细方案见：

- [`docs/DESIGN.md`](docs/DESIGN.md) — 网站设计方案（前端/后端/Agent 流水线）
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — 技术路线与分阶段实施计划

## 目录结构

```
.
├── frontend/   # Next.js 前端
├── backend/    # FastAPI 后端 + 任务队列
├── agent/      # Agent 编排 prompt 模板
├── infra/      # Docker Compose 等部署配置
└── docs/       # 设计文档
```

## 本地开发（Phase 0）

### 后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
# 访问 http://localhost:8000/health
```

需要系统安装 `ffmpeg` 和一款中文字体（如 `fonts-wqy-zenhei`），否则视频渲染/字幕烧录会失败或中文显示为方块（`apt-get install -y ffmpeg fonts-wqy-zenhei`；Docker 镜像已内置）。

生成任务改成异步了（Phase 2），还需要 Redis + Celery worker：

```bash
redis-server --daemonize yes            # 或用你自己的 Redis 实例
celery -A app.celery_app worker --loglevel=info   # 另开一个终端，在 backend/ 目录下执行
```

提交生成任务（立即返回 `pending`，由 worker 异步执行）：

```bash
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{"query": "静夜思"}'
# 拿到 {"id": "...", "status": "pending", ...}，轮询查看进度：
curl http://localhost:8000/tasks/<id>
```

在 `backend/.env` 中未配置 `ANTHROPIC_API_KEY` 时，把 `CONTENT_PROVIDER` 设为 `mock` 可用内置示例数据跑通除 Claude 之外的流程；把 `TTS_PROVIDER` 设为 `silent` 可在没有公网访问的环境下用静音占位音频跑通渲染流程（详见 `backend/.env.example` 注释）。

### 前端

```bash
cd frontend
cp .env.local.example .env.local   # 配置后端地址 NEXT_PUBLIC_API_BASE_URL
npm install
npm run dev
# 访问 http://localhost:3000，搜索后会跳转到 /status/[id] 轮询进度并播放结果视频
```

### 一键启动（Docker Compose）

```bash
cd infra
docker compose up --build
```

## 当前进度

见 [`docs/ROADMAP.md`](docs/ROADMAP.md) 中的里程碑检查表，**Phase 2 已完成**：Celery/Redis 异步执行流水线、`/status/[id]` 轮询展示分步进度、完成后播放/下载、`/gallery` 作品库页，均已在浏览器中验证过完整用户路径。产物迁移到对象存储 + CDN 待确定云服务商后再接入（当前是本地磁盘 + FastAPI 静态文件服务）。
