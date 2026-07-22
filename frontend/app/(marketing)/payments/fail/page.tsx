"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";

function FailInner() {
  const sp = useSearchParams();
  const code = sp.get("code") || "";
  const message = sp.get("message") || "결제가 취소되었거나 실패했습니다.";
  const orderId = sp.get("orderId") || "";

  return (
    <main className="mx-auto max-w-md px-4 py-16 text-center">
      <h1 className="text-xl font-extrabold">결제 실패</h1>
      <p className="mt-4 text-sm text-[var(--muted)]">{message}</p>
      {code && <p className="mt-1 text-xs text-[var(--muted)]">code: {code}</p>}
      {orderId && <p className="mt-1 text-xs text-[var(--muted)]">order: {orderId}</p>}
      <div className="mt-8 flex justify-center gap-3">
        <Button asChild variant="outline">
          <Link href="/store">스토어</Link>
        </Button>
        <Button asChild>
          <Link href="/hub">허브</Link>
        </Button>
      </div>
    </main>
  );
}

export default function PaymentFailPage() {
  return (
    <Suspense fallback={<main className="py-20 text-center text-sm">로딩…</main>}>
      <FailInner />
    </Suspense>
  );
}
