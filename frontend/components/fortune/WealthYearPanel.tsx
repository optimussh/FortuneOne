"use client";

import { useMemo, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { MingshiTable, WealthYearReport } from "@/lib/api";

function MingshiMini({ table }: { table: MingshiTable }) {
  const cols = table.columns;
  return (
    <div className="overflow-x-auto rounded-xl border border-[var(--border)]">
      <table className="w-full min-w-[300px] border-collapse text-center text-sm">
        <thead>
          <tr className="bg-[var(--primary-light)] text-xs text-[var(--muted)]">
            <th className="border-b border-[var(--border)] px-2 py-2">구분</th>
            {cols.map((c) => (
              <th key={c.key} className="border-b border-[var(--border)] px-2 py-2">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border-b border-[var(--border)] px-2 py-1 text-xs text-[var(--muted)]">
              천간
            </td>
            {cols.map((c) => (
              <td
                key={c.key}
                className="border-b border-[var(--border)] px-2 py-2 text-lg font-bold text-[var(--primary)]"
              >
                {c.stem}
              </td>
            ))}
          </tr>
          <tr>
            <td className="border-b border-[var(--border)] px-2 py-1 text-xs text-[var(--muted)]">
              십성
            </td>
            {cols.map((c) => (
              <td key={c.key} className="border-b border-[var(--border)] px-2 py-1 text-xs">
                {c.stem_god}
              </td>
            ))}
          </tr>
          <tr>
            <td className="border-b border-[var(--border)] px-2 py-1 text-xs text-[var(--muted)]">
              지지
            </td>
            {cols.map((c) => (
              <td key={c.key} className="border-b border-[var(--border)] px-2 py-2 text-lg font-bold">
                {c.branch}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-2 py-1 text-xs text-[var(--muted)]">십성</td>
            {cols.map((c) => (
              <td key={c.key} className="px-2 py-1 text-xs">
                {c.branch_god}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

type Sub = "overview" | "months" | "calendar" | "export";

const SCORE_COLORS: Record<number, string> = {
  90: "#16a34a",
  80: "#22c55e",
  70: "#84cc16",
  60: "#eab308",
  50: "#f97316",
  40: "#ef4444",
  30: "#b91c1c",
};

export function WealthYearPanel({ data }: { data: WealthYearReport }) {
  const [sub, setSub] = useState<Sub>("overview");
  const [month, setMonth] = useState(() => Math.min(12, Math.max(1, new Date().getMonth() + 1)));
  const [expandedDay, setExpandedDay] = useState<number | null>(null);
  const [showLong, setShowLong] = useState(true);

  const calMonth = useMemo(
    () => data.calendar.months.find((m) => m.month === month) || data.calendar.months[0],
    [data.calendar.months, month]
  );
  const monthMeta = data.month_guide.months.find((m) => m.month === month);

  const downloadTxt = () => {
    const blob = new Blob([data.export.body], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = data.export.filename_hint || `wealth-${data.year}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const printReport = () => {
    const w = window.open("", "_blank");
    if (!w) return;
    w.document.write(
      `<pre style="font-family:sans-serif;white-space:pre-wrap;padding:24px;line-height:1.6">${data.export.body
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")}</pre>`
    );
    w.document.close();
    w.focus();
    w.print();
  };

  const subs: { id: Sub; label: string }[] = [
    { id: "overview", label: "총론·재물운" },
    { id: "months", label: "월별 활용" },
    { id: "calendar", label: "재물 캘린더" },
    { id: "export", label: "저장·수익화" },
  ];

  const el = data.elements;

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-xl font-extrabold text-[var(--primary)]">{data.title}</h2>
        <p className="mt-1 text-xs text-[var(--muted)]">{data.subtitle}</p>
        <p className="mt-2 text-sm font-semibold">{data.header.age_text}</p>
        <p className="mt-1 text-xs text-[var(--muted)]">
          양력 {data.header.solar_text} · 음력 {data.header.lunar_text} · 시간 {data.header.time_text}
        </p>
        <p className="mt-1 font-mono text-xs text-[var(--primary)]">{data.header.pillars_line}</p>
      </div>

      <MingshiMini table={data.mingshi} />

      {/* P3 elements */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] p-3">
        <div className="mb-2 flex flex-wrap justify-between gap-2 text-xs">
          <span className="font-semibold">오행 비중 (참고)</span>
          <span>
            일주/강약 {el.strength_ratio} ·{" "}
            <strong className="text-[var(--primary)]">{el.strength}</strong>
          </span>
        </div>
        <div className="grid grid-cols-5 gap-1 text-center text-[10px]">
          {(["wood", "fire", "earth", "metal", "water"] as const).map((k) => (
            <div key={k} className="rounded-lg bg-white py-2 shadow-sm">
              <div className="font-bold">{el.labels[k]?.replace(/\(.*\)/, "") || k}</div>
              <div className="text-sm font-extrabold text-[var(--primary)]">
                {el.scaled[k] ?? 0}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* P3 daeun */}
      <div className="rounded-xl border border-[var(--border)] p-3">
        <p className="mb-2 text-xs font-semibold">대운 (십년 단위 · 간략)</p>
        <p className="mb-2 text-[10px] leading-relaxed text-[var(--muted)]">{data.daeun.intro}</p>
        <div className="flex gap-1 overflow-x-auto pb-1">
          {data.daeun.periods.map((p) => (
            <div
              key={p.index}
              className={`min-w-[4.5rem] shrink-0 rounded-lg border px-1.5 py-2 text-center text-[10px] ${
                p.is_current
                  ? "border-[var(--primary)] bg-[var(--primary-light)]"
                  : "border-[var(--border)]"
              }`}
            >
              <div className="font-semibold">{p.age_label}</div>
              <div className="mt-1 font-bold text-[var(--primary)]">{p.stem}</div>
              <div className="font-bold">{p.branch}</div>
              <div className="mt-0.5 text-[9px] text-[var(--muted)]">{p.stem_branch}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {subs.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => setSub(s.id)}
            className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
              sub === s.id
                ? "bg-[var(--primary)] text-white"
                : "border border-[var(--border)] bg-white"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {sub === "overview" && (
        <div className="space-y-3">
          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{data.overview.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-line text-sm leading-7">{data.overview.body}</p>
            </CardContent>
          </Card>
          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{data.year_money.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-line text-sm leading-7">{data.year_money.body}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {sub === "months" && (
        <div className="space-y-3">
          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{data.month_guide.title}</CardTitle>
              <CardDescription className="text-xs leading-relaxed">
                {data.month_guide.intro}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-3 flex flex-wrap gap-1">
                {data.month_guide.grades_legend.map((g) => (
                  <span
                    key={g.id}
                    className="rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
                    style={{ background: g.color }}
                  >
                    {g.label}
                  </span>
                ))}
              </div>
              <div className="grid grid-cols-4 gap-1 sm:grid-cols-6">
                {data.month_guide.months.map((m) => (
                  <button
                    key={m.month}
                    type="button"
                    onClick={() => {
                      setMonth(m.month);
                      setSub("calendar");
                    }}
                    className="rounded-lg border border-[var(--border)] p-2 text-center text-[10px] hover:border-[var(--primary)]"
                  >
                    <div className="font-bold">{m.month}월</div>
                    <div
                      className="mt-1 rounded-full px-1 py-0.5 text-white"
                      style={{ background: m.grade_color }}
                    >
                      {m.grade_label}
                    </div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
          {data.month_guide.months.map((m) => (
            <Card key={m.month} className="border-[var(--border)]">
              <CardHeader className="pb-1">
                <CardTitle className="flex items-center justify-between text-sm">
                  <span>
                    {m.title}{" "}
                    <span className="font-mono text-xs text-[var(--muted)]">{m.ganzhi}</span>
                  </span>
                  <span
                    className="rounded-full px-2 py-0.5 text-[10px] text-white"
                    style={{ background: m.grade_color }}
                  >
                    {m.grade_label}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-7">{m.body}</p>
                <button
                  type="button"
                  className="mt-2 text-xs font-semibold text-[var(--primary)] underline"
                  onClick={() => {
                    setMonth(m.month);
                    setSub("calendar");
                  }}
                >
                  {m.month}월 일자별 캘린더 →
                </button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {sub === "calendar" && calMonth && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-1">
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => {
                  setMonth(m);
                  setExpandedDay(null);
                }}
                className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                  month === m
                    ? "bg-[var(--primary)] text-white"
                    : "border border-[var(--border)] bg-white"
                }`}
              >
                {m}월
              </button>
            ))}
          </div>
          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{calMonth.title}</CardTitle>
              <CardDescription className="text-xs">
                {data.calendar.note}
                {monthMeta ? ` · 월 등급 ${monthMeta.grade_label}` : ""}
              </CardDescription>
              <div className="flex flex-wrap gap-1 pt-1">
                {data.calendar.score_legend.map((s) => (
                  <span key={s.score} className="text-[10px] text-[var(--muted)]">
                    <span
                      className="mr-0.5 inline-block h-2 w-2 rounded-full"
                      style={{ background: SCORE_COLORS[s.score] }}
                    />
                    {s.score} {s.label}
                  </span>
                ))}
              </div>
              <label className="mt-2 flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  checked={showLong}
                  onChange={(e) => setShowLong(e.target.checked)}
                />
                장문 해석 표시 (P4)
              </label>
            </CardHeader>
            <CardContent className="space-y-2">
              {calMonth.days.map((d) => {
                const open = expandedDay === d.day;
                return (
                  <button
                    key={d.day}
                    type="button"
                    onClick={() => setExpandedDay(open ? null : d.day)}
                    className="w-full rounded-xl border border-[var(--border)] p-3 text-left transition hover:border-[var(--primary)]"
                  >
                    <div className="flex items-start gap-2">
                      <div
                        className="flex h-10 w-10 shrink-0 flex-col items-center justify-center rounded-lg text-xs font-bold text-white"
                        style={{ background: SCORE_COLORS[d.score] || "#888" }}
                      >
                        <span>{d.day}</span>
                        <span className="text-[9px] font-normal">{d.score}</span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-1 text-xs">
                          <span className="font-bold">
                            {d.day}일({d.weekday})
                          </span>
                          <span className="text-[var(--muted)]">{d.score_label}</span>
                          {d.shinsal?.map((t) => (
                            <span
                              key={t}
                              className="rounded bg-[var(--primary-light)] px-1.5 py-0.5 text-[10px] font-semibold text-[var(--primary)]"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                        <p className="mt-1 text-sm leading-6 text-[var(--foreground)]">
                          {showLong && d.body_long ? d.body_long : d.body}
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </CardContent>
          </Card>
        </div>
      )}

      {sub === "export" && (
        <div className="space-y-3">
          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">저장 · 인쇄 (P4)</CardTitle>
              <CardDescription className="text-xs">
                텍스트 내려받기 또는 브라우저 인쇄로 PDF 저장이 가능합니다.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              <Button size="sm" onClick={downloadTxt}>
                TXT 다운로드
              </Button>
              <Button size="sm" variant="outline" onClick={printReport}>
                인쇄 / PDF
              </Button>
            </CardContent>
          </Card>

          <Card className="border-dashed border-[var(--primary)] bg-[var(--primary-light)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">수익화 미리보기 (미적용)</CardTitle>
              <CardDescription className="text-xs leading-relaxed">
                {data.monetization.message}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {data.monetization.concepts.map((c) => (
                <div key={c.id} className="rounded-xl border border-[var(--border)] bg-white p-3">
                  <div className="font-bold">{c.name}</div>
                  {"unit_price_krw" in c && c.unit_price_krw != null && (
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      단가 약 {c.unit_price_krw}원 · 팩 구매 시 보너스
                    </p>
                  )}
                  {"packs" in c && c.packs && (
                    <ul className="mt-2 space-y-1 text-xs">
                      {c.packs.map((p) => (
                        <li key={p.count}>
                          {p.count}개 {p.price_krw.toLocaleString()}원
                          {p.bonus_pct
                            ? ` (+${p.bonus_pct}% 보너스 ${p.bonus_count ?? 0}개)`
                            : ""}
                        </li>
                      ))}
                    </ul>
                  )}
                  {"spend_hints" in c && c.spend_hints && (
                    <p className="mt-2 text-[10px] text-[var(--muted)]">
                      예상 소모: 월 해금 {c.spend_hints.month_unlock} · 일자 장문{" "}
                      {c.spend_hints.day_long} · 연간 캘린더{" "}
                      {c.spend_hints.full_year_calendar} · PDF {c.spend_hints.pdf_export}
                    </p>
                  )}
                  {"price_krw" in c && c.price_krw != null && (
                    <p className="mt-1 text-xs">
                      {c.price_krw.toLocaleString()}원 — {c.covers}
                    </p>
                  )}
                </div>
              ))}
              <p className="text-[10px] text-[var(--muted)]">{data.disclaimer}</p>
            </CardContent>
          </Card>
        </div>
      )}

      <p className="text-center text-[10px] text-[var(--muted)]">{data.disclaimer}</p>
    </div>
  );
}
