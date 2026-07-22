"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  checkoutStoreProduct,
  getStoreProduct,
  listFortuneProfiles,
  type FortuneProfile,
  type StoreProduct,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

function CheckoutInner() {
  const { id } = useParams<{ id: string }>();
  const search = useSearchParams();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [product, setProduct] = useState<StoreProduct | null>(null);
  const [profiles, setProfiles] = useState<FortuneProfile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [partnerId, setPartnerId] = useState<number | "">("");
  const [buyerName, setBuyerName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [method, setMethod] = useState("mock_card");
  const [agree1, setAgree1] = useState(false);
  const [agree2, setAgree2] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace(`/login?next=/store/${id}/checkout`);
      return;
    }
    setEmail(user.email || "");
    setBuyerName(user.email?.split("@")[0] || "");
    getStoreProduct(id).then((r) => setProduct(r.product));
    listFortuneProfiles().then((rows) => {
      setProfiles(rows);
      if (rows[0]) setProfileId(rows[0].id);
    });
  }, [user, authLoading, router, id]);

  const pay = async () => {
    if (!profileId) {
      setError("사주 프로필을 선택하세요. 없으면 프로필 관리에서 등록하세요.");
      return;
    }
    if (!agree1 || !agree2) {
      setError("필수 약관에 동의해 주세요");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const r = await checkoutStoreProduct({
        product_id: id,
        profile_id: Number(profileId),
        partner_profile_id: partnerId ? Number(partnerId) : undefined,
        buyer_name: buyerName,
        email,
        phone,
        method,
        agree_privacy: agree1,
        agree_age14: agree2,
      });
      setMsg(r.message);
      router.push(r.result_path);
    } catch (e) {
      setError(e instanceof Error ? e.message : "결제 실패");
    } finally {
      setBusy(false);
    }
  };

  if (!product) {
    return (
      <main className="py-20 text-center text-sm text-[var(--muted)]">결제 페이지 로딩…</main>
    );
  }

  const methods = ["mock_card", "mock_kakao", "mock_naver", "mock_phone", "mock_transfer"];

  return (
    <main className="mx-auto max-w-md px-4 py-10 pb-20">
      <h1 className="text-center text-xl font-extrabold">결제 · 사주 연결</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">{product.title}</p>
      <p className="mt-1 text-center text-lg font-bold text-amber-700">
        {product.is_free ? "무료" : `${product.price_krw.toLocaleString()}원 (모의)`}
      </p>
      {search.get("unlocked") && (
        <p className="mt-2 text-center text-xs text-emerald-700">이미 해금된 상품입니다</p>
      )}

      <Card className="mt-6 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">1. 내 사주 프로필 (결과 기준)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {profiles.length === 0 ? (
            <p className="text-sm text-red-600">
              등록된 사주가 없습니다.{" "}
              <Link href="/profiles" className="underline">
                프로필 등록
              </Link>
            </p>
          ) : (
            <select
              className="w-full rounded-lg border border-[var(--border)] p-2 text-sm"
              value={profileId}
              onChange={(e) => setProfileId(e.target.value ? Number(e.target.value) : "")}
            >
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} · {p.display_name || "이름없음"} · {p.solar_date}
                </option>
              ))}
            </select>
          )}
          {product.needs_partner && (
            <div>
              <p className="mb-1 text-xs font-semibold">상대 프로필 (궁합형)</p>
              <select
                className="w-full rounded-lg border border-[var(--border)] p-2 text-sm"
                value={partnerId}
                onChange={(e) =>
                  setPartnerId(e.target.value ? Number(e.target.value) : "")
                }
              >
                <option value="">선택(선택사항)</option>
                {profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.label} · {p.display_name || "이름없음"}
                  </option>
                ))}
              </select>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">2. 구매자 정보</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Input
            placeholder="구매자명"
            value={buyerName}
            onChange={(e) => setBuyerName(e.target.value)}
          />
          <Input
            type="email"
            placeholder="이메일"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            placeholder="휴대전화"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </CardContent>
      </Card>

      <Card className="mt-4 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">3. 결제 수단 (모의)</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {methods.map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMethod(m)}
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                method === m
                  ? "bg-[var(--primary)] text-white"
                  : "border border-[var(--border)]"
              }`}
            >
              {m.replace("mock_", "")}
            </button>
          ))}
        </CardContent>
      </Card>

      <div className="mt-4 space-y-2 text-sm">
        <label className="flex items-start gap-2">
          <input type="checkbox" checked={agree1} onChange={(e) => setAgree1(e.target.checked)} />
          <span>개인정보 수집 및 이용에 동의 (필수)</span>
        </label>
        <label className="flex items-start gap-2">
          <input type="checkbox" checked={agree2} onChange={(e) => setAgree2(e.target.checked)} />
          <span>(필수) 만 14세 이상</span>
        </label>
      </div>

      {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}
      {msg && <p className="mt-3 text-center text-sm text-emerald-700">{msg}</p>}

      <Button className="mt-6 w-full" disabled={busy} onClick={() => void pay()}>
        {busy ? "처리 중…" : product.is_free ? "결과 생성" : "모의 결제하기"}
      </Button>
      <Button asChild variant="outline" className="mt-2 w-full">
        <Link href={`/store/${id}`}>취소</Link>
      </Button>
    </main>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<main className="py-20 text-center text-sm">결제 로딩…</main>}>
      <CheckoutInner />
    </Suspense>
  );
}
