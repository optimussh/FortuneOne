"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  getStoreMenu,
  getStoreProducts,
  getStoreRecommend,
  type StoreProduct,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

function ProductCard({ p }: { p: StoreProduct }) {
  const teaser =
    (p.intro_blurbs && p.intro_blurbs[0]) ||
    p.subtitle ||
    `${(p.result_sections || []).slice(0, 2).join(" · ")} 등 ${(p.result_sections || []).length}단 구성`;
  return (
    <Link href={`/store/${p.id}`} className="block">
      <Card className="border-[var(--border)] transition hover:border-[var(--primary)] hover:shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-[10px] font-semibold text-[var(--primary)]">
                {p.hit ? "HIT · " : ""}
                {p.category_label}
              </p>
              <CardTitle className="mt-1 text-base leading-snug">{p.title}</CardTitle>
              <p className="mt-1.5 line-clamp-2 text-[12px] leading-relaxed text-[var(--muted)]">
                {teaser}
              </p>
            </div>
            <div className="shrink-0 text-right">
              <div className="text-base font-extrabold text-amber-700">
                {p.is_free ? "무료" : `${p.price_krw.toLocaleString()}원`}
              </div>
              <p className="mt-1 text-[10px] text-[var(--muted)]">
                {(p.result_sections || []).length}단
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex items-center justify-between pt-0">
          <p className="text-[11px] text-[var(--muted)]">
            {(p.result_sections || []).slice(0, 3).join(" · ")}
            {(p.result_sections || []).length > 3 ? " …" : ""}
          </p>
          <span className="text-xs font-semibold text-[var(--primary)]">자세히 →</span>
        </CardContent>
      </Card>
    </Link>
  );
}

function StoreInner() {
  const sp = useSearchParams();
  const router = useRouter();
  const cat = sp.get("cat") || "";
  const qParam = sp.get("q") || "";
  const [categories, setCategories] = useState<{ id: string; label: string }[]>([]);
  const [products, setProducts] = useState<StoreProduct[]>([]);
  const [recs, setRecs] = useState<StoreProduct[]>([]);
  const [roleGuide, setRoleGuide] = useState<{
    free_tabs?: Record<string, string>;
    store?: string;
    summary?: string;
  } | null>(null);
  const [counts, setCounts] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [qInput, setQInput] = useState(qParam);

  useEffect(() => {
    setQInput(qParam);
  }, [qParam]);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getStoreMenu(),
      getStoreProducts(cat || undefined, qParam || undefined),
      !cat && !qParam ? getStoreRecommend(6) : Promise.resolve({ products: [] as StoreProduct[] }),
    ])
      .then(([menu, list, rec]) => {
        setCategories(menu.categories || []);
        setProducts(list.products || []);
        setRoleGuide(menu.role_guide || list.role_guide || null);
        setCounts(list.category_counts || null);
        setRecs(rec.products || []);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "실패"))
      .finally(() => setLoading(false));
  }, [cat, qParam]);

  const submitSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (cat) params.set("cat", cat);
    if (qInput.trim()) params.set("q", qInput.trim());
    const qs = params.toString();
    router.push(qs ? `/store?${qs}` : "/store");
  };

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 pb-20">
      <p className="text-center text-xs font-semibold tracking-wide text-[var(--primary)]">
        STORE
      </p>
      <h1 className="mt-1 text-center text-2xl font-extrabold">운세 스토어</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        연애·결혼·재물·직장 주제 심화 · 결제 후{" "}
        <strong className="text-[var(--foreground)]">내 사주 프로필</strong>로 결과 생성
      </p>
      <p className="mt-2 text-center text-xs">
        <Link href="/library" className="font-semibold text-[var(--primary)] underline">
          내 구매 · 다시보기
        </Link>
        <span className="text-[var(--muted)]"> · 웹 7일 · 메일 링크 30일</span>
      </p>

      <form onSubmit={submitSearch} className="mx-auto mt-5 flex max-w-md gap-2">
        <Input
          value={qInput}
          onChange={(e) => setQInput(e.target.value)}
          placeholder="연애, 이직, 결혼, 재물…"
          className="flex-1"
          aria-label="스토어 검색"
        />
        <Button type="submit" size="sm">
          검색
        </Button>
      </form>

      <Card className="mt-5 border-[var(--primary)] bg-[var(--primary-light)]">
        <CardContent className="space-y-1.5 py-3 text-xs leading-relaxed text-[var(--muted)]">
          <p className="font-semibold text-[var(--foreground)]">
            {roleGuide?.summary ||
              "상세 사주 탭은 기본, 스토어는 한 주제를 깊게 파는 패키지입니다."}
          </p>
          <p>
            <Link href="/me" className="font-semibold text-[var(--primary)] underline">
              상세 사주
            </Link>
            에서 오늘·신년·토정·부자되기를 본 뒤, 더 궁금한 주제만 골라 보세요.
          </p>
        </CardContent>
      </Card>

      {!cat && !qParam && recs.length > 0 && (
        <section className="mt-6">
          <h2 className="text-sm font-bold">추천 · 히트 주제</h2>
          <p className="mt-0.5 text-[11px] text-[var(--muted)]">
            벤치마크 기준 인기 축(연애·결혼·재물·직장) 우선
          </p>
          <div className="mt-3 space-y-2">
            {recs.map((p) => (
              <ProductCard key={`rec-${p.id}`} p={p} />
            ))}
          </div>
        </section>
      )}

      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <Link
          href={qParam ? `/store?q=${encodeURIComponent(qParam)}` : "/store"}
          className={`rounded-full px-3 py-1 text-xs font-semibold ${
            !cat ? "bg-[var(--primary)] text-white" : "border border-[var(--border)]"
          }`}
        >
          전체
        </Link>
        {categories.map((c) => {
          const href = qParam
            ? `/store?cat=${c.id}&q=${encodeURIComponent(qParam)}`
            : `/store?cat=${c.id}`;
          return (
            <Link
              key={c.id}
              href={href}
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                cat === c.id
                  ? "bg-[var(--primary)] text-white"
                  : "border border-[var(--border)]"
              }`}
            >
              {c.label}
              {counts?.[c.id] != null ? ` (${counts[c.id]})` : ""}
            </Link>
          );
        })}
      </div>

      {!loading && (
        <p className="mt-4 text-center text-[11px] text-[var(--muted)]">
          {products.length}개
          {qParam ? ` · “${qParam}” 검색` : cat ? " · 선택 분류" : " · 전체"}
        </p>
      )}

      {loading && (
        <p className="mt-10 text-center text-sm text-[var(--muted)]">불러오는 중…</p>
      )}
      {error && <p className="mt-6 text-center text-sm text-red-600">{error}</p>}

      <div className="mt-4 space-y-3">
        {products.map((p) => (
          <ProductCard key={p.id} p={p} />
        ))}
      </div>

      {!loading && products.length === 0 && (
        <Card className="mt-10 border-dashed border-[var(--border)]">
          <CardContent className="space-y-3 py-10 text-center text-sm text-[var(--muted)]">
            <p>검색·분류에 맞는 상품이 없습니다.</p>
            <Button asChild size="sm" variant="outline">
              <Link href="/store">전체 보기</Link>
            </Button>
          </CardContent>
        </Card>
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
