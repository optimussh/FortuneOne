import Link from "next/link";

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
        {/* Brand */}
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
            FortuneOne
          </div>
          <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.7 }}>
            사주 · 운세 · 타로 · 궁합
            <br />
            로컬 제품 데모
          </p>
        </div>

        {/* Links */}
        <div>
          <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>서비스</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <Link href="/" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              사주
            </Link>
            <Link href="/today" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              띠별 운세
            </Link>
            <Link href="/tarot" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              타로
            </Link>
            <Link href="/compatibility" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              궁합
            </Link>
            <Link href="/login" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              로그인
            </Link>
          </div>
        </div>

        {/* Policy */}
        <div>
          <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>약관 및 정책</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <Link href="/policy" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              서비스 이용약관
            </Link>
            <Link href="/policy/privacy" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
              개인정보 처리방침
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
        }}
      >
        © {new Date().getFullYear()} FortuneOne. All rights reserved.
      </div>
    </footer>
  );
}
