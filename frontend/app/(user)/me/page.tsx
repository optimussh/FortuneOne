"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  createFortuneProfile,
  getPrimaryFullReport,
  type FullReport,
  type FortuneProfile,
  type ReportSection,
} from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function SectionBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="mb-5 last:mb-0">
      <h4 className="mb-2 text-sm font-bold text-[var(--primary)]">{title}</h4>
      <p className="whitespace-pre-line text-sm leading-7 text-[var(--foreground)]">{body}</p>
    </div>
  );
}

function SectionsList({ sections }: { sections: ReportSection[] }) {
  return (
    <>
      {sections.map((s) => (
        <SectionBlock key={s.id} title={s.title} body={s.body} />
      ))}
    </>
  );
}

const TABS = [
  { id: "daily", label: "오늘의 운세" },
  { id: "newyear", label: "2026 신년" },
  { id: "five", label: "오행 사주" },
  { id: "life", label: "인생풀이" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function MePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [report, setReport] = useState<FullReport | null>(null);
  const [profile, setProfile] = useState<FortuneProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<TabId>("daily");

  // onboarding if no profile
  const [needSaju, setNeedSaju] = useState(false);
  const [solarDate, setSolarDate] = useState("");
  const [gender, setGender] = useState<"male" | "female">("male");
  const [timeUnknown, setTimeUnknown] = useState(true);
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(0);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    setNeedSaju(false);
    try {
      const data = await getPrimaryFullReport();
      setProfile(data.profile);
      setReport(data.report);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "불러오기 실패";
      if (msg.includes("프로필") || msg.includes("404") || msg.includes("없습니다")) {
        setNeedSaju(true);
        setReport(null);
        setProfile(null);
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/me");
      return;
    }
    void load();
  }, [user, authLoading, router, load]);

  const saveSaju = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!solarDate) {
      setError("생년월일을 입력하세요");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await createFortuneProfile({
        label: "나",
        solar_date: solarDate,
        hour: timeUnknown ? 12 : hour,
        minute: timeUnknown ? 0 : minute,
        time_unknown: timeUnknown,
        gender,
      });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "저장 실패");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-16 text-center text-sm text-[var(--muted)]">
        사주 리포트를 불러오는 중…
      </main>
    );
  }

  if (needSaju) {
    return (
      <main className="mx-auto max-w-md px-4 py-12">
        <h1 className="text-center text-2xl font-extrabold">사주 정보 등록</h1>
        <p className="mt-2 text-center text-sm text-[var(--muted)]">
          로그인 계정에 기본 사주를 등록하면 오늘의 운세·신년·인생풀이를 볼 수 있습니다.
        </p>
        <form onSubmit={saveSaju} className="mt-8 space-y-4 rounded-2xl border border-[var(--border)] p-5">
          <div>
            <label className="mb-1 block text-xs font-semibold">생년월일 (양력)</label>
            <Input type="date" required value={solarDate} onChange={(e) => setSolarDate(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <Button type="button" variant={gender === "male" ? "default" : "outline"} onClick={() => setGender("male")}>
              남성
            </Button>
            <Button
              type="button"
              variant={gender === "female" ? "default" : "outline"}
              onClick={() => setGender("female")}
            >
              여성
            </Button>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={timeUnknown} onChange={(e) => setTimeUnknown(e.target.checked)} />
            시간 모름
          </label>
          {!timeUnknown && (
            <div className="flex gap-2">
              <Input type="number" min={0} max={23} value={hour} onChange={(e) => setHour(Number(e.target.value))} />
              <Input
                type="number"
                min={0}
                max={59}
                value={minute}
                onChange={(e) => setMinute(Number(e.target.value))}
              />
            </div>
          )}
          {error && <p className="text-center text-sm text-red-600">{error}</p>}
          <Button type="submit" className="w-full" disabled={saving}>
            {saving ? "저장 중…" : "등록하고 운세 보기"}
          </Button>
        </form>
      </main>
    );
  }

  if (!report || !profile) {
    return (
      <main className="mx-auto max-w-md px-4 py-16 text-center">
        <p className="text-sm text-red-600">{error || "리포트가 없습니다"}</p>
        <Button className="mt-4" onClick={() => void load()}>
          다시 시도
        </Button>
      </main>
    );
  }

  const scores = report.daily.scores ?? {};
  const lucky = report.daily.lucky ?? {};

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 pb-20">
      <div className="mb-6 text-center">
        <p className="text-xs font-semibold tracking-wide text-[var(--primary)]">MY SAJU</p>
        <h1 className="mt-1 text-2xl font-extrabold sm:text-3xl">나의 상세 운세</h1>
        <p className="mt-2 text-sm text-[var(--muted)]">
          {profile.label} · 양력 {profile.solar_date}
          {profile.time_unknown ? " · 시간 미상" : ""} · 일간{" "}
          <span className="font-bold text-[var(--primary)]">{report.day_master}</span>
        </p>
      </div>

      {/* pillars strip */}
      <div className="mb-6 grid grid-cols-4 gap-2">
        {(
          [
            ["년", report.pillars.year],
            ["월", report.pillars.month],
            ["일", report.pillars.day],
            ["시", report.pillars.hour],
          ] as const
        ).map(([label, p]) => (
          <div
            key={label}
            className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] py-3 text-center"
          >
            <div className="text-[10px] text-[var(--muted)]">{label}</div>
            {p ? (
              <>
                <div className="text-lg font-bold text-[var(--primary)]">{p.stem}</div>
                <div className="text-lg font-bold">{p.branch}</div>
              </>
            ) : (
              <div className="py-2 text-muted">—</div>
            )}
          </div>
        ))}
      </div>

      {/* tabs */}
      <div className="mb-4 flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
              tab === t.id
                ? "bg-[var(--primary)] text-white"
                : "border border-[var(--border)] bg-white text-[var(--foreground)]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "daily" && (
        <Card className="border-[var(--border)]">
          <CardHeader>
            <CardTitle>{report.daily.title}</CardTitle>
            <CardDescription>
              총운 {scores.overall ?? "—"} · 애정 {scores.love ?? "—"} · 금전 {scores.money ?? "—"} ·
              건강 {scores.health ?? "—"}
              {lucky.color ? ` · 행운색 ${lucky.color}` : ""}
              {lucky.direction ? ` · ${lucky.direction}` : ""}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SectionsList sections={report.daily.sections} />
          </CardContent>
        </Card>
      )}

      {tab === "newyear" && (
        <Card className="border-[var(--border)]">
          <CardHeader>
            <CardTitle>{report.new_year_2026.title}</CardTitle>
            <CardDescription>{report.new_year_2026.subtitle}</CardDescription>
          </CardHeader>
          <CardContent>
            <SectionsList sections={report.new_year_2026.sections} />
          </CardContent>
        </Card>
      )}

      {tab === "five" && (
        <div className="space-y-4">
          <p className="text-center text-sm text-[var(--muted)]">{report.five_element.title}</p>
          {report.five_element.groups.map((g) => (
            <Card key={g.id} className="border-[var(--border)]">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{g.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-line text-sm leading-7">{g.body}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {tab === "life" && (
        <div className="space-y-4">
          <div className="text-center">
            <h2 className="text-lg font-bold">{report.life_reading.title}</h2>
            <p className="text-sm text-[var(--muted)]">{report.life_reading.subtitle}</p>
          </div>
          {report.life_reading.groups.map((g) => (
            <Card key={g.id} className="border-[var(--border)]">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{g.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <SectionsList sections={g.sections} />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {error && <p className="mt-4 text-center text-sm text-red-600">{error}</p>}

      <Card className="mt-8 border-dashed border-[var(--primary)] bg-[var(--primary-light)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">프리미엄 시즌 리포트 (미리보기)</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-[var(--muted)]">
          2026 하반기 심층 · AI 음성 상담 · 광고 없는 무제한 타로는 추후 오픈 예정입니다.
          지금은 전 기능 무료 로컬 체험 중이에요.
        </CardContent>
      </Card>

      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Button variant="outline" onClick={() => void load()}>
          새로고침
        </Button>
        <Button asChild variant="outline">
          <Link href="/hub">데일리 허브</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/share">공유 카드</Link>
        </Button>
        <Button asChild>
          <Link href="/ask">질문형 운세</Link>
        </Button>
      </div>
    </main>
  );
}
