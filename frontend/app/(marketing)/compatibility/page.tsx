"use client";

import { useState } from "react";
import { postCompatibility, type CompatReport } from "@/lib/api";
import {
  defaultSajuForm,
  formToHour,
  formToSolarDate,
  type SajuFormValue,
} from "@/lib/saju-form";
import { SajuDetailForm } from "@/components/fortune/SajuDetailForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function toPayload(v: SajuFormValue) {
  const { hour, time_unknown } = formToHour(v);
  return {
    solar_date: formToSolarDate(v),
    hour,
    minute: 0,
    gender: v.gender,
    time_unknown,
    calendar_type: v.calendar_type,
    display_name: v.display_name.trim() || v.label,
    time_slot: v.time_slot,
  };
}

function PersonCard({
  title,
  value,
  onChange,
}: {
  title: string;
  value: SajuFormValue;
  onChange: (v: SajuFormValue) => void;
}) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--card-bg)] p-4">
      <div className="mb-3 text-center text-sm font-bold text-[var(--primary)]">{title}</div>
      <SajuDetailForm value={value} onChange={onChange} showRelation={false} compact />
    </div>
  );
}

function ScoreBar({ label, value }: { label: string; value: number | null | undefined }) {
  if (value == null) {
    return (
      <div className="text-xs text-[var(--muted)]">
        {label}: <span className="font-medium">시주 미상 · 제외</span>
      </div>
    );
  }
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span>{label}</span>
        <span className="font-semibold">{value}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[var(--border)]">
        <div
          className="h-full rounded-full bg-[var(--primary)]"
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}

export default function CompatibilityPage() {
  const [a, setA] = useState<SajuFormValue>(() => ({
    ...defaultSajuForm(),
    display_name: "나",
    label: "본인",
    gender: "male",
  }));
  const [b, setB] = useState<SajuFormValue>(() => ({
    ...defaultSajuForm(),
    display_name: "상대",
    label: "애인",
    gender: "female",
    birth_year: 1992,
    birth_month: 8,
    birth_day: 20,
  }));
  const [result, setResult] = useState<CompatReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await postCompatibility(toPayload(a), toPayload(b));
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 pb-20">
      <h1 className="text-center text-2xl font-extrabold">사주 궁합</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        양력·음력 · 12시진 · 성별을 넣으면 일간·오행·지지까지 상세 분석합니다
      </p>
      <p className="mt-1 text-center text-[11px] text-[var(--muted)]">
        예전에 날짜·성별만 받던 방식은 시주·음력을 반영하지 못해 점수만 짧게 나왔습니다. 지금은
        입력한 달력·시간으로 사주를 다시 짜서 비교합니다.
      </p>

      <div className="mt-8 grid gap-4 lg:grid-cols-2">
        <PersonCard title="사람 A" value={a} onChange={setA} />
        <PersonCard title="사람 B" value={b} onChange={setB} />
      </div>

      <Button className="mt-6 w-full" disabled={loading} onClick={() => void submit()}>
        {loading ? "분석 중…" : "상세 궁합 보기"}
      </Button>
      {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-8 space-y-4">
          <Card className="border-[var(--primary)] bg-[var(--primary-light)]">
            <CardHeader className="pb-2 text-center">
              <CardDescription className="text-xs">종합 궁합 (참고 점수)</CardDescription>
              <CardTitle className="text-4xl font-extrabold text-[var(--primary)]">
                {result.score}
                <span className="text-lg font-bold">점</span>
              </CardTitle>
              <p className="text-sm font-semibold">{result.grade}</p>
              <p className="text-xs text-[var(--muted)]">
                일간 {result.a_day_master} × {result.b_day_master} · {result.relation.label}
              </p>
              <p className="text-[10px] text-[var(--muted)]">
                A가 보는 B 십성: {result.relation.a_sees_b} · B가 보는 A: {result.relation.b_sees_a}
              </p>
            </CardHeader>
            <CardContent>
              <p className="text-center text-sm leading-7">{result.summary}</p>
            </CardContent>
          </Card>

          <div className="grid gap-3 sm:grid-cols-2">
            {[result.a, result.b].map((p) => (
              <Card key={p.display_name + p.solar_used} className="border-[var(--border)]">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">
                    {p.display_name}{" "}
                    <span className="text-xs font-normal text-[var(--muted)]">
                      ({p.gender_ko})
                    </span>
                  </CardTitle>
                  <CardDescription className="text-[11px] leading-relaxed">
                    {p.birth_input} → 계산 양력 {p.solar_used}
                    <br />
                    {p.time_text}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-1 text-sm">
                  <p>
                    일간{" "}
                    <strong className="text-[var(--primary)]">{p.day_master}</strong>{" "}
                    <span className="text-xs text-[var(--muted)]">({p.day_master_nature})</span>
                  </p>
                  <p className="font-mono text-xs text-[var(--primary)]">{p.pillars_line}</p>
                  <p className="text-xs text-[var(--muted)]">{p.elements_line}</p>
                  <p className="text-[11px]">
                    강 {p.strong} · 약 {p.weak}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">항목별 점수</CardTitle>
              <CardDescription className="text-xs">
                참고 지표입니다. 투자·결혼 등 결정은 당사자 합의를 우선하세요.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <ScoreBar label="일간 관계" value={result.breakdown.day_master} />
              <ScoreBar label="오행 보완" value={result.breakdown.five_elements} />
              <ScoreBar label="일지" value={result.breakdown.day_branch} />
              <ScoreBar label="년·월지" value={result.breakdown.year_month} />
              <ScoreBar label="시지" value={result.breakdown.hour} />
            </CardContent>
          </Card>

          {result.sections.map((s) => (
            <Card key={s.id} className="border-[var(--border)]">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-[var(--primary)]">{s.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-line text-sm leading-7">{s.body}</p>
              </CardContent>
            </Card>
          ))}

          <p className="text-center text-[10px] leading-relaxed text-[var(--muted)]">
            {result.disclaimer}
          </p>
        </div>
      )}
    </main>
  );
}
