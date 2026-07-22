"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getStoreProductResult } from "@/lib/api";
import { ChartFactsBadge } from "@/components/fortune/ChartFactsBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function ResultInner() {
  const { id } = useParams<{ id: string }>();
  const sp = useSearchParams();
  const profileId = Number(sp.get("profile_id") || 0);
  const partnerId = sp.get("partner_id") ? Number(sp.get("partner_id")) : undefined;
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const token = sp.get("token") || undefined;
  const [report, setReport] = useState<Awaited<
    ReturnType<typeof getStoreProductResult>
  >["report"] | null>(null);
  const [access, setAccess] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (authLoading) return;
    // email token allows view without login; web uses unlock row profile if omitted
    if (!token && !user) {
      const next = profileId
        ? `/store/${id}/result?profile_id=${profileId}`
        : `/store/${id}/result`;
      router.replace(`/login?next=${encodeURIComponent(next)}`);
      return;
    }
    getStoreProductResult(id, profileId || 0, partnerId, token)
      .then((r) => {
        setReport(r.report);
        setAccess((r.access as Record<string, unknown>) || null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "실패"));
  }, [user, authLoading, id, profileId, partnerId, token, router]);

  if (error) {
    return (
      <main className="mx-auto max-w-lg px-4 py-16 text-center">
        <p className="text-sm text-red-600">{error}</p>
        <Button asChild className="mt-4">
          <Link href={`/store/${id}/checkout`}>결제·프로필 선택으로</Link>
        </Button>
      </main>
    );
  }

  if (!report) {
    return (
      <main className="py-20 text-center text-sm text-[var(--muted)]">결과 생성 중…</main>
    );
  }

  const h = report.header as {
    display_name?: string;
    day_master?: string;
    pillars_line?: string;
    elements_line?: string;
  };

  return (
    <main className="mx-auto max-w-2xl px-4 py-10 pb-20">
      <p className="text-center text-xs font-semibold text-[var(--primary)]">RESULT</p>
      <h1 className="mt-2 text-center text-xl font-extrabold leading-snug">
        {report.product.title}
      </h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        {h.display_name} · 일간 {h.day_master}
      </p>
      <p className="mt-1 text-center font-mono text-xs text-[var(--primary)]">{h.pillars_line}</p>
      <p className="mt-1 text-center text-[11px] text-[var(--muted)]">{h.elements_line}</p>

      {report.chart_facts && (
        <div className="mx-auto mt-4 max-w-md">
          <ChartFactsBadge facts={report.chart_facts} />
        </div>
      )}

      {access && (
        <Card className="mx-auto mt-4 max-w-md border-emerald-200 bg-emerald-50">
          <CardContent className="py-3 text-center text-[11px] leading-relaxed text-emerald-900">
            <strong>다시보기</strong>:{" "}
            {(access.policy as string) || "웹 7일 · 이메일 링크 30일"}
            {access.web_expires_at != null && (
              <>
                <br />웹 만료: {String(access.web_expires_at).slice(0, 10)}
                {access.days_left_web != null ? ` (약 ${String(access.days_left_web)}일 남음)` : ""}
              </>
            )}
            {access.email_result_link ? (
              <>
                <br />
                <span className="break-all text-[10px]">
                  이메일용 링크(복사): {String(access.email_result_link)}
                </span>
              </>
            ) : null}
          </CardContent>
        </Card>
      )}

      <Card className="mt-4 border-dashed border-[var(--border)]">
        <CardContent className="py-3 text-center text-[11px] text-[var(--muted)]">
          이 결과는 <strong>스토어 주제 심화</strong>입니다. 기본 탭(신년·토정·부자되기)과
          역할이 다릅니다.{" "}
          <Link href="/me" className="text-[var(--primary)] underline">
            상세 사주
          </Link>
        </CardContent>
      </Card>

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">서문</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-7">{report.intro}</p>
        </CardContent>
      </Card>

      {report.sections.map((s) => (
        <Card key={s.id} className="mt-3 border-[var(--border)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-[var(--primary)]">{s.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-7">{s.body}</p>
          </CardContent>
        </Card>
      ))}

      <p className="mt-6 text-center text-[10px] leading-relaxed text-[var(--muted)]">
        {report.disclaimer}
        <br />
        {report.engine_note}
      </p>

      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Button asChild variant="outline">
          <Link href="/library">내 구매 · 다시보기</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/store">스토어</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/hub">허브</Link>
        </Button>
        <Button asChild>
          <Link href="/profiles">사주 프로필</Link>
        </Button>
      </div>
    </main>
  );
}

export default function StoreResultPage() {
  return (
    <Suspense fallback={<main className="py-20 text-center text-sm">로딩…</main>}>
      <ResultInner />
    </Suspense>
  );
}
