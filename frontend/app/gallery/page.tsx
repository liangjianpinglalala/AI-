"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { API_BASE_URL, Work, listWorks } from "../../lib/api";

const QUERY_TYPE_LABELS: Record<string, string> = {
  poem: "古诗",
  idiom: "成语",
};

export default function GalleryPage() {
  const [works, setWorks] = useState<Work[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listWorks()
      .then(setWorks)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "获取作品库失败")
      );
  }, []);

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">作品库</h1>
        <Link href="/" className="text-neutral-500 hover:text-neutral-900">
          ← 返回首页
        </Link>
      </div>

      {error && <p className="text-red-500">{error}</p>}

      {works && works.length === 0 && (
        <p className="text-neutral-500">
          还没有生成过作品，回首页输入一首古诗或成语试试吧。
        </p>
      )}

      {works && works.length > 0 && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {works.map((work) => (
            <div
              key={work.id}
              className="flex flex-col gap-2 rounded-lg border border-neutral-200 bg-white p-3 shadow-sm"
            >
              {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
              <video
                controls
                preload="metadata"
                className="w-full rounded"
                src={`${API_BASE_URL}${work.video_url}`}
              />
              <div className="flex items-center justify-between">
                <span className="font-medium">{work.query}</span>
                <span className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs text-neutral-500">
                  {QUERY_TYPE_LABELS[work.query_type] ?? work.query_type}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
