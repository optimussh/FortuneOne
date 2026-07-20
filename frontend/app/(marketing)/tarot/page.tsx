"use client";

import { TarotInteractive } from "@/components/tarot/TarotInteractive";
import Link from "next/link";

export default function TarotPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">타로 카드</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        카드를 펼친 뒤, 직접 골라 뒤집어 보세요
      </p>
      <div className="mt-4 text-center text-xs">
        <Link href="/tarot/daily" className="font-semibold text-[var(--primary)] underline">
          오늘의 1장 타로 →
        </Link>
      </div>
      <div className="mt-8">
        <TarotInteractive mode="free" />
      </div>
    </main>
  );
}
