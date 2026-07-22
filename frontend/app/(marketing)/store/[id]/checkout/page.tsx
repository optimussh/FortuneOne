"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  createPaymentOrder,
  getPaymentConfig,
  getStoreProduct,
  listFortuneProfiles,
  type FortuneProfile,
  type PaymentConfig,
  type StoreProduct,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

/**
 * Checkout: creates payment order via /api/payments.
 * - mock: auto-confirm → success page
 * - toss: loads Toss SDK when keys present (test/live)
 */
function StepDots({ step }: { step: number }) {
  const labels = ["상품", "프로필", "결제"];
  return (
    <div className="mb-6 flex items-center justify-center gap-2">
      {labels.map((label, i) => {
        const n = i + 1;
        const active = n === step;
        const done = n < step;
        return (
          <div key={label} className="flex items-center gap-2">
            {i > 0 && <span className="h-px w-4 bg-[var(--border)]" />}
            <div className="flex flex-col items-center gap-0.5">
              <span
                className={`flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold ${
                  active || done
                    ? "bg-[var(--primary)] text-white"
                    : "border border-[var(--border)] text-[var(--muted)]"
                }`}
              >
                {n}
              </span>
              <span
                className={`text-[10px] ${active ? "font-semibold text-[var(--foreground)]" : "text-[var(--muted)]"}`}
              >
                {label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CheckoutInner() {
  const { id } = useParams<{ id: string }>();
  const search = useSearchParams();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [product, setProduct] = useState<StoreProduct | null>(null);
  const [payCfg, setPayCfg] = useState<PaymentConfig | null>(null);
  const [profiles, setProfiles] = useState<FortuneProfile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [partnerId, setPartnerId] = useState<number | "">("");
  const [buyerName, setBuyerName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
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
    getPaymentConfig().then(setPayCfg).catch(() => setPayCfg(null));
    listFortuneProfiles().then((rows) => {
      setProfiles(rows);
      if (rows[0]) setProfileId(rows[0].id);
    });
  }, [user, authLoading, router, id]);

  const pay = async () => {
    if (!profileId) {
      setError("사주 프로필을 선택하세요.");
      return;
    }
    if (!agree1 || !agree2) {
      setError("필수 약관에 동의해 주세요");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const order = await createPaymentOrder({
        kind: "store_product",
        product_id: id,
        profile_id: Number(profileId),
        partner_profile_id: partnerId ? Number(partnerId) : undefined,
        buyer_name: buyerName,
        email,
        phone,
        agree_privacy: agree1,
        agree_age14: agree2,
      });

      if (order.free) {
        setMsg(order.message);
        router.push(order.result_path);
        return;
      }

      // Mock path — fully testable without Toss
      if (order.provider === "mock" || order.mock_auto_confirm) {
        setMsg("모의 결제 확인으로 이동…");
        const q = new URLSearchParams({
          orderId: order.order_id || "",
          paymentKey: `mock_${order.order_id}`,
          amount: String(order.amount_krw),
        });
        router.push(`/payments/success?${q}`);
        return;
      }

      // Toss path — load widget when SDK available
      if (order.provider === "toss" && order.client_key && order.order_id) {
        setMsg("토스 결제창 준비… (테스트 키면 샌드박스)");
        await openTossPayment({
          clientKey: order.client_key,
          customerKey: order.customer_key || `user_${user?.email}`,
          orderId: order.order_id,
          orderName: order.product_name || product?.title || "FortuneOne",
          amount: order.amount_krw,
          successUrl: order.success_url || `${window.location.origin}/payments/success`,
          failUrl: order.fail_url || `${window.location.origin}/payments/fail`,
        });
        return;
      }

      setError("결제 제공자를 초기화하지 못했습니다. PAYMENT_PROVIDER=mock 으로 테스트하세요.");
    } catch (e) {
      const m = e instanceof Error ? e.message : "결제 실패";
      // Common when API process is outdated (missing /api/payments)
      if (/not found|404|Failed to fetch|NetworkError/i.test(m)) {
        setError(
          m +
            " — 백엔드(API :8000)를 최신 코드로 재시작해 주세요. (PAYMENT mock 라우트 필요)"
        );
      } else {
        setError(m);
      }
    } finally {
      setBusy(false);
    }
  };

  if (!product) {
    return (
      <main className="py-20 text-center text-sm text-[var(--muted)]">결제 페이지 로딩…</main>
    );
  }

  return (
    <main className="mx-auto max-w-md px-4 py-10 pb-20">
      <StepDots step={2} />
      <h1 className="text-center text-xl font-extrabold">결제 · 사주 연결</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">{product.title}</p>
      <p className="mt-1 text-center text-lg font-bold text-amber-700">
        {product.is_free ? "무료" : `${product.price_krw.toLocaleString()}원`}
      </p>
      <p className="mt-2 text-center text-[11px] text-[var(--muted)]">
        선택한 사주 프로필로 맞춤 결과가 생성됩니다
      </p>

      {payCfg && (
        <p className="mt-2 text-center text-[10px] text-[var(--muted)]">
          결제: <strong>{payCfg.provider === "mock" ? "모의결제 (개발)" : payCfg.provider}</strong>
          {payCfg.test_mode ? " · 테스트 모드" : ""}
        </p>
      )}

      {search.get("unlocked") && (
        <p className="mt-2 text-center text-xs text-emerald-700">
          이미 해금된 상품일 수 있어요. 아래에서 프로필만 고르고 결과로 이동하세요.
        </p>
      )}

      <Card className="mt-6 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">내 사주 프로필</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {profiles.length === 0 ? (
            <p className="text-sm text-red-600">
              프로필 없음 ·{" "}
              <Link href="/profiles" className="underline">
                등록
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
              <p className="mb-1 text-xs font-semibold">상대 프로필</p>
              <select
                className="w-full rounded-lg border border-[var(--border)] p-2 text-sm"
                value={partnerId}
                onChange={(e) =>
                  setPartnerId(e.target.value ? Number(e.target.value) : "")
                }
              >
                <option value="">선택(선택)</option>
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

      <div className="mt-4 space-y-2 text-sm">
        <label className="flex items-start gap-2">
          <input type="checkbox" checked={agree1} onChange={(e) => setAgree1(e.target.checked)} />
          <span>
            <Link href="/policy/privacy" className="underline">
              개인정보
            </Link>{" "}
            수집·이용 동의 (필수)
          </span>
        </label>
        <label className="flex items-start gap-2">
          <input type="checkbox" checked={agree2} onChange={(e) => setAgree2(e.target.checked)} />
          <span>(필수) 만 14세 이상 · 디지털 콘텐츠 안내 확인</span>
        </label>
        <p className="text-[10px] text-[var(--muted)]">
          <Link href="/policy/refund" className="underline">
            환불 정책
          </Link>
          {" · "}
          <Link href="/policy/business" className="underline">
            사업자 정보
          </Link>
        </p>
      </div>

      {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}
      {msg && <p className="mt-3 text-center text-sm text-emerald-700">{msg}</p>}

      <Button className="mt-6 w-full" disabled={busy} onClick={() => void pay()}>
        {busy
          ? "처리 중…"
          : product.is_free
            ? "결과 생성"
            : payCfg?.provider === "toss"
              ? "토스로 결제"
              : "모의 결제 테스트"}
      </Button>
      <Button asChild variant="outline" className="mt-2 w-full">
        <Link href={`/store/${id}`}>취소</Link>
      </Button>
    </main>
  );
}

async function openTossPayment(opts: {
  clientKey: string;
  customerKey: string;
  orderId: string;
  orderName: string;
  amount: number;
  successUrl: string;
  failUrl: string;
}) {
  // Dynamic load Toss SDK v2
  await loadScript("https://js.tosspayments.com/v2/standard");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const TossPayments = (window as any).TossPayments;
  if (!TossPayments) {
    throw new Error("TossPayments SDK 로드 실패");
  }
  const toss = TossPayments(opts.clientKey);
  const payment = toss.payment({ customerKey: opts.customerKey });
  await payment.requestPayment({
    method: "CARD",
    amount: { currency: "KRW", value: opts.amount },
    orderId: opts.orderId,
    orderName: opts.orderName,
    successUrl: opts.successUrl,
    failUrl: opts.failUrl,
  });
}

function loadScript(src: string) {
  return new Promise<void>((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error("script load failed"));
    document.body.appendChild(s);
  });
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<main className="py-20 text-center text-sm">결제 로딩…</main>}>
      <CheckoutInner />
    </Suspense>
  );
}
