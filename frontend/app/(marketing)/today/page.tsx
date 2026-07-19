"use client";

import { useEffect, useState } from "react";
import { getZodiacToday, type ZodiacItem } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TodayZodiacPage() {
  const [items, setItems] = useState<ZodiacItem[]>([]);
  const [date, setDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getZodiacToday()
      .then((res) => {
        setItems(res.items);
        setDate(res.date);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">띠별 오늘의 운세</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        {date || "…"} · 매일 갱신되는 12띠 가이드
      </p>

      {loading && <p className="mt-10 text-center text-sm text-[var(--muted)]">불러오는 중…</p>}
      {error && (
        <p className="mt-10 text-center text-sm text-red-600">
          {error} (API http://localhost:8000 실행 여부 확인)
        </p>
      )}

      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        {items.map((z) => (
          <Card key={z.zodiac} className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-base">
                <span>{z.zodiac}띠</span>
                <span className="text-lg font-bold text-[var(--primary)]">{z.score}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p className="leading-relaxed">{z.summary}</p>
              <p className="text-xs text-[var(--muted)]">
                행운색 {z.lucky_color} · DO {z.do} · DON&apos;T {z.dont}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}
