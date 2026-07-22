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
    <main className="mx-auto max-w-lg px-4 py-10 pb-20">
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

      <Card className="mt-6 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">운세 소개</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm leading-7 text-[var(--muted)]">
          {(product.intro_blurbs || []).map((b, i) => (
            <p key={i}>{b}</p>
          ))}
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

      <div className="mt-8 flex flex-col gap-2">
        {unlocked ? (
          <Button onClick={() => router.push(`/store/${product.id}/checkout?unlocked=1`)}>
            결과 보기 (해금됨)
          </Button>
        ) : (
          <Button
            onClick={() => {
              if (!user) {
                router.push(`/login?next=/store/${product.id}/checkout`);
                return;
              }
              router.push(`/store/${product.id}/checkout`);
            }}
          >
            {product.is_free ? "사주 선택 후 무료 보기" : "결제하고 결과 보기"}
          </Button>
        )}
        <Button asChild variant="outline">
          <Link href="/store">목록으로</Link>
        </Button>
      </div>
    </main>
  );
}
