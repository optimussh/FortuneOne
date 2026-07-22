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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.all([getStoreMenu(), getStoreProducts(cat || undefined)])
      .then(([menu, list]) => {
        setCategories(menu.categories || []);
        setProducts(list.products || []);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "실패"))
      .finally(() => setLoading(false));
  }, [cat]);

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 pb-20">
      <h1 className="text-center text-2xl font-extrabold">운세 스토어</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        샘플 사이트 메뉴·상품 구조를 벤치마크한 FortuneOne 카탈로그 · 문구는 자체 스타일
      </p>
      <p className="mt-1 text-center text-[11px] text-[var(--muted)]">
        결제 후 회원 사주 프로필 기준으로 결과가 생성됩니다 (로컬 모의 결제)
      </p>

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
                구성: {(p.result_sections || []).slice(0, 3).join(" · ")}
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
