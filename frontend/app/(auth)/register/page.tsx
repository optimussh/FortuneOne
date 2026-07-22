"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { registerWithSaju } from "@/lib/api";
import { SajuDetailForm } from "@/components/fortune/SajuDetailForm";
import {
  defaultSajuForm,
  formToHour,
  formToSolarDate,
  setActiveProfileId,
  type SajuFormValue,
} from "@/lib/saju-form";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [saju, setSaju] = useState<SajuFormValue>(defaultSajuForm());
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const field: React.CSSProperties = {
    width: "100%",
    padding: "12px 14px",
    borderRadius: 10,
    border: "1px solid var(--border)",
    fontSize: 15,
  };
  const label: React.CSSProperties = {
    fontSize: 13,
    fontWeight: 600,
    display: "block",
    marginBottom: 6,
  };

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
    if (!saju.display_name.trim()) {
      setError("이름을 입력하세요");
      return;
    }

    setIsLoading(true);
    try {
      const { hour, time_unknown } = formToHour(saju);
      const data = await registerWithSaju({
        email,
        password,
        password_confirm: passwordConfirm,
        saju: {
          display_name: saju.display_name.trim(),
          label: saju.label || "본인",
          birth_year: saju.birth_year,
          birth_month: saju.birth_month,
          birth_day: saju.birth_day,
          time_slot: saju.time_slot,
          calendar_type: saju.calendar_type,
          gender: saju.gender,
          solar_date: formToSolarDate(saju),
          hour,
          minute: 0,
          time_unknown,
        },
      });
      localStorage.setItem("token", data.access_token);
      if (data.profile?.id) setActiveProfileId(data.profile.id);
      router.push("/welcome");
      router.refresh();
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
          maxWidth: 480,
          background: "var(--card-bg, #fff)",
          borderRadius: 20,
          padding: "36px 32px",
          border: "1px solid var(--border)",
          boxShadow: "0 8px 40px rgba(0,0,0,0.06)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 24 }}>
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
            계정 + 상세 사주 정보 등록
          </p>
        </div>

        <form onSubmit={handleRegister} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label style={label}>이메일</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} style={field} />
          </div>
          <div>
            <label style={label}>비밀번호 (6자 이상)</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={field}
            />
          </div>
          <div>
            <label style={label}>비밀번호 확인</label>
            <input
              type="password"
              required
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              style={field}
            />
          </div>

          <div
            style={{
              marginTop: 4,
              paddingTop: 16,
              borderTop: "1px solid var(--border)",
            }}
          >
            <p style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>사주 정보</p>
            <SajuDetailForm value={saju} onChange={setSaju} showRelation />
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
            {isLoading ? "가입 중…" : "가입하고 내 운세 보기"}
          </button>
        </form>

        <p style={{ marginTop: 20, textAlign: "center", fontSize: 14, color: "var(--muted)" }}>
          이미 계정이 있나요?{" "}
          <Link href="/login" style={{ color: "var(--primary)", fontWeight: 600 }}>
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
