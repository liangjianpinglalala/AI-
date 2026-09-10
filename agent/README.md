# Agent 编排层

存放驱动“输入 -> 视频”流水线的 prompt 模板与编排逻辑，与后端 API 代码解耦，便于独立迭代调优。

## 流水线步骤

1. `content_retrieval` — 检索/校验古诗或成语的原文、作者、背景、含义
2. `script_generation` — 生成分镜脚本（旁白、字幕、画面 prompt、时长）
3. 配音（TTS）、画面生成、字幕对齐、剪辑合成 — 见 `backend/` 中对应 pipeline 步骤（Phase 1 起实现）

## 目录结构

```
agent/
├── prompts/                  # 各步骤的 prompt 模板
│   ├── content_retrieval.md
│   └── script_generation.md
└── README.md
```
