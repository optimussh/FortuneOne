"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  buyBeadPack,
  buyWealthYear,
  getWallet,
  type MingshiTable,
  type WealthYearReport,
} from "@/lib/api";

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

type Sub = "overview" | "months" | "calendar" | "shop";

const SCORE_COLORS: Record<number, string> = {
  90: "#16a34a",
  80: "#22c55e",
  70: "#84cc16",
  60: "#eab308",
  50: "#f97316",
  40: "#ef4444",
  30: "#b91c1c",
};

export function WealthYearPanel({
  data,
  onUnlocked,
}: {
  data: WealthYearReport;
  onUnlocked?: () => void;
}) {
  const unlocked = Boolean(data.access?.unlocked ?? data.monetization?.unlocked);
  const price =
    data.access?.price_krw ??
    data.monetization?.price_krw ??
    data.monetization?.wealth_year?.price_krw ??
    3900;

  const [sub, setSub] = useState<Sub>("overview");
  const [month, setMonth] = useState(() => Math.min(12, Math.max(1, new Date().getMonth() + 1)));
  const [expandedDay, setExpandedDay] = useState<number | null>(null);
  const [showLong, setShowLong] = useState(true);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const [beads, setBeads] = useState<number | null>(null);

  const calMonth = useMemo(
    () => data.calendar.months.find((m) => m.month === month) || data.calendar.months[0],
    [data.calendar.months, month]
  );
  const monthMeta = data.month_guide.months.find((m) => m.month === month);

  const refreshWallet = async () => {
    try {
      const w = await getWallet();
      setBeads(w.beads);
    } catch {
      /* guest */
    }
  };

  useEffect(() => {
    void refreshWallet();
  }, []);

  const unlockYear = async () => {
    setBusy(true);
    setMsg("");
    try {
      const r = await buyWealthYear(data.year);
      setMsg(r.message);
      onUnlocked?.();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "해금 실패");
    } finally {
      setBusy(false);
    }
  };

  const buyPack = async (packId: string) => {
    setBusy(true);
    setMsg("");
    try {
      const r = await buyBeadPack(packId);
      setBeads(r.beads);
      setMsg(r.message);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "구매 실패");
    } finally {
      setBusy(false);
    }
  };

  const downloadTxt = () => {
    if (data.export.locked || !data.export.body) {
      setMsg(data.export.message || "해금 후 저장할 수 있습니다.");
      setSub("shop");
      return;
    }
    const blob = new Blob([data.export.body], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = data.export.filename_hint || `wealth-${data.year}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const printReport = () => {
    if (data.export.locked || !data.export.body) {
      setMsg(data.export.message || "해금 후 인쇄할 수 있습니다.");
      setSub("shop");
      return;
    }
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
    { id: "shop", label: "해금·구슬" },
  ];

  const el = data.elements;
  const packs = data.monetization?.packs || [];

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

      {/* Access banner */}
      <div
        className={`rounded-xl border px-3 py-3 text-sm ${
          unlocked
            ? "border-emerald-300 bg-emerald-50 text-emerald-900"
            : "border-amber-300 bg-amber-50 text-amber-950"
        }`}
      >
        <p className="font-semibold">
          {unlocked ? "전체 해금" : "무료 미리보기"}
          {beads != null ? ` · 구슬 ${beads}` : ""}
        </p>
        <p className="mt-1 text-xs leading-relaxed">
          {data.access?.message ||
            (unlocked
              ? "전체 내용을 볼 수 있습니다."
              : "총론 일부 · 월 등급 · 일부 일자만 공개됩니다.")}
        </p>
        {!unlocked && (
          <div className="mt-2 flex flex-wrap gap-2">
            <Button size="sm" disabled={busy} onClick={() => void unlockYear()}>
              {busy ? "처리 중…" : `연간 전체 해금 (모의 ${price.toLocaleString()}원)`}
            </Button>
            <Button size="sm" variant="outline" onClick={() => setSub("shop")}>
              구슬 충전
            </Button>
          </div>
        )}
        <p className="mt-2 text-[10px] opacity-80">
          점수·등급은 참고 지표이며 투자·재테크 권유가 아닙니다.
        </p>
      </div>

      {msg && (
        <p className="rounded-lg bg-[var(--primary-light)] px-3 py-2 text-center text-xs">{msg}</p>
      )}

      <MingshiMini table={data.mingshi} />

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
              <CardTitle className="flex items-center justify-between text-base">
                <span>{data.overview.title}</span>
                {data.overview.locked && (
                  <span className="text-[10px] font-normal text-amber-700">미리보기</span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-line text-sm leading-7">{data.overview.body}</p>
            </CardContent>
          </Card>
          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-base">
                <span>{data.year_money.title}</span>
                {data.year_money.locked && (
                  <span className="text-[10px] font-normal text-amber-700">미리보기</span>
                )}
              </CardTitle>
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
              <p className="mb-2 text-[10px] text-[var(--muted)]">
                무료: 월별 <strong>활용 등급</strong>만 공개 · 상세 본문은 해금 후
              </p>
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
            <Card
              key={m.month}
              className={`border-[var(--border)] ${m.locked ? "opacity-90" : ""}`}
            >
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
                {m.locked && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-2"
                    disabled={busy}
                    onClick={() => void unlockYear()}
                  >
                    월 상세 해금하기
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {sub === "calendar" && (
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
          {calMonth && (
            <Card className="border-[var(--border)]">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{calMonth.title}</CardTitle>
                <CardDescription className="text-xs">
                  {data.calendar.note}
                  {monthMeta ? ` · 월 등급 ${monthMeta.grade_label}` : ""}
                  {calMonth.preview_note ? ` · ${calMonth.preview_note}` : ""}
                </CardDescription>
                {unlocked && (
                  <label className="mt-2 flex items-center gap-2 text-xs">
                    <input
                      type="checkbox"
                      checked={showLong}
                      onChange={(e) => setShowLong(e.target.checked)}
                    />
                    장문 해석 표시
                  </label>
                )}
              </CardHeader>
              <CardContent className="space-y-2">
                {calMonth.locked || !calMonth.days?.length ? (
                  <div className="rounded-xl border border-dashed border-amber-400 bg-amber-50 p-4 text-center text-sm">
                    <p>{calMonth.lock_reason || "이 달은 미리보기에서 잠겨 있습니다."}</p>
                    <Button
                      size="sm"
                      className="mt-3"
                      disabled={busy}
                      onClick={() => void unlockYear()}
                    >
                      전체 캘린더 해금
                    </Button>
                  </div>
                ) : (
                  calMonth.days.map((d) => {
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
                              <span className="text-[9px] text-[var(--muted)]">참고</span>
                              {d.shinsal?.map((t) => (
                                <span
                                  key={t}
                                  className="rounded bg-[var(--primary-light)] px-1.5 py-0.5 text-[10px] font-semibold text-[var(--primary)]"
                                >
                                  {t}
                                </span>
                              ))}
                            </div>
                            <p className="mt-1 text-sm leading-6">
                              {showLong && unlocked && d.body_long ? d.body_long : d.body}
                            </p>
                            {d.long_locked && (
                              <p className="mt-1 text-[10px] text-amber-700">
                                장문은 연간 해금 후 제공됩니다.
                              </p>
                            )}
                          </div>
                        </div>
                      </button>
                    );
                  })
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {sub === "shop" && (
        <div className="space-y-3">
          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">저장 · 인쇄</CardTitle>
              <CardDescription className="text-xs">
                {data.export.locked
                  ? data.export.message || "해금 후 이용"
                  : "텍스트 내려받기 또는 브라우저 인쇄(PDF)"}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              <Button size="sm" onClick={downloadTxt} disabled={!!data.export.locked}>
                TXT 다운로드
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={printReport}
                disabled={!!data.export.locked}
              >
                인쇄 / PDF
              </Button>
            </CardContent>
          </Card>

          <Card className="border-amber-400 bg-amber-50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">부자되기 단건 해금</CardTitle>
              <CardDescription className="text-xs leading-relaxed">
                {data.year}년 총론 전문 · 월별 본문 · 365일 · 장문 · export
                <br />
                로컬 MVP는 <strong>모의 결제</strong> (실제 카드 청구 없음)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button disabled={busy || unlocked} onClick={() => void unlockYear()}>
                {unlocked
                  ? "이미 해금됨"
                  : `모의 결제 ${Number(price).toLocaleString()}원으로 해금`}
              </Button>
            </CardContent>
          </Card>

          <Card className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">구슬 충전</CardTitle>
              <CardDescription className="text-xs">
                타로 추가 뽑기 · 질문형(무료 1회/일 초과) · 다른 프로필 심화 등에 사용
                {beads != null ? ` · 보유 ${beads}개` : ""}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {(packs.length
                ? packs
                : [
                    {
                      id: "pack_100",
                      label: "구슬 100개",
                      total_beads: 100,
                      price_krw: 10000,
                      bonus_pct: 0,
                    },
                    {
                      id: "pack_200",
                      label: "구슬 200개 +10%",
                      total_beads: 220,
                      price_krw: 20000,
                      bonus_pct: 10,
                    },
                    {
                      id: "pack_500",
                      label: "구슬 500개 +15%",
                      total_beads: 575,
                      price_krw: 50000,
                      bonus_pct: 15,
                    },
                  ]
              ).map((p) => (
                <div
                  key={p.id}
                  className="flex items-center justify-between gap-2 rounded-xl border border-[var(--border)] bg-white px-3 py-2 text-sm"
                >
                  <div>
                    <div className="font-semibold">{p.label}</div>
                    <div className="text-[10px] text-[var(--muted)]">
                      {p.total_beads}개 · {p.price_krw.toLocaleString()}원
                      {p.bonus_pct ? ` (보너스 ${p.bonus_pct}%)` : ""}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busy}
                    onClick={() => void buyPack(p.id)}
                  >
                    모의 구매
                  </Button>
                </div>
              ))}
              <p className="text-[10px] text-[var(--muted)]">
                소모 예: 타로 추가 3 · 질문 2 · 다른 프로필 심화 5 구슬
              </p>
              <Button asChild size="sm" variant="secondary">
                <Link href="/shop">상점 페이지 열기</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      <p className="text-center text-[10px] text-[var(--muted)]">{data.disclaimer}</p>
    </div>
  );
}
