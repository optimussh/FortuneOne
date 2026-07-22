"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  getPrimaryFullReport,
  getProfileFullReport,
  getStreak,
  listFortuneProfiles,
  listJournal,
  postCheckin,
  upsertJournal,
  type FullReport,
  type FortuneProfile,
  type JournalEntry,
  type StreakInfo,
} from "@/lib/api";
import { getActiveProfileId, setActiveProfileId } from "@/lib/saju-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const TOPICS = [
  { slug: "love", label: "연애", emoji: "💕" },
  { slug: "money", label: "재물", emoji: "💰" },
  { slug: "work", label: "일·학업", emoji: "💼" },
  { slug: "health", label: "건강", emoji: "🌿" },
];

export default function HubPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [report, setReport] = useState<FullReport | null>(null);
  const [profile, setProfile] = useState<FortuneProfile | null>(null);
  const [streak, setStreak] = useState<StreakInfo | null>(null);
  const [journal, setJournal] = useState<JournalEntry | null>(null);
  const [note, setNote] = useState("");
  const [mood, setMood] = useState<number>(3);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const today = new Date().toISOString().slice(0, 10);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      await postCheckin("hub").then(setStreak).catch(() => getStreak().then(setStreak));
      try {
        const profiles = await listFortuneProfiles();
        let aid = getActiveProfileId();
        if (!aid || !profiles.some((p) => p.id === aid)) {
          const self = profiles.find((p) => p.is_self || p.label === "본인" || p.label === "나");
          aid = self?.id ?? profiles[0]?.id ?? null;
          if (aid) setActiveProfileId(aid);
        }
        const data = aid
          ? await getProfileFullReport(aid)
          : await getPrimaryFullReport();
        setProfile(data.profile);
        setReport(data.report);
      } catch {
        router.replace("/profiles");
        return;
      }
      const list = await listJournal().catch(() => [] as JournalEntry[]);
      const todayJ = list.find((j) => j.entry_date === today) || null;
      setJournal(todayJ);
      if (todayJ) {
        setNote(todayJ.body);
        setMood(todayJ.mood || 3);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "불러오기 실패");
    } finally {
      setLoading(false);
    }
  }, [router, today]);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/hub");
      return;
    }
    void load();
  }, [user, authLoading, router, load]);

  const saveJournal = async () => {
    setSaving(true);
    try {
      const row = await upsertJournal(today, { body: note, mood });
      setJournal(row);
    } catch (e) {
      setError(e instanceof Error ? e.message : "저장 실패");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <main className="px-4 py-20 text-center text-sm text-[var(--muted)]">허브 불러오는 중…</main>
    );
  }

  const scores = report?.daily?.scores || {};
  const lucky = report?.daily?.lucky || {};
  const oneLiner = report?.daily?.sections?.[0]?.body?.slice(0, 120) || report?.daily?.sections?.[0]?.body;

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 pb-20">
      <div className="mb-6 text-center">
        <p className="text-xs font-semibold text-[var(--primary)]">DAILY HUB</p>
        <h1 className="mt-1 text-2xl font-extrabold">
          안녕하세요
          {profile
            ? `, ${profile.display_name || profile.label}`
            : ""}
        </h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          {today}
          {profile ? ` · ${profile.label}` : ""}
        </p>
        <p className="mt-2 flex flex-wrap justify-center gap-x-3 gap-y-1 text-xs">
          <Link href="/profiles" className="font-semibold text-[var(--primary)] underline">
            사주 프로필
          </Link>
          <Link href="/me" className="font-semibold text-[var(--primary)] underline">
            상세 사주
          </Link>
          <Link href="/library" className="font-semibold text-[var(--primary)] underline">
            내 구매 · 다시보기
          </Link>
        </p>
      </div>

      {streak && (
        <div className="mb-4 space-y-2">
          <div className="flex items-center justify-center gap-3 rounded-2xl border border-[var(--border)] bg-[var(--card-bg)] px-4 py-3">
            <span className="text-2xl">🔥</span>
            <div>
              <div className="font-bold">{streak.current_streak}일 연속</div>
              <div className="text-xs text-[var(--muted)]">
                최고 {streak.longest_streak}일
                {streak.already_checked_in_today ? " · 오늘 출석 완료" : ""}
              </div>
            </div>
            <div className="ml-auto flex gap-1">
              {streak.recent_7.map((ok, i) => (
                <span
                  key={i}
                  className="h-2 w-2 rounded-full"
                  style={{ background: ok ? "#f59e0b" : "#e5e7eb" }}
                />
              ))}
            </div>
          </div>
          {streak.reward_message && (
            <p className="rounded-xl bg-amber-50 px-3 py-2 text-center text-xs font-semibold text-amber-900">
              {streak.reward_message}
              {streak.beads_awarded_today
                ? ` (+구슬 ${streak.beads_awarded_today})`
                : ""}
            </p>
          )}
          {streak.milestones && streak.milestones.length > 0 && (
            <div className="flex flex-wrap justify-center gap-2">
              {streak.milestones.map((m) => (
                <span
                  key={m.day}
                  className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ${
                    m.claimed
                      ? "bg-emerald-100 text-emerald-800"
                      : m.achieved
                        ? "bg-amber-100 text-amber-900"
                        : "border border-[var(--border)] text-[var(--muted)]"
                  }`}
                  title={`${m.label} · 구슬 ${m.beads}`}
                >
                  {m.label}
                  {m.claimed ? " ✓" : m.achieved ? " 보상!" : ` · ${m.beads}구슬`}
                </span>
              ))}
            </div>
          )}
          {streak.next_milestone && !streak.next_milestone.achieved && (
            <p className="text-center text-[10px] text-[var(--muted)]">
              다음 보상: {streak.next_milestone.label} (구슬 {streak.next_milestone.beads})
              · 앞으로 {streak.next_milestone.day - streak.current_streak}일
            </p>
          )}
        </div>
      )}

      {report && (
        <Card className="mb-6 border-[var(--border)]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-end justify-between">
              <span>오늘의 운세</span>
              <span className="text-3xl font-extrabold text-[var(--primary)]">
                {scores.overall ?? "—"}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="leading-relaxed text-[var(--muted)]">{oneLiner}…</p>
            <div className="flex flex-wrap gap-3 text-xs">
              {lucky.color && <span>색 {lucky.color}</span>}
              {lucky.direction && <span>방향 {lucky.direction}</span>}
              {lucky.number && <span>숫자 {lucky.number}</span>}
            </div>
            <div className="flex flex-wrap gap-2">
              <Button asChild size="sm" variant="outline">
                <Link href="/me">자세히 읽기 (상세 사주)</Link>
              </Button>
              <Button asChild size="sm">
                <Link href="/me?tab=tojeong">2026 토정 보기</Link>
              </Button>
              <Button asChild size="sm" variant="secondary">
                <Link href="/me?tab=wealth">2026 부자되기</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="mb-4 border-dashed border-[var(--border)]">
        <CardContent className="py-3 text-center text-[11px] leading-relaxed text-[var(--muted)]">
          오늘은 허브에서 한눈에, 깊은 주제는{" "}
          <Link href="/store" className="font-semibold text-[var(--primary)] underline">
            스토어
          </Link>
          에서 · 산 결과는{" "}
          <Link href="/library" className="font-semibold text-[var(--primary)] underline">
            다시보기
          </Link>
        </CardContent>
      </Card>

      <div className="mb-6 grid gap-3 sm:grid-cols-2">
        <Card className="border-[var(--primary)] bg-[var(--primary-light)]">
          <CardContent className="flex items-center justify-between gap-3 py-4">
            <div>
              <p className="text-sm font-bold">2026 토정 (기본)</p>
              <p className="mt-0.5 text-xs text-[var(--muted)]">종합 · 월별 12 · 영역운</p>
            </div>
            <Button asChild size="sm">
              <Link href="/me?tab=tojeong">보기</Link>
            </Button>
          </CardContent>
        </Card>
        <Card className="border-amber-500/50 bg-amber-50">
          <CardContent className="flex items-center justify-between gap-3 py-4">
            <div>
              <p className="text-sm font-bold text-amber-900">2026 부자되기 (기본)</p>
              <p className="mt-0.5 text-xs text-amber-800/80">월 등급 · 일자 캘린더</p>
            </div>
            <Button asChild size="sm" className="bg-amber-700 hover:bg-amber-800">
              <Link href="/me?tab=wealth">보기</Link>
            </Button>
          </CardContent>
        </Card>
        <Card className="border-[var(--border)] sm:col-span-2">
          <CardContent className="flex items-center justify-between gap-3 py-4">
            <div>
              <p className="text-sm font-bold">운세 스토어 (심화)</p>
              <p className="mt-0.5 text-xs text-[var(--muted)]">
                연애·결혼·재물·직장 주제 패키지 · 모의 결제
              </p>
            </div>
            <Button asChild size="sm" variant="outline">
              <Link href="/store">둘러보기</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="mb-6 grid grid-cols-3 gap-2 sm:grid-cols-3">
        {TOPICS.map((t) => (
          <Link
            key={t.slug}
            href={`/topics/${t.slug}`}
            className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] p-3 text-center transition hover:border-[var(--primary)]"
          >
            <div className="text-xl">{t.emoji}</div>
            <div className="mt-1 text-xs font-semibold">{t.label}</div>
          </Link>
        ))}
        <Link
          href="/tarot/daily"
          className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] p-3 text-center transition hover:border-[var(--primary)]"
        >
          <div className="text-xl">🃏</div>
          <div className="mt-1 text-xs font-semibold">오늘의 타로</div>
        </Link>
        <Link
          href="/journal"
          className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] p-3 text-center transition hover:border-[var(--primary)]"
        >
          <div className="text-xl">📓</div>
          <div className="mt-1 text-xs font-semibold">일기</div>
        </Link>
        <Link
          href="/compatibility"
          className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] p-3 text-center transition hover:border-[var(--primary)]"
        >
          <div className="text-xl">💞</div>
          <div className="mt-1 text-xs font-semibold">궁합</div>
        </Link>
      </div>

      <Card className="border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">오늘 한 줄 일기</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-center gap-2">
            {[1, 2, 3, 4, 5].map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMood(m)}
                className={`text-xl ${mood === m ? "scale-125" : "opacity-40"}`}
              >
                {["", "😞", "😐", "🙂", "😊", "🤩"][m]}
              </button>
            ))}
          </div>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            maxLength={1000}
            rows={3}
            placeholder="오늘 운세와 하루를 한 줄로…"
            className="w-full rounded-xl border border-[var(--border)] p-3 text-sm"
          />
          <Button size="sm" onClick={() => void saveJournal()} disabled={saving}>
            {saving ? "저장 중…" : journal ? "수정 저장" : "일기 남기기"}
          </Button>
        </CardContent>
      </Card>

      {error && <p className="mt-4 text-center text-sm text-red-600">{error}</p>}

      <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">
        <Link href="/me" className="text-[var(--primary)] underline">
          상세 사주
        </Link>
        <Link href="/me?tab=tojeong" className="text-[var(--primary)] underline">
          2026 토정
        </Link>
        <Link href="/me?tab=wealth" className="text-[var(--primary)] underline">
          2026 부자되기
        </Link>
        <Link href="/shop" className="text-[var(--primary)] underline">
          구슬 상점
        </Link>
        <Link href="/store" className="text-[var(--primary)] underline">
          운세 스토어
        </Link>
        <Link href="/library" className="text-[var(--primary)] underline">
          내 구매 · 다시보기
        </Link>
        <Link href="/about/engines" className="text-[var(--primary)] underline">
          엔진·라이선스
        </Link>
        <Link href="/today" className="text-[var(--primary)] underline">
          띠별
        </Link>
        <Link href="/share" className="text-[var(--primary)] underline">
          공유 카드
        </Link>
      </div>
    </main>
  );
}
