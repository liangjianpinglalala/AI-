"use client";

import { useEffect, useState } from "react";

import { API_BASE_URL, Task, TaskStatus, fetchTask } from "../../../lib/api";

const STEP_LABELS: Record<TaskStatus, string> = {
  pending: "排队中",
  fetching_content: "检索古诗/成语内容",
  generating_script: "生成分镜脚本",
  synthesizing_audio: "合成配音",
  generating_images: "生成画面",
  building_subtitles: "生成字幕",
  rendering_video: "剪辑合成视频",
  completed: "已完成",
  failed: "生成失败",
};

const STEP_ORDER: TaskStatus[] = [
  "pending",
  "fetching_content",
  "generating_script",
  "synthesizing_audio",
  "generating_images",
  "building_subtitles",
  "rendering_video",
  "completed",
];

const POLL_INTERVAL_MS = 2000;

export default function StatusPage({ params }: { params: { id: string } }) {
  const [task, setTask] = useState<Task | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    const poll = async () => {
      try {
        const data = await fetchTask(params.id);
        if (cancelled) return;
        setTask(data);
        setError(null);
        if (data.status !== "completed" && data.status !== "failed") {
          timer = setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "查询任务状态失败");
          timer = setTimeout(poll, POLL_INTERVAL_MS * 1.5);
        }
      }
    };

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [params.id]);

  const currentIndex = task ? STEP_ORDER.indexOf(task.status) : -1;
  const progressPercent =
    currentIndex >= 0
      ? Math.max(10, ((currentIndex + 1) / STEP_ORDER.length) * 100)
      : 5;

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <h1 className="text-2xl font-bold">{task ? task.query : "正在加载…"}</h1>

      {error && <p className="text-red-500">{error}</p>}

      {task && task.status !== "completed" && task.status !== "failed" && (
        <div className="w-full max-w-md">
          <div className="mb-2 text-neutral-600">
            {STEP_LABELS[task.status] ?? task.status}…
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-neutral-200">
            <div
              className="h-full bg-neutral-900 transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}

      {task && task.status === "failed" && (
        <p className="max-w-md text-center text-red-500">
          生成失败：{task.error_message}
        </p>
      )}

      {task && task.status === "completed" && task.result_video_url && (
        <div className="flex w-full max-w-2xl flex-col items-center gap-4">
          {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
          <video
            controls
            className="w-full rounded-lg shadow"
            src={`${API_BASE_URL}${task.result_video_url}`}
          />
          <a
            href={`${API_BASE_URL}${task.result_video_url}`}
            download
            className="rounded-lg bg-neutral-900 px-4 py-2 text-white hover:bg-neutral-700"
          >
            下载视频
          </a>
        </div>
      )}
    </main>
  );
}
