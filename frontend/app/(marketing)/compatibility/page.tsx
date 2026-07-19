"use client";

import { useState } from "react";
import { postCompatibility } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Person = {
  solar_date: string;
  gender: "male" | "female";
};

const empty: Person = { solar_date: "", gender: "male" };

export default function CompatibilityPage() {
  const [a, setA] = useState<Person>(empty);
  const [b, setB] = useState<Person>({ ...empty, gender: "female" });
  const [result, setResult] = useState<{
    score: number;
    summary: string;
    a_day_master: string;
    b_day_master: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (!a.solar_date || !b.solar_date) {
      setError("두 사람의 생년월일을 입력하세요");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const body = (p: Person) => ({
        solar_date: p.solar_date,
        hour: 12,
        minute: 0,
        gender: p.gender,
        time_unknown: true,
      });
      const res = await postCompatibility(body(a), body(b));
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "실패");
    } finally {
      setLoading(false);
    }
  };

  const personForm = (
    title: string,
    p: Person,
    setP: (v: Person) => void
  ) => (
    <div className="space-y-3 rounded-xl border border-[var(--border)] p-4">
      <div className="font-semibold">{title}</div>
      <Input
        type="date"
        value={p.solar_date}
        onChange={(e) => setP({ ...p, solar_date: e.target.value })}
      />
      <div className="flex gap-2">
        <Button
          type="button"
          size="sm"
          variant={p.gender === "male" ? "default" : "outline"}
          onClick={() => setP({ ...p, gender: "male" })}
        >
          남성
        </Button>
        <Button
          type="button"
          size="sm"
          variant={p.gender === "female" ? "default" : "outline"}
          onClick={() => setP({ ...p, gender: "female" })}
        >
          여성
        </Button>
      </div>
    </div>
  );

  return (
    <main className="mx-auto max-w-xl px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">사주 궁합</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        두 사람의 생년월일로 일간·오행 보완 점수를 계산합니다
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {personForm("A", a, setA)}
        {personForm("B", b, setB)}
      </div>

      <Button className="mt-6 w-full" disabled={loading} onClick={() => void submit()}>
        {loading ? "분석 중…" : "궁합 보기"}
      </Button>
      {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}

      {result && (
        <Card className="mt-8 border-[var(--border)]">
          <CardHeader>
            <CardTitle className="text-center text-3xl text-[var(--primary)]">
              {result.score}점
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-center text-sm">
            <p>
              일간 {result.a_day_master} × {result.b_day_master}
            </p>
            <p className="leading-relaxed text-[var(--muted)]">{result.summary}</p>
          </CardContent>
        </Card>
      )}
    </main>
  );
}
