import Link from "next/link";

/** Placeholder home until Task 3 marketing rewrite. */
export default function HomePage() {
  return (
    <main
      style={{
        maxWidth: 720,
        margin: "0 auto",
        padding: "80px 24px",
        textAlign: "center",
      }}
    >
      <h1
        style={{
          fontSize: 40,
          fontWeight: 800,
          marginBottom: 16,
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}
      >
        FortuneOne
      </h1>
      <p style={{ fontSize: 18, color: "var(--muted)", lineHeight: 1.7, marginBottom: 32 }}>
        사주 · 운세 로컬 MVP
        <br />
        서비스 페이지는 준비 중입니다.
      </p>
      <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
        <Link
          href="/login"
          style={{
            fontSize: 14,
            fontWeight: 600,
            padding: "10px 20px",
            borderRadius: 8,
            color: "#fff",
            background: "var(--primary)",
            textDecoration: "none",
          }}
        >
          로그인
        </Link>
        <Link
          href="/register"
          style={{
            fontSize: 14,
            fontWeight: 600,
            padding: "10px 20px",
            borderRadius: 8,
            color: "var(--primary)",
            border: "1px solid var(--primary)",
            textDecoration: "none",
          }}
        >
          회원가입
        </Link>
      </div>
    </main>
  );
}
