"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { getStoreProduct, type StoreProduct } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function StoreProductPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const router = useRouter();
  const [product, setProduct] = useState<StoreProduct | null>(null);
  const [unlocked, setUnlocked] = useState(false);
  const [error, setError] = useState("");
  const [payment, setPayment] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!id) return;
    getStoreProduct(id)
      .then((r) => {
        setProduct(r.product);
        setUnlocked(r.unlocked);
        setPayment(r.payment_module);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "실패"));
  }, [id, user]);

  if (error) {
    return (
      <main className="mx-auto max-w-lg px-4 py-16 text-center">
        <p className="text-sm text-red-600">{error}</p>
        <Button asChild className="mt-4" variant="outline">
          <Link href="/store">스토어로</Link>
        </Button>
      </main>
    );
  }

  if (!product) {
    return (
      <main className="py-20 text-center text-sm text-[var(--muted)]">상품 불러오는 중…</main>
    );
  }

  return (
    <main className="mx-auto max-w-lg px-4 py-10 pb-28">
      <p className="text-center text-xs font-semibold text-[var(--primary)]">
        {product.category_label}
      </p>
      <h1 className="mt-2 text-center text-xl font-extrabold leading-snug">{product.title}</h1>
      {product.subtitle && (
        <p className="mt-1 text-center text-xs text-[var(--muted)]">{product.subtitle}</p>
      )}
      <p className="mt-3 text-center text-2xl font-extrabold text-amber-700">
        {product.is_free ? "무료" : `${product.price_krw.toLocaleString()}원`}
      </p>
      <p className="mt-2 text-center text-[11px] text-[var(--muted)]">
        결제 후 <strong className="text-[var(--foreground)]">내 사주 프로필</strong>로 맞춤 결과 생성
        · 웹 7일 · 메일 링크 30일 다시보기
      </p>

      <Card className="mt-6 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">이런 내용이에요</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm leading-7 text-[var(--muted)]">
          {(product.intro_blurbs || []).length > 0 ? (
            (product.intro_blurbs || []).map((b, i) => <p key={i}>{b}</p>)
          ) : (
            <p>선택하신 사주 프로필을 기준으로 주제 해석과 실천 문장을 제공합니다.</p>
          )}
        </CardContent>
      </Card>

      {(product.for_whom || []).length > 0 && (
        <Card className="mt-4 border-[var(--border)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">이런 분께</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-1 pl-5 text-sm">
              {product.for_whom!.map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">운세 구성 ({(product.result_sections || []).length}단)</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal space-y-1 pl-5 text-sm">
            {(product.result_sections || []).map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ol>
        </CardContent>
      </Card>

      <Card className="mt-4 border-amber-200 bg-amber-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">기본 탭과 차이</CardTitle>
        </CardHeader>
        <CardContent className="text-xs leading-relaxed text-[var(--muted)]">
          <p>
            {product.diff_from_free_tabs ||
              "상세 사주 탭(오늘·신년·토정·부자되기)은 기본 제공, 스토어는 주제 심화 패키지입니다."}
          </p>
          <p className="mt-2">
            <Link href="/me" className="font-semibold text-[var(--primary)] underline">
              상세 사주 열기
            </Link>
            {" · "}
            <Link href="/me?tab=tojeong" className="underline text-[var(--primary)]">
              토정
            </Link>
            {" · "}
            <Link href="/me?tab=wealth" className="underline text-[var(--primary)]">
              부자되기
            </Link>
          </p>
        </CardContent>
      </Card>

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">결제 안내 (모의)</CardTitle>
        </CardHeader>
        <CardContent className="text-xs leading-relaxed text-[var(--muted)]">
          <p>수단: {((payment?.methods as string[]) || ["모의결제"]).join(" · ")}</p>
          <ul className="mt-2 list-disc space-y-1 pl-4">
            {((payment?.notices as string[]) || []).map((n) => (
              <li key={n}>{n}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <div className="mt-6 flex flex-col gap-2">
        <Button asChild variant="outline">
          <Link href="/store">목록으로</Link>
        </Button>
        {unlocked && (
          <Button asChild variant="outline">
            <Link href="/library">내 구매 · 다시보기</Link>
          </Button>
        )}
      </div>

      {/* Sticky purchase bar */}
      <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-[var(--border)] bg-white/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-lg items-center gap-3">
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold">{product.title}</p>
            <p className="text-sm font-extrabold text-amber-700">
              {product.is_free ? "무료" : `${product.price_krw.toLocaleString()}원`}
            </p>
          </div>
          {unlocked ? (
            <Button
              className="shrink-0"
              onClick={() => router.push(`/store/${product.id}/checkout?unlocked=1`)}
            >
              결과 보기
            </Button>
          ) : (
            <Button
              className="shrink-0"
              onClick={() => {
                if (!user) {
                  router.push(`/login?next=/store/${product.id}/checkout`);
                  return;
                }
                router.push(`/store/${product.id}/checkout`);
              }}
            >
              {product.is_free ? "무료로 보기" : "결제하고 보기"}
            </Button>
          )}
        </div>
      </div>
    </main>
  );
}
