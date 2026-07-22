import Link from "next/link";

/** Business fields: replace placeholders before production go-live. */
const BIZ = {
  name: "FortuneOne",
  tagline: "사주 · 운세 · 타로 · 궁합 · 스토어",
  ceo: "[대표자명]",
  number: "[사업자등록번호]",
  mailOrder: "[통신판매업 신고번호]",
  address: "[사업장 주소]",
  phone: "[고객센터]",
  email: "support@fortuneone.local",
};

export function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid var(--border)",
        background: "var(--card-bg, #fff)",
        padding: "48px 24px 32px",
        marginTop: 80,
      }}
    >
      <div
        style={{
          maxWidth: 1200,
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 40,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 800,
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              marginBottom: 12,
            }}
          >
            {BIZ.name}
          </div>
          <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.7 }}>
            {BIZ.tagline}
            <br />
            디지털 운세 콘텐츠 · 엔터테인먼트 참고용
          </p>
          <p style={{ fontSize: 11, color: "var(--muted)", lineHeight: 1.6, marginTop: 12 }}>
            상호 {BIZ.name} · 대표 {BIZ.ceo}
            <br />
            사업자 {BIZ.number}
            <br />
            통신판매 {BIZ.mailOrder}
            <br />
            {BIZ.address}
            <br />
            {BIZ.phone} · {BIZ.email}
          </p>
        </div>

        <div>
          <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>서비스</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <Link href="/" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              사주
            </Link>
            <Link href="/hub" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              허브
            </Link>
            <Link href="/store" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              스토어
            </Link>
            <Link href="/today" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              띠별 운세
            </Link>
            <Link href="/tarot" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              타로
            </Link>
            <Link
              href="/compatibility"
              style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}
            >
              궁합
            </Link>
            <Link href="/shop" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              구슬·해금
            </Link>
          </div>
        </div>

        <div>
          <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>약관 및 정책</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <Link href="/policy" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              서비스 이용약관
            </Link>
            <Link
              href="/policy/privacy"
              style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}
            >
              개인정보 처리방침
            </Link>
            <Link
              href="/policy/refund"
              style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}
            >
              환불 정책 (웹 7일 · 메일 30일)
            </Link>
            <Link
              href="/policy/business"
              style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}
            >
              사업자 정보
            </Link>
            <Link
              href="/about/engines"
              style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}
            >
              오픈소스 · 라이선스
            </Link>
          </div>
        </div>
      </div>

      <div
        style={{
          maxWidth: 1200,
          margin: "32px auto 0",
          paddingTop: 24,
          borderTop: "1px solid var(--border)",
          textAlign: "center",
          fontSize: 12,
          color: "var(--muted)",
          lineHeight: 1.6,
        }}
      >
        © {new Date().getFullYear()} FortuneOne. All rights reserved.
        <br />
        운세 결과는 참고용이며 투자·법률·의료 자문이 아닙니다. 다시보기: 웹 7일 · 이메일 링크 30일.
      </div>
    </footer>
  );
}
