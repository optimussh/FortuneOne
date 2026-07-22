"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { confirmPayment, getPaymentOrder } from "@/lib/api";
import { Button } from "@/components/ui/button";

/**
 * Toss redirects here with paymentKey, orderId, amount.
 * Mock flow also lands here after client-side mock confirm.
 */
function SuccessInner() {
  const sp = useSearchParams();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [msg, setMsg] = useState("결제 확인 중…");
  const [error, setError] = useState("");
  const [resultPath, setResultPath] = useState("");

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/payments/success");
      return;
    }

    const orderId = sp.get("orderId") || sp.get("order_id") || "";
    const paymentKey = sp.get("paymentKey") || sp.get("payment_key") || "";
    const amountStr = sp.get("amount") || "";

    const run = async () => {
      if (!orderId) {
        setError("orderId가 없습니다");
        return;
      }
      try {
        let amount = amountStr ? Number(amountStr) : 0;
        if (!amount) {
          const o = await getPaymentOrder(orderId);
          amount = o.amount_krw;
        }
        const key = paymentKey || `mock_${orderId}`;
        const r = await confirmPayment({
          payment_key: key,
          order_id: orderId,
          amount,
        });
        setMsg(r.message || "결제 완료");
        setResultPath(r.result_path);
        if (r.result_path) {
          setTimeout(() => router.replace(r.result_path), 800);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "확인 실패");
      }
    };
    void run();
  }, [user, authLoading, sp, router]);

  return (
    <main className="mx-auto max-w-md px-4 py-16 text-center">
      <h1 className="text-xl font-extrabold">결제 결과</h1>
      {error ? (
        <p className="mt-4 text-sm text-red-600">{error}</p>
      ) : (
        <p className="mt-4 text-sm text-[var(--muted)]">{msg}</p>
      )}
      {resultPath && (
        <Button asChild className="mt-6">
          <Link href={resultPath}>결과 보기</Link>
        </Button>
      )}
      <div className="mt-4">
        <Link href="/store" className="text-sm text-[var(--primary)] underline">
          스토어
        </Link>
      </div>
    </main>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={<main className="py-20 text-center text-sm">처리 중…</main>}>
      <SuccessInner />
    </Suspense>
  );
}
