"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  getPrimaryFullReport,
  getStoreRecommend,
  postCheckin,
  type StoreProduct,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

/**
 * Onboarding after register: 오늘 한 줄 → 기본 탭 → 추천 스토어 (B8)
 */
export default function WelcomePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [oneLiner, setOneLiner] = useState("");
  const [score, setScore] = useState<number | null>(null);
  const [recs, setRecs] = useState<StoreProduct[]>([]);
  const [reward, setReward] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/welcome");
      return;
    }
    (async () => {
      try {
        const check = await postCheckin("hub").catch(() => null);
        if (check?.reward_message) setReward(check.reward_message);
        const data = await getPrimaryFullReport().catch(() => null);
        if (data?.report?.daily) {
          setScore(data.report.daily.scores?.overall ?? null);
          const body = data.report.daily.sections?.[0]?.body || "";
          setOneLiner(body.replace(/\n\n/g, " ").slice(0, 160));
        }
        const r = await getStoreRecommend(6);
        setRecs(r.products || []);
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading, router]);

  if (authLoading || loading) {
    return (
      <main className="px-4 py-20 text-center text-sm text-[var(--muted)]">
        환영 준비 중…
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-lg px-4 py-10 pb-24">
      <p className="text-center text-xs font-semibold text-[var(--primary)]">WELCOME</p>
      <h1 className="mt-1 text-center text-2xl font-extrabold">시작이 반가워요</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        점신·운세 앱처럼, 가입 직후 <strong className="text-[var(--foreground)]">오늘 한 줄</strong>
        부터 보여 드립니다
      </p>

      {reward && (
        <p className="mt-3 rounded-xl bg-amber-50 px-3 py-2 text-center text-xs font-semibold text-amber-900">
          {reward}
        </p>
      )}

      <Card className="mt-6 border-[var(--primary)] bg-[var(--primary-light)]">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-end justify-between text-base">
            <span>1. 오늘의 운세</span>
            {score != null && (
              <span className="text-2xl font-extrabold text-[var(--primary)]">{score}</span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p className="leading-relaxed text-[var(--muted)]">
            {oneLiner || "상세 사주에서 오늘 운세를 확인해 보세요."}
            {oneLiner ? "…" : ""}
          </p>
          <Button asChild className="w-full">
            <Link href="/me">자세히 읽기 (상세 사주)</Link>
          </Button>
        </CardContent>
      </Card>

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">2. 기본으로 제공되는 것</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 text-sm sm:grid-cols-2">
          {[
            { href: "/me?tab=tojeong", label: "2026 토정", desc: "종합·월별" },
            { href: "/me?tab=wealth", label: "2026 부자되기", desc: "월·일 캘린더" },
            { href: "/hub", label: "데일리 허브", desc: "출석·일기" },
            { href: "/tarot/daily", label: "일일 타로", desc: "카드 한 장" },
          ].map((x) => (
            <Link
              key={x.href}
              href={x.href}
              className="rounded-xl border border-[var(--border)] bg-white px-3 py-3 hover:border-[var(--primary)]"
            >
              <p className="font-semibold">{x.label}</p>
              <p className="text-[11px] text-[var(--muted)]">{x.desc}</p>
            </Link>
          ))}
        </CardContent>
      </Card>

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">3. 더 깊게 — 추천 주제</CardTitle>
          <p className="text-[11px] text-[var(--muted)]">
            기본 탭 다음에, 한 주제만 골라 스토어에서 심화
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          {recs.map((p) => (
            <Link
              key={p.id}
              href={`/store/${p.id}`}
              className="flex items-start justify-between gap-2 rounded-xl border border-[var(--border)] px-3 py-2.5 hover:border-[var(--primary)]"
            >
              <div className="min-w-0">
                <p className="text-[10px] font-semibold text-[var(--primary)]">
                  {p.hit ? "HIT · " : ""}
                  {p.category_label}
                </p>
                <p className="text-sm font-semibold leading-snug">{p.title}</p>
                {p.subtitle && (
                  <p className="mt-0.5 line-clamp-1 text-[11px] text-[var(--muted)]">
                    {p.subtitle}
                  </p>
                )}
              </div>
              <span className="shrink-0 text-sm font-bold text-amber-700">
                {p.is_free ? "무료" : `${p.price_krw.toLocaleString()}원`}
              </span>
            </Link>
          ))}
          <Button asChild variant="outline" className="mt-2 w-full">
            <Link href="/store">스토어 전체 보기</Link>
          </Button>
        </CardContent>
      </Card>

      <p className="mt-8 text-center text-xs text-[var(--muted)]">
        <Link href="/hub" className="font-semibold text-[var(--primary)] underline">
          허브로 이동
        </Link>
        {" · "}다음에 언제든 이 순서로 돌아오면 됩니다
      </p>
    </main>
  );
}
