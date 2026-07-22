import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "환불 정책 - FortuneOne",
  description: "FortuneOne 디지털 콘텐츠 환불 정책 (템플릿)",
};

/** Fill bracket placeholders when business is ready. */
export default function RefundPolicyPage() {
  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "60px 24px 80px", lineHeight: 1.8, fontSize: 14 }}>
      <Link href="/" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
        ← 홈
      </Link>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginTop: 24 }}>환불 정책</h1>
      <p style={{ color: "var(--muted)" }}>시행일: [시행일] · 템플릿 — 법률 검토 후 확정하세요</p>

      <section style={{ marginTop: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>1. 적용 대상</h2>
        <p>
          FortuneOne이 판매하는 <strong>디지털 운세 리포트·구슬·이용권</strong> 등 온라인 콘텐츠에
          적용됩니다. 실물 상품 배송은 해당하지 않습니다.
        </p>
      </section>

      <section style={{ marginTop: 28 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>2. 청약 철회·환불</h2>
        <ul style={{ paddingLeft: 20 }}>
          <li>
            결제 후 <strong>콘텐츠를 열람(결과 페이지 접속·다운로드)하기 전</strong>에는 원칙적으로
            환불을 요청할 수 있습니다. (전자상거래법상 디지털 콘텐츠 청약철회 제한 가능 구간 참고)
          </li>
          <li>
            <strong>결과 열람 이후</strong>에는 디지털 특성상 원칙적으로 환불이 제한될 수 있습니다.
            단, 중복 결제·시스템 오류 등 회사 귀책 사유는 환불합니다.
          </li>
          <li>구슬 등 충전 재화는 미사용 분에 한해 [정책 확정] 합니다.</li>
        </ul>
      </section>

      <section style={{ marginTop: 28 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>3. 신청 방법</h2>
        <p>
          고객센터 이메일 <strong>[support@example.com]</strong> 또는 전화{" "}
          <strong>[전화번호]</strong> 로 주문번호·결제일을 알려 주세요. [N]영업일 이내 처리합니다.
        </p>
      </section>

      <section style={{ marginTop: 28 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>4. 유의사항</h2>
        <p>
          본 서비스는 엔터테인먼트·참고용이며 투자·법률·의료 자문이 아닙니다. 해석 결과에 대한 주관적
          불만족만으로는 환불이 어려울 수 있습니다.
        </p>
      </section>
    </div>
  );
}
