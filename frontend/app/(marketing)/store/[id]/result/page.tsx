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
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (authLoading) return;
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
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          <Button asChild>
            <Link href={`/store/${id}/checkout`}>결제·프로필 선택</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/library">내 구매 · 다시보기</Link>
          </Button>
        </div>
      </main>
    );
  }

  if (!report) {
    return (
      <main className="py-20 text-center text-sm text-[var(--muted)]">
        결과를 준비하고 있어요…
      </main>
    );
  }

  const h = report.header as {
    display_name?: string;
    day_master?: string;
    day_master_nature?: string;
    pillars_line?: string;
    elements_line?: string;
  };
  const emailLink = access?.email_result_link
    ? String(access.email_result_link)
    : "";
  const sections = report.sections || [];

  const copyEmailLink = async () => {
    if (!emailLink) return;
    try {
      await navigator.clipboard.writeText(emailLink);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };

  return (
    <main className="mx-auto max-w-2xl px-4 py-10 pb-24">
      <p className="text-center text-xs font-semibold tracking-wide text-[var(--primary)]">
        결과 · {sections.length}단 구성
      </p>
      <h1 className="mt-2 text-center text-xl font-extrabold leading-snug sm:text-2xl">
        {report.product.title}
      </h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        {h.display_name}
        {h.day_master ? ` · 일간 ${h.day_master}` : ""}
        {h.day_master_nature ? ` · ${h.day_master_nature}` : ""}
      </p>
      {h.pillars_line && (
        <p className="mt-1 text-center font-mono text-xs text-[var(--primary)]">
          {h.pillars_line}
        </p>
      )}
      {h.elements_line && (
        <p className="mt-1 text-center text-[11px] text-[var(--muted)]">{h.elements_line}</p>
      )}

      {report.chart_facts && (
        <div className="mx-auto mt-4 max-w-md">
          <ChartFactsBadge facts={report.chart_facts} />
        </div>
      )}

      {access && (
        <Card className="mx-auto mt-4 max-w-md border-emerald-200 bg-emerald-50">
          <CardContent className="space-y-2 py-3 text-center text-[11px] leading-relaxed text-emerald-900">
            <p>
              <strong>다시보기</strong>{" "}
              {(access.policy as string) || "웹 7일 · 이메일 링크 30일"}
              {access.web_expires_at != null && (
                <>
                  {" · "}웹 만료 {String(access.web_expires_at).slice(0, 10)}
                  {access.days_left_web != null
                    ? ` (약 ${String(access.days_left_web)}일)`
                    : ""}
                </>
              )}
            </p>
            {emailLink ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="h-8 border-emerald-300 bg-white text-xs"
                onClick={() => void copyEmailLink()}
              >
                {copied ? "링크 복사됨" : "30일 메일용 링크 복사"}
              </Button>
            ) : null}
            <p>
              <Link href="/library" className="font-semibold underline">
                내 구매 목록에서 다시 열기
              </Link>
            </p>
          </CardContent>
        </Card>
      )}

      {/* TOC */}
      {sections.length > 2 && (
        <Card className="mt-5 border-[var(--border)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">목차</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="columns-1 gap-x-6 text-sm sm:columns-2">
              {sections.map((s, i) => (
                <li key={s.id} className="mb-1.5 break-inside-avoid">
                  <a
                    href={`#sec-${s.id}`}
                    className="text-[var(--primary)] underline-offset-2 hover:underline"
                  >
                    {i + 1}. {s.title}
                  </a>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      )}

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">서문</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-line text-sm leading-7 text-[var(--foreground)]">
            {report.intro}
          </p>
        </CardContent>
      </Card>

      {sections.map((s, i) => (
        <Card
          key={s.id}
          id={`sec-${s.id}`}
          className="mt-3 scroll-mt-20 border-[var(--border)]"
        >
          <CardHeader className="pb-2">
            <p className="text-[10px] font-semibold text-[var(--muted)]">
              {i + 1} / {sections.length}
            </p>
            <CardTitle className="text-base text-[var(--primary)]">{s.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-line text-sm leading-7">{s.body}</p>
          </CardContent>
        </Card>
      ))}

      <p className="mt-8 text-center text-[10px] leading-relaxed text-[var(--muted)]">
        {report.disclaimer}
        <br />
        {report.engine_note}
      </p>

      <div className="mt-8 flex flex-wrap justify-center gap-2">
        <Button asChild>
          <Link href="/library">내 구매 · 다시보기</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/store">스토어</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/me">상세 사주</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/hub">허브</Link>
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
