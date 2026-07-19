"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, FORTUNE_STORAGE_KEY } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다");
      return;
    }
    if (password.length < 6) {
      setError("비밀번호는 6자 이상이어야 합니다");
      return;
    }

    setIsLoading(true);
    try {
      const res = await apiFetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          password_confirm: passwordConfirm,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "회원가입에 실패했습니다");
      }

      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);
      const loginRes = await apiFetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });
      if (loginRes.ok) {
        const data = await loginRes.json();
        localStorage.setItem("token", data.access_token);
      }

      if (typeof window !== "undefined" && sessionStorage.getItem(FORTUNE_STORAGE_KEY)) {
        router.push("/fortune/result");
      } else {
        router.push("/");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--background)",
        padding: 24,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 440,
          background: "var(--card-bg, #fff)",
          borderRadius: 20,
          padding: "48px 40px",
          border: "1px solid var(--border)",
          boxShadow: "0 8px 40px rgba(0,0,0,0.06)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <Link
            href="/"
            style={{
              fontSize: 28,
              fontWeight: 800,
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              textDecoration: "none",
            }}
          >
            FortuneOne
          </Link>
          <p style={{ marginTop: 8, fontSize: 14, color: "var(--muted)" }}>
            이메일로 가입 · 사주 저장
          </p>
        </div>

        <form onSubmit={handleRegister} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
              이메일
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: "100%",
                padding: "12px 14px",
                borderRadius: 10,
                border: "1px solid var(--border)",
                fontSize: 15,
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
              비밀번호
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: "100%",
                padding: "12px 14px",
                borderRadius: 10,
                border: "1px solid var(--border)",
                fontSize: 15,
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
              비밀번호 확인
            </label>
            <input
              type="password"
              required
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              style={{
                width: "100%",
                padding: "12px 14px",
                borderRadius: 10,
                border: "1px solid var(--border)",
                fontSize: 15,
              }}
            />
          </div>
          {error && (
            <p style={{ color: "var(--danger)", fontSize: 13, textAlign: "center" }}>{error}</p>
          )}
          <button
            type="submit"
            disabled={isLoading}
            style={{
              marginTop: 8,
              width: "100%",
              padding: "14px",
              borderRadius: 10,
              border: "none",
              background: "var(--primary)",
              color: "#fff",
              fontWeight: 700,
              fontSize: 15,
              cursor: "pointer",
              opacity: isLoading ? 0.7 : 1,
            }}
          >
            {isLoading ? "가입 중…" : "회원가입"}
          </button>
        </form>

        <p style={{ marginTop: 24, textAlign: "center", fontSize: 14, color: "var(--muted)" }}>
          이미 계정이 있나요?{" "}
          <Link href="/login" style={{ color: "var(--primary)", fontWeight: 600 }}>
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
