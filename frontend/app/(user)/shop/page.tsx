"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { buyBeadPack, buyWealthYear, getWallet, type WalletInfo } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ShopPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

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
  }, [user, authLoading, router, load]);

  const packs =
    (wallet?.catalog?.packs as {
      id: string;
      label: string;
      total_beads: number;
      price_krw: number;
      bonus_pct: number;
    }[]) || [];

  const onBuyPack = async (id: string) => {
    setBusy(true);
    setMsg("");
    try {
      const r = await buyBeadPack(id);
      setMsg(r.message);
      await load();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "실패");
    } finally {
      setBusy(false);
    }
  };

  const onUnlock = async () => {
    setBusy(true);
    setMsg("");
    try {
      const r = await buyWealthYear(2026);
      setMsg(r.message);
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
        <p className="text-xs text-[var(--muted)]">보유 구슬 (가입 시 {wallet.starter_beads}개 지급)</p>
      </div>

      {msg && (
        <p className="mb-4 rounded-xl bg-[var(--primary-light)] px-3 py-2 text-center text-sm">
          {msg}
        </p>
      )}

      <Card className="mb-4 border-amber-400 bg-amber-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">2026 부자되기 단건</CardTitle>
          <CardDescription className="text-xs">
            총론 전문 · 월별 · 일자 캘린더 · 장문 · 저장 — 모의{" "}
            {(wallet.catalog as { wealth_year?: { price_krw: number } })?.wealth_year?.price_krw?.toLocaleString() ||
              "3,900"}
            원
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button disabled={busy || wealthUnlocked} onClick={() => void onUnlock()}>
            {wealthUnlocked ? "이미 해금됨" : "모의 결제로 해금"}
          </Button>
          <Button asChild variant="link" className="mt-2">
            <Link href="/me?tab=wealth">부자되기 보기 →</Link>
          </Button>
        </CardContent>
      </Card>

      <Card className="mb-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">구슬 팩</CardTitle>
          <CardDescription className="text-xs">
            많이 살수록 보너스 · 타로 추가·질문·프로필 심화에 사용
          </CardDescription>
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
              <Button size="sm" variant="outline" disabled={busy} onClick={() => void onBuyPack(p.id)}>
                모의 구매
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
            점수·운세는 참고 지표이며 투자 권유가 아닙니다. 실제 PG 연동 전 모의 결제만 동작합니다.
          </p>
        </CardContent>
      </Card>

      <div className="mt-6 flex justify-center gap-3 text-sm">
        <Link href="/hub" className="text-[var(--primary)] underline">
          허브
        </Link>
        <Link href="/me?tab=wealth" className="text-[var(--primary)] underline">
          부자되기
        </Link>
      </div>
    </main>
  );
}
