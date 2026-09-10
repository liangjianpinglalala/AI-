"use client";

import { useState } from "react";

export default function HomePage() {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO(Phase 1): 调用后端 POST /tasks 提交生成任务，跳转到进度页
    console.log("submit query:", query);
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
        />
        <button
          type="submit"
          className="rounded-lg bg-neutral-900 px-4 py-2 text-white hover:bg-neutral-700"
        >
          生成
        </button>
      </form>
    </main>
  );
}
