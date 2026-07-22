"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  createPaymentOrder,
  getPaymentConfig,
  getWallet,
  type PaymentConfig,
  type WalletInfo,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ShopPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const [payCfg, setPayCfg] = useState<PaymentConfig | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const [agree, setAgree] = useState(false);

  const load = useCallback(async () => {
    const w = await getWallet();
    setWallet(w);
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/shop");
      return;
    }
    void load().catch((e) => setMsg(e instanceof Error ? e.message : "실패"));
    getPaymentConfig().then(setPayCfg).catch(() => null);
  }, [user, authLoading, router, load]);

  const packs =
    (wallet?.catalog?.packs as {
      id: string;
      label: string;
      total_beads: number;
      price_krw: number;
      bonus_pct: number;
    }[]) || [];

  const startPay = async (kind: "beads_pack" | "wealth_year", product_id: string) => {
    if (!agree) {
      setMsg("약관에 동의해 주세요");
      return;
    }
    setBusy(true);
    setMsg("");
    try {
      const order = await createPaymentOrder({
        kind,
        product_id,
        agree_privacy: true,
        agree_age14: true,
        email: user?.email || "",
      });
      if (order.free) {
        setMsg(order.message);
        await load();
        return;
      }
      if (order.provider === "mock" || order.mock_auto_confirm) {
        const q = new URLSearchParams({
          orderId: order.order_id || "",
          paymentKey: `mock_${order.order_id}`,
          amount: String(order.amount_krw),
        });
        router.push(`/payments/success?${q}`);
        return;
      }
      setMsg("토스 결제 연동: 스토어 체크아웃과 동일한 SDK 경로를 사용하세요. 현재는 mock 권장.");
      await load();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "실패");
    } finally {
      setBusy(false);
    }
  };

  if (authLoading || !wallet) {
    return (
      <main className="px-4 py-20 text-center text-sm text-[var(--muted)]">상점 불러오는 중…</main>
    );
  }

  const wealthUnlocked = wallet.unlocks["wealth_2026"];

  return (
    <main className="mx-auto max-w-lg px-4 py-8 pb-20">
      <div className="mb-6 text-center">
        <p className="text-xs font-semibold text-[var(--primary)]">SHOP</p>
        <h1 className="mt-1 text-2xl font-extrabold">구슬 · 해금</h1>
        <p className="mt-2 text-sm text-[var(--muted)]">{wallet.note}</p>
        <p className="mt-3 text-3xl font-extrabold text-amber-600">✦ {wallet.beads}</p>
        <p className="text-xs text-[var(--muted)]">
          보유 구슬 · 결제 provider: {payCfg?.provider || "mock"}
        </p>
        <p className="mt-2 text-[10px] text-[var(--muted)]">
          유료 해금 다시보기: 웹 7일 · 이메일 링크 30일 (
          <Link href="/policy/refund" className="underline">
            환불·기간 정책
          </Link>
          )
        </p>
      </div>

      {msg && (
        <p className="mb-4 rounded-xl bg-[var(--primary-light)] px-3 py-2 text-center text-sm">
          {msg}
        </p>
      )}

      <label className="mb-4 flex items-start gap-2 text-sm">
        <input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)} />
        <span>
          <Link href="/policy" className="underline">
            이용약관
          </Link>
          ·
          <Link href="/policy/privacy" className="underline">
            개인정보
          </Link>
          · 만 14세 이상 동의
        </span>
      </label>

      <Card className="mb-4 border-amber-400 bg-amber-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">2026 부자되기 단건</CardTitle>
          <CardDescription className="text-xs">
            연간 해금 · 모의/토스 결제 모듈 연동
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            disabled={busy || wealthUnlocked}
            onClick={() => void startPay("wealth_year", "wealth_2026")}
          >
            {wealthUnlocked ? "이미 해금됨" : "결제하고 해금"}
          </Button>
          <Button asChild variant="link" className="mt-2">
            <Link href="/me?tab=wealth">부자되기 보기 →</Link>
          </Button>
        </CardContent>
      </Card>

      <Card className="mb-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">구슬 팩</CardTitle>
          <CardDescription className="text-xs">타로 추가·질문·프로필 심화</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {packs.map((p) => (
            <div
              key={p.id}
              className="flex items-center justify-between rounded-xl border border-[var(--border)] px-3 py-2"
            >
              <div className="text-sm">
                <div className="font-semibold">{p.label}</div>
                <div className="text-[10px] text-[var(--muted)]">
                  {p.total_beads}개 · {p.price_krw.toLocaleString()}원
                  {p.bonus_pct ? ` · +${p.bonus_pct}%` : ""}
                </div>
              </div>
              <Button
                size="sm"
                variant="outline"
                disabled={busy}
                onClick={() => void startPay("beads_pack", p.id)}
              >
                결제
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card className="border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">구슬 사용처</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm text-[var(--muted)]">
          <p>· 타로 추가 뽑기: {wallet.costs.tarot_extra} 구슬</p>
          <p>· 질문형 (무료 1회/일 초과): {wallet.costs.ask} 구슬</p>
          <p>· 다른 사람 프로필 심화: {wallet.costs.profile_deep} 구슬</p>
          <p className="pt-2 text-[10px]">
            <Link href="/store" className="text-[var(--primary)] underline">
              운세 스토어
            </Link>
            도 동일 결제 모듈을 사용합니다.
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
