# 技术路线

## 一、技术栈总览

| 模块 | 首选技术 | 备选方案 |
|---|---|---|
| 前端 | Next.js 14 + TypeScript + TailwindCSS | Vite + React |
| 后端 API | Python 3.11 + FastAPI | Node.js + Express |
| 任务队列 | Redis + Celery | Redis + RQ |
| 数据库 | PostgreSQL | SQLite（MVP） |
| 内容知识源 | 本地静态数据集 + SQLite 全文检索 | 向量库 (Chroma) |
| 脚本生成 | Anthropic SDK + Claude（structured output） | — |
| 配音 TTS | `edge-tts`（免费） | 阿里云/腾讯云 TTS、MiniMax |
| 画面生成 | 通义万相 / Replicate(SDXL) | 本地 Stable Diffusion |
| 动态效果 | Ken Burns（ffmpeg 实现） | 图生视频（Phase 3） |
| 字幕对齐 | TTS 时长切分 | faster-whisper 强制对齐 |
| 剪辑合成 | ffmpeg | Remotion |
| 对象存储 | Cloudflare R2 / 阿里云 OSS | 本地磁盘（demo） |
| 部署 | Docker Compose；前端 Vercel，后端 VPS/Railway | — |
| CI/CD | GitHub Actions | — |

## 二、分阶段实施路线

### Phase 0：项目脚手架（当前阶段）
- monorepo 结构：`frontend/` `backend/` `agent/` `infra/` `docs/`
- FastAPI 骨架 + `/health` 接口 + `tasks`/`works` 基础模型
- Next.js 骨架 + 首页搜索静态 UI
- Docker Compose（backend + frontend + postgres + redis）
- GitHub Actions 基础 lint/build

**验收标准**：`docker compose up` 能同时起前后端，前端可调通 `/health`。

### Phase 1：MVP 全链路打通（单线程同步版本）
1. `fetch_content(query)` → Claude 生成结构化诗词/成语信息
2. `generate_script(content)` → Claude 生成分镜 JSON
3. `synthesize_audio(scenes)` → edge-tts 逐句配音
4. `generate_images(scenes)` → 文生图 API，每 scene 一张图
5. `build_subtitles(scenes, audio_durations)` → 生成 `.srt`
6. `render_video(...)` → ffmpeg 拼接（图片+Ken Burns+字幕烧录+转场）
7. 落盘返回视频 URL

**验收标准**：输入“静夜思”，等待后能拿到包含字幕+配音+插画的 mp4。

### Phase 2：异步化 + 体验优化
- [x] Celery + Redis 异步任务，`POST /generate` 立即返回，前端轮询 `/tasks/{id}`
- [x] 每步状态落库（`fetching_content` → … → `completed`/`failed`）
- [x] `works` 缓存命中直接复用（Phase 1 已提前实现）
- [x] 分步进度条 UI（首页搜索 → `/status/[id]` 进度页 → 播放器+下载）
- [ ] 作品库/画廊页
- [ ] 产物迁移到对象存储 + CDN（当前仍是本地磁盘 + FastAPI 静态文件服务）

### Phase 3：质量与能力升级
- 图生视频动态画面 + 角色一致性
- 自检 Agent：脚本/字幕/时长自动校验，不合格自动重跑
- faster-whisper 精确字幕对齐
- 背景音乐库、用户账号、分享、社区

## 三、里程碑检查表

- [x] Phase 0：仓库骨架 + Docker Compose 跑通
- [x] Phase 1：单条同步链路能产出一个完整视频
- [ ] Phase 2：异步任务队列 + 进度展示 + 缓存复用上线
- [ ] Phase 3：动态画面 + 自检机制 + 用户功能
