import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "诗成动画 · 古诗成语动画生成器",
  description: "输入一首古诗名或一个成语，自动生成解说动画，全程无需人工干预。",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-neutral-50 text-neutral-900">
        {children}
      </body>
    </html>
  );
}
