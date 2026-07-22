"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getStoreProductResult } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function ResultInner() {
  const { id } = useParams<{ id: string }>();
  const sp = useSearchParams();
  const profileId = Number(sp.get("profile_id") || 0);
  const partnerId = sp.get("partner_id") ? Number(sp.get("partner_id")) : undefined;
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [report, setReport] = useState<Awaited<
    ReturnType<typeof getStoreProductResult>
  >["report"] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace(`/login?next=/store/${id}/result?profile_id=${profileId}`);
      return;
    }
    if (!profileId) {
      setError("profile_id가 필요합니다");
      return;
    }
    getStoreProductResult(id, profileId, partnerId)
      .then((r) => setReport(r.report))
      .catch((e) => setError(e instanceof Error ? e.message : "실패"));
  }, [user, authLoading, id, profileId, partnerId, router]);

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

      <Card className="mt-6 border-[var(--border)]">
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
