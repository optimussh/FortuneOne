"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { getStoreMenu, getStoreProducts, type StoreProduct } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function StoreInner() {
  const sp = useSearchParams();
  const cat = sp.get("cat") || "";
  const [categories, setCategories] = useState<{ id: string; label: string }[]>([]);
  const [products, setProducts] = useState<StoreProduct[]>([]);
  const [roleGuide, setRoleGuide] = useState<{
    free_tabs?: Record<string, string>;
    store?: string;
    summary?: string;
  } | null>(null);
  const [counts, setCounts] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.all([getStoreMenu(), getStoreProducts(cat || undefined)])
      .then(([menu, list]) => {
        setCategories(menu.categories || []);
        setProducts(list.products || []);
        setRoleGuide(menu.role_guide || list.role_guide || null);
        setCounts(list.category_counts || null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "실패"))
      .finally(() => setLoading(false));
  }, [cat]);

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 pb-20">
      <h1 className="text-center text-2xl font-extrabold">운세 스토어</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        주제별 심화 패키지 · 결제(모의) 후 내 사주 프로필로 결과 생성
      </p>

      {/* Role separation */}
      <Card className="mt-6 border-[var(--primary)] bg-[var(--primary-light)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">기본 탭 vs 스토어</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-xs leading-relaxed text-[var(--muted)]">
          <p className="font-semibold text-[var(--foreground)]">
            {roleGuide?.summary ||
              "상세 사주 탭은 기본 제공, 스토어는 주제를 더 깊게 파는 패키지입니다."}
          </p>
          <ul className="list-disc space-y-1 pl-4">
            <li>
              <Link href="/me" className="font-semibold text-[var(--primary)] underline">
                상세 사주
              </Link>
              : 오늘 · 신년 · 토정 · 부자되기 · 오행 · 인생풀이 (기본)
            </li>
            <li>
              <strong>스토어</strong>: 연애·결혼·재물·직장 등 주제 심화 (프로필 연동 결과)
            </li>
            <li>
              <Link href="/me?tab=wealth" className="underline text-[var(--primary)]">
                부자되기
              </Link>
              는 재물 캘린더, 스토어 재물 상품은 태도·습관 심화로 역할 분리
            </li>
          </ul>
          {counts && (
            <p className="pt-1 text-[10px]">
              분류 현황:{" "}
              {Object.entries(counts)
                .map(([k, v]) => `${k} ${v}`)
                .join(" · ")}
            </p>
          )}
        </CardContent>
      </Card>

      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <Link
          href="/store"
          className={`rounded-full px-3 py-1 text-xs font-semibold ${
            !cat ? "bg-[var(--primary)] text-white" : "border border-[var(--border)]"
          }`}
        >
          전체
        </Link>
        {categories.map((c) => (
          <Link
            key={c.id}
            href={`/store?cat=${c.id}`}
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              cat === c.id
                ? "bg-[var(--primary)] text-white"
                : "border border-[var(--border)]"
            }`}
          >
            {c.label}
            {counts?.[c.id] != null ? ` (${counts[c.id]})` : ""}
          </Link>
        ))}
      </div>

      {loading && (
        <p className="mt-10 text-center text-sm text-[var(--muted)]">불러오는 중…</p>
      )}
      {error && <p className="mt-6 text-center text-sm text-red-600">{error}</p>}

      <div className="mt-8 space-y-3">
        {products.map((p) => (
          <Card key={p.id} className="border-[var(--border)]">
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-[10px] font-semibold text-[var(--primary)]">
                    {p.category_label}
                  </p>
                  <CardTitle className="mt-1 text-base leading-snug">{p.title}</CardTitle>
                  {p.subtitle && (
                    <p className="mt-1 text-[11px] text-[var(--muted)]">{p.subtitle}</p>
                  )}
                </div>
                <div className="shrink-0 text-right">
                  <div className="text-lg font-extrabold text-amber-700">
                    {p.is_free ? "무료" : `${p.price_krw.toLocaleString()}원`}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-[11px] text-[var(--muted)]">
                구성 {(p.result_sections || []).length}단 ·{" "}
                {(p.result_sections || []).slice(0, 3).join(" · ")}
                {(p.result_sections || []).length > 3 ? " …" : ""}
              </p>
              <Button asChild size="sm">
                <Link href={`/store/${p.id}`}>상세 보기</Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {!loading && products.length === 0 && (
        <p className="mt-10 text-center text-sm text-[var(--muted)]">상품이 없습니다</p>
      )}
    </main>
  );
}

export default function StorePage() {
  return (
    <Suspense
      fallback={
        <main className="py-20 text-center text-sm text-[var(--muted)]">스토어 로딩…</main>
      }
    >
      <StoreInner />
    </Suspense>
  );
}
