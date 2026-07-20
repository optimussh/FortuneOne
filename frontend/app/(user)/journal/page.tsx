"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { listJournal, type JournalEntry } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function JournalPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [items, setItems] = useState<JournalEntry[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/journal");
      return;
    }
    listJournal()
      .then(setItems)
      .catch((e) => setError(e instanceof Error ? e.message : "실패"));
  }, [user, authLoading, router]);

  return (
    <main className="mx-auto max-w-xl px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">운세 일기</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">기록한 하루를 돌아보세요</p>
      <div className="mt-4 text-center">
        <Button asChild size="sm">
          <Link href="/hub">오늘 일기 쓰러 가기</Link>
        </Button>
      </div>
      {error && <p className="mt-4 text-center text-sm text-red-600">{error}</p>}
      <div className="mt-8 space-y-3">
        {items.length === 0 && !error && (
          <p className="text-center text-sm text-[var(--muted)]">아직 일기가 없습니다.</p>
        )}
        {items.map((j) => (
          <Card key={j.id} className="border-[var(--border)]">
            <CardHeader className="pb-1">
              <CardTitle className="flex justify-between text-sm">
                <span>{j.entry_date}</span>
                <span>
                  {j.mood ? ["", "😞", "😐", "🙂", "😊", "🤩"][j.mood] : ""}
                  {j.linked_overall_score != null ? ` · 운세 ${j.linked_overall_score}` : ""}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{j.body || "(내용 없음)"}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}
