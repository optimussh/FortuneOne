"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getMyPurchases, type PurchaseItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

/**
 * 내가 산 운세 결과 다시보기 (웹 7일 · 이메일 링크 30일)
 */
export default function LibraryPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [items, setItems] = useState<PurchaseItem[]>([]);
  const [policy, setPolicy] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [copiedKey, setCopiedKey] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getMyPurchases();
      setItems(data.items || []);
      setPolicy(data.policy?.summary || "");
    } catch (e) {
      setError(e instanceof Error ? e.message : "실패");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/library");
      return;
    }
    void load();
  }, [user, authLoading, router, load]);

  if (authLoading || loading) {
    return (
      <main className="px-4 py-20 text-center text-sm text-[var(--muted)]">불러오는 중…</main>
    );
  }

  return (
    <main className="mx-auto max-w-lg px-4 py-10 pb-20">
      <p className="text-center text-xs font-semibold text-[var(--primary)]">MY LIBRARY</p>
      <h1 className="mt-1 text-center text-2xl font-extrabold">내 구매 · 다시보기</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        스토어·해금한 유료 결과를 기간 안에 다시 엽니다
      </p>

      <Card className="mt-6 border-[var(--primary)] bg-[var(--primary-light)]">
        <CardContent className="py-3 text-xs leading-relaxed text-[var(--muted)]">
          <p className="font-semibold text-[var(--foreground)]">다시보기란?</p>
          <p className="mt-1">
            {policy ||
              "결제 후 웹(로그인) 7일, 이메일 링크 30일 동안 같은 결과를 다시 볼 수 있는 기간입니다."}
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-4">
            <li>
              <strong>웹 7일</strong>: 로그인 후 이 목록에서 「결과 보기」
            </li>
            <li>
              <strong>이메일 링크 30일</strong>: 결과 화면에 나온 링크를 저장·전달 (메일 자동 발송은
              추후)
            </li>
            <li>기간이 지나면 재구매가 필요할 수 있습니다</li>
          </ul>
        </CardContent>
      </Card>

      {error && <p className="mt-4 text-center text-sm text-red-600">{error}</p>}

      <div className="mt-6 space-y-3">
        {items.length === 0 && (
          <Card className="border-[var(--border)]">
            <CardContent className="py-8 text-center text-sm text-[var(--muted)]">
              아직 구매·해금한 상품이 없습니다.
              <div className="mt-4">
                <Button asChild size="sm">
                  <Link href="/store">스토어 둘러보기</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {items.map((it) => (
          <Card
            key={it.product_key}
            className={`border ${it.web_ok ? "border-[var(--border)]" : "border-amber-300"}`}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-base leading-snug">{it.title}</CardTitle>
              <p className="text-[10px] text-[var(--muted)]">
                {it.kind} · {it.source}
                {it.created_at ? ` · ${it.created_at.slice(0, 10)}` : ""}
              </p>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div className="flex flex-wrap gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 font-semibold text-white ${
                    it.web_ok ? "bg-emerald-600" : "bg-amber-600"
                  }`}
                >
                  웹 {it.web_ok ? "열람 가능" : "만료"}
                  {it.days_left_web != null && it.web_ok
                    ? ` · ${it.days_left_web}일 남음`
                    : ""}
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 font-semibold ${
                    it.email_ok
                      ? "bg-sky-100 text-sky-800"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  메일 링크 {it.email_ok ? "유효" : "만료"}
                </span>
              </div>
              {it.web_expires_at && (
                <p className="text-[var(--muted)]">
                  웹 만료: {String(it.web_expires_at).slice(0, 16).replace("T", " ")}
                </p>
              )}
              {it.email_expires_at && (
                <p className="text-[var(--muted)]">
                  메일 만료: {String(it.email_expires_at).slice(0, 16).replace("T", " ")}
                </p>
              )}
              <div className="flex flex-wrap gap-2 pt-1">
                {it.web_ok ? (
                  <Button asChild size="sm">
                    <Link href={it.result_path}>결과 보기</Link>
                  </Button>
                ) : (
                  <Button asChild size="sm" variant="outline">
                    <Link href="/store">재구매 · 스토어</Link>
                  </Button>
                )}
                {it.email_result_link && it.email_ok && (
                  <Button
                    size="sm"
                    variant="outline"
                    type="button"
                    onClick={async () => {
                      try {
                        await navigator.clipboard?.writeText(it.email_result_link || "");
                        setCopiedKey(it.product_key);
                        window.setTimeout(() => setCopiedKey(""), 2000);
                      } catch {
                        setError("링크 복사에 실패했습니다. 결과 화면에서 복사해 주세요.");
                      }
                    }}
                  >
                    {copiedKey === it.product_key ? "복사됨" : "메일용 링크 복사"}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">
        <Link href="/me" className="text-[var(--primary)] underline">
          상세 사주
        </Link>
        <Link href="/store" className="text-[var(--primary)] underline">
          스토어
        </Link>
        <Link href="/hub" className="text-[var(--primary)] underline">
          허브
        </Link>
        <Link href="/profiles" className="text-[var(--primary)] underline">
          사주 프로필
        </Link>
        <Link href="/shop" className="text-[var(--primary)] underline">
          구슬·해금
        </Link>
      </div>
    </main>
  );
}
