"use client";

import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { SajuResponse, StemBranch } from "@/lib/api";

const PILLAR_LABELS: { key: keyof SajuResponse["pillars"]; label: string }[] = [
  { key: "year", label: "년주" },
  { key: "month", label: "월주" },
  { key: "day", label: "일주" },
  { key: "hour", label: "시주" },
];

const ELEMENT_META: { key: string; label: string; color: string }[] = [
  { key: "wood", label: "목", color: "#22c55e" },
  { key: "fire", label: "화", color: "#ef4444" },
  { key: "earth", label: "토", color: "#d97706" },
  { key: "metal", label: "금", color: "#a1a1aa" },
  { key: "water", label: "수", color: "#3b82f6" },
];

const SCORE_LABELS: Record<string, string> = {
  overall: "총운",
  love: "애정",
  money: "금전",
  health: "건강",
};

function PillarCell({
  label,
  value,
}: {
  label: string;
  value: StemBranch | null | undefined;
}) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-[var(--border)] bg-[var(--background)] px-2 py-4">
      <span className="mb-2 text-xs font-medium text-[var(--muted)]">{label}</span>
      {value ? (
        <>
          <span className="text-2xl font-bold tracking-wide text-[var(--primary)]">
            {value.stem}
          </span>
          <span className="mt-1 text-2xl font-bold tracking-wide">{value.branch}</span>
        </>
      ) : (
        <span className="py-4 text-sm text-[var(--muted)]">—</span>
      )}
    </div>
  );
}

export function SajuResult({ data }: { data: SajuResponse }) {
  const maxElement = Math.max(1, ...Object.values(data.elements));
  const scores = data.daily.scores ?? {};
  const lucky = data.daily.lucky ?? {};

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-8 sm:py-12">
      <div className="text-center">
        <h1 className="text-2xl font-extrabold sm:text-3xl">사주 결과</h1>
        <p className="mt-2 text-sm text-[var(--muted)]">
          양력 {data.input.solar_date}
          {!data.input.time_assumed &&
            ` · ${String(data.input.hour).padStart(2, "0")}:${String(data.input.minute).padStart(2, "0")}`}
          {data.input.time_assumed && " · 시간 미상(정오 가정)"}
          {" · "}
          {data.input.gender === "female" ? "여성" : "남성"}
        </p>
        <p className="mt-1 text-sm">
          일간(Day Master):{" "}
          <span className="font-bold text-[var(--primary)]">{data.day_master}</span>
        </p>
      </div>

      <Card className="border-[var(--border)] bg-[var(--card-bg)]">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">사주 원국 (사주팔자)</CardTitle>
          <CardDescription className="text-[var(--muted)]">
            천간 · 지지
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-2 sm:gap-3">
            {PILLAR_LABELS.map(({ key, label }) => (
              <PillarCell key={key} label={label} value={data.pillars[key]} />
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-[var(--border)] bg-[var(--card-bg)]">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">오행 분포</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {ELEMENT_META.map(({ key, label, color }) => {
            const count = data.elements[key] ?? 0;
            const pct = Math.round((count / maxElement) * 100);
            return (
              <div key={key} className="flex items-center gap-3">
                <span className="w-8 text-sm font-semibold" style={{ color }}>
                  {label}
                </span>
                <div className="h-3 flex-1 overflow-hidden rounded-full bg-[var(--secondary)]">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${pct}%`, backgroundColor: color }}
                  />
                </div>
                <span className="w-6 text-right text-sm tabular-nums text-[var(--muted)]">
                  {count}
                </span>
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Card className="border-[var(--border)] bg-[var(--card-bg)]">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">오늘의 운세</CardTitle>
          <CardDescription className="text-[var(--muted)]">
            {data.daily.date}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-5">
          <p className="leading-relaxed text-[var(--foreground)]">{data.daily.summary}</p>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {Object.entries(scores).map(([key, value]) => (
              <div
                key={key}
                className="rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-3 text-center"
              >
                <div className="text-xs text-[var(--muted)]">
                  {SCORE_LABELS[key] ?? key}
                </div>
                <div className="mt-1 text-2xl font-bold text-[var(--primary)]">
                  {value}
                </div>
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-4 rounded-xl border border-[var(--border)] bg-[var(--primary-light)] px-4 py-3 text-sm">
            {lucky.color && (
              <div>
                <span className="text-[var(--muted)]">행운 색 · </span>
                <span className="font-semibold">{lucky.color}</span>
              </div>
            )}
            {lucky.direction && (
              <div>
                <span className="text-[var(--muted)]">행운 방향 · </span>
                <span className="font-semibold">{lucky.direction}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center gap-3 pb-8">
        <Button asChild variant="outline">
          <Link href="/">다시 입력</Link>
        </Button>
      </div>
    </div>
  );
}

export function SajuResultEmpty() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-4 px-4 py-20 text-center">
      <h1 className="text-xl font-bold">결과가 없습니다</h1>
      <p className="text-sm text-[var(--muted)]">
        사주 입력 후 결과를 확인할 수 있습니다.
      </p>
      <Button asChild>
        <Link href="/">사주 입력하러 가기</Link>
      </Button>
    </div>
  );
}
