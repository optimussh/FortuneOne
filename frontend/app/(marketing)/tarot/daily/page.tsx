"use client";

import { TarotInteractive } from "@/components/tarot/TarotInteractive";
import Link from "next/link";

export default function DailyTarotPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">오늘의 타로</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">하루 한 장 · 직감으로 고르기</p>
      <div className="mt-8">
        <TarotInteractive mode="daily" />
      </div>
      <p className="mt-8 text-center text-sm">
        <Link href="/tarot" className="text-[var(--primary)] underline">
          다른 스프레드 보기
        </Link>
      </p>
    </main>
  );
}
