"use client";

import { useState } from "react";
import { postTarot, type TarotCard } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TarotPage() {
  const [count, setCount] = useState(1);
  const [question, setQuestion] = useState("");
  const [cards, setCards] = useState<TarotCard[] | null>(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const draw = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await postTarot(count, question);
      setCards(res.cards);
      setSummary(res.summary);
    } catch (e) {
      setError(e instanceof Error ? e.message : "실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-xl px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">타로 카드</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        질문을 떠올리고 카드를 뽑아 보세요
      </p>

      <div className="mt-8 space-y-4 rounded-2xl border border-[var(--border)] bg-[var(--card-bg)] p-5">
        <div>
          <label className="mb-1 block text-xs font-medium text-[var(--muted)]">질문 (선택)</label>
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="예: 이번 주 이직 운은?"
          />
        </div>
        <div className="flex gap-2">
          {[1, 3, 5].map((n) => (
            <Button
              key={n}
              type="button"
              variant={count === n ? "default" : "outline"}
              onClick={() => setCount(n)}
            >
              {n}장
            </Button>
          ))}
        </div>
        <Button className="w-full" disabled={loading} onClick={() => void draw()}>
          {loading ? "섞는 중…" : "카드 뽑기"}
        </Button>
        {error && <p className="text-center text-sm text-red-600">{error}</p>}
      </div>

      {cards && (
        <div className="mt-8 space-y-4">
          <p className="text-center text-sm text-[var(--muted)]">{summary}</p>
          {cards.map((c) => (
            <Card key={`${c.id}-${c.position}`} className="border-[var(--border)]">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">
                  {c.position}: {c.name}
                  {c.reversed ? " (역방향)" : " (정방향)"}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm leading-relaxed text-[var(--muted)]">
                {c.meaning}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </main>
  );
}
