export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type TaskStatus =
  | "pending"
  | "fetching_content"
  | "generating_script"
  | "synthesizing_audio"
  | "generating_images"
  | "building_subtitles"
  | "rendering_video"
  | "completed"
  | "failed";

export interface Task {
  id: string;
  query: string;
  query_type: string | null;
  status: TaskStatus;
  error_message: string | null;
  result_video_url: string | null;
}

export async function createGenerateTask(query: string): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    throw new Error(`生成请求失败（${res.status}）`);
  }
  return res.json();
}

export async function fetchTask(id: string): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/tasks/${id}`);
  if (!res.ok) {
    throw new Error(`查询任务状态失败（${res.status}）`);
  }
  return res.json();
}

export interface Work {
  id: string;
  query: string;
  query_type: string;
  video_url: string;
  created_at: string;
}

export async function listWorks(): Promise<Work[]> {
  const res = await fetch(`${API_BASE_URL}/works`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`获取作品库失败（${res.status}）`);
  }
  return res.json();
}
