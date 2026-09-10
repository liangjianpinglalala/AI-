"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createGenerateTask } from "../lib/api";

export default function HomePage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || submitting) return;

    setSubmitting(true);
    setError(null);
    try {
      const task = await createGenerateTask(trimmed);
      router.push(`/status/${task.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成请求失败，请稍后重试");
      setSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <h1 className="text-3xl font-bold">诗成动画</h1>
      <p className="text-neutral-500">
        输入一首古诗名或一个成语，自动生成讲解动画
      </p>
      <form onSubmit={handleSubmit} className="flex w-full max-w-md gap-2">
        <input
          className="flex-1 rounded-lg border border-neutral-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-neutral-400"
          placeholder="例如：静夜思 / 画蛇添足"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={submitting}
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-neutral-900 px-4 py-2 text-white hover:bg-neutral-700 disabled:opacity-50"
        >
          {submitting ? "提交中…" : "生成"}
        </button>
      </form>
      {error && <p className="text-red-500">{error}</p>}
    </main>
  );
}
