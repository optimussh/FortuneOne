"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  getPrimaryFullReport,
  postTopicFortune,
  type ReportSection,
  type SajuRequestBody,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const LABELS: Record<string, string> = {
  love: "연애·관계",
  money: "재물·기회",
  work: "일·학업",
  health: "건강·컨디션",
};

export default function TopicPage() {
  const params = useParams();
  const slug = String(params.slug || "love");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [headline, setHeadline] = useState("");
  const [score, setScore] = useState(0);
  const [sections, setSections] = useState<ReportSection[]>([]);
  const [lucky, setLucky] = useState<{ color: string; action: string } | null>(null);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError("");
      try {
        let body: SajuRequestBody | null = null;
        const token = localStorage.getItem("token");
        if (token) {
          try {
            const pr = await getPrimaryFullReport();
            body = {
              solar_date: pr.profile.solar_date,
              hour: pr.profile.hour ?? 12,
              minute: pr.profile.minute ?? 0,
              gender: pr.profile.gender === "female" ? "female" : "male",
              time_unknown: pr.profile.time_unknown,
            };
          } catch {
            /* fallthrough */
          }
        }
        if (!body) {
          const raw = sessionStorage.getItem("fortune:last");
          if (raw) {
            const j = JSON.parse(raw);
            body = {
              solar_date: j.input.solar_date,
              hour: j.input.hour,
              minute: j.input.minute,
              gender: j.input.gender === "female" ? "female" : "male",
              time_unknown: j.input.time_assumed,
            };
          }
        }
        if (!body) {
          setError("사주 정보가 없습니다. 홈에서 사주를 보거나 로그인해 주세요.");
          setLoading(false);
          return;
        }
        const topic = (["love", "money", "work", "health"].includes(slug)
          ? slug
          : "love") as "love" | "money" | "work" | "health";
        const data = await postTopicFortune(topic, body);
        setTitle(data.title);
        setHeadline(data.headline);
        setScore(data.score);
        setSections(data.sections);
        setLucky(data.lucky);
      } catch (e) {
        setError(e instanceof Error ? e.message : "실패");
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [slug]);

  return (
    <main className="mx-auto max-w-xl px-4 py-10">
      <div className="mb-4 flex flex-wrap justify-center gap-2">
        {Object.entries(LABELS).map(([k, v]) => (
          <Link
            key={k}
            href={`/topics/${k}`}
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              k === slug ? "bg-[var(--primary)] text-white" : "border border-[var(--border)]"
            }`}
          >
            {v}
          </Link>
        ))}
      </div>

      {loading && <p className="text-center text-sm text-[var(--muted)]">불러오는 중…</p>}
      {error && (
        <div className="text-center">
          <p className="text-sm text-red-600">{error}</p>
          <Button asChild className="mt-4" size="sm">
            <Link href="/">사주 입력</Link>
          </Button>
        </div>
      )}

      {!loading && !error && (
        <>
          <h1 className="text-center text-2xl font-extrabold">{title || LABELS[slug]}</h1>
          <p className="mt-2 text-center text-3xl font-bold text-[var(--primary)]">{score}</p>
          <p className="mt-2 text-center text-sm text-[var(--muted)]">{headline}</p>
          <div className="mt-8 space-y-4">
            {sections.map((s) => (
              <Card key={s.id} className="border-[var(--border)]">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{s.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-7">{s.body}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          {lucky && (
            <p className="mt-6 text-center text-sm">
              행운 색 <strong>{lucky.color}</strong> · 실천: {lucky.action}
            </p>
          )}
          <div className="mt-8 text-center">
            <Button asChild variant="outline">
              <Link href="/hub">허브로</Link>
            </Button>
          </div>
        </>
      )}
    </main>
  );
}
