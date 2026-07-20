"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { getPrimaryFullReport, postTopicFortune } from "@/lib/api";

const PRESETS = [
  { q: "이직해도 될까?", topic: "work" as const },
  { q: "그 사람 마음은?", topic: "love" as const },
  { q: "돈 흐름이 어때?", topic: "money" as const },
  { q: "컨디션 관리는?", topic: "health" as const },
];

/** Rule-based Q&A (local mock for LLM path — no external API key). */
export default function AskPage() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const ask = async (question: string, topic?: "love" | "money" | "work" | "health") => {
    setLoading(true);
    setError("");
    setAnswer("");
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("질문형 운세는 로그인 후 이용할 수 있습니다.");
        return;
      }
      const pr = await getPrimaryFullReport();
      const body = {
        solar_date: pr.profile.solar_date,
        hour: pr.profile.hour ?? 12,
        minute: pr.profile.minute ?? 0,
        gender: (pr.profile.gender === "female" ? "female" : "male") as "male" | "female",
        time_unknown: pr.profile.time_unknown,
      };
      const t =
        topic ||
        (question.includes("연애") || question.includes("사람")
          ? "love"
          : question.includes("돈") || question.includes("재물")
            ? "money"
            : question.includes("건강") || question.includes("컨디션")
              ? "health"
              : "work");
      const data = await postTopicFortune(t, body);
      const dm = pr.report.day_master;
      setAnswer(
        `【질문】 ${question}\n\n` +
          `일간 ${dm} 기준으로 본 답변입니다.\n\n` +
          `${data.headline} (점수 ${data.score})\n\n` +
          data.sections.map((s) => `■ ${s.title}\n${s.body}`).join("\n\n") +
          `\n\n실천: ${data.lucky.action}\n\n` +
          `(로컬 규칙 기반 답변 · 외부 LLM 연동 시 더 자연스러운 대화로 확장 가능)`
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-xl px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">질문형 운세</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        궁금한 걸 고르거나 직접 물어보세요 (규칙 기반 로컬 AI)
      </p>

      <div className="mt-6 flex flex-wrap justify-center gap-2">
        {PRESETS.map((p) => (
          <Button
            key={p.q}
            size="sm"
            variant="outline"
            onClick={() => {
              setQ(p.q);
              void ask(p.q, p.topic);
            }}
          >
            {p.q}
          </Button>
        ))}
      </div>

      <div className="mt-6 flex gap-2">
        <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="질문을 입력…" />
        <Button disabled={loading || !q.trim()} onClick={() => void ask(q)}>
          {loading ? "…" : "묻기"}
        </Button>
      </div>

      {error && <p className="mt-4 text-center text-sm text-red-600">{error}</p>}

      {answer && (
        <Card className="mt-6 border-[var(--border)]">
          <CardContent className="pt-6">
            <p className="whitespace-pre-wrap text-sm leading-7">{answer}</p>
          </CardContent>
        </Card>
      )}
    </main>
  );
}
