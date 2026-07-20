"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { registerWithSaju } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [solarDate, setSolarDate] = useState("");
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(0);
  const [timeUnknown, setTimeUnknown] = useState(true);
  const [gender, setGender] = useState<"male" | "female">("male");
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
    if (!solarDate) {
      setError("생년월일(양력)을 입력해 주세요");
      return;
    }

    setIsLoading(true);
    try {
      const data = await registerWithSaju({
        email,
        password,
        password_confirm: passwordConfirm,
        saju: {
          solar_date: solarDate,
          hour: timeUnknown ? 12 : hour,
          minute: timeUnknown ? 0 : minute,
          time_unknown: timeUnknown,
          gender,
          label: "나",
        },
      });
      localStorage.setItem("token", data.access_token);
      router.push("/hub");
      router.refresh();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  };

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
          padding: "40px 36px",
          border: "1px solid var(--border)",
          boxShadow: "0 8px 40px rgba(0,0,0,0.06)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 28 }}>
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
            가입 시 기본 사주 정보를 함께 등록합니다
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
              marginTop: 8,
              paddingTop: 16,
              borderTop: "1px solid var(--border)",
            }}
          >
            <p style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>기본 사주 정보</p>
            <div style={{ marginBottom: 12 }}>
              <label style={label}>생년월일 (양력) *</label>
              <input
                type="date"
                required
                value={solarDate}
                onChange={(e) => setSolarDate(e.target.value)}
                style={field}
              />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={label}>성별 *</label>
              <div style={{ display: "flex", gap: 8 }}>
                <button
                  type="button"
                  onClick={() => setGender("male")}
                  style={{
                    flex: 1,
                    padding: 10,
                    borderRadius: 10,
                    border: gender === "male" ? "2px solid var(--primary)" : "1px solid var(--border)",
                    background: gender === "male" ? "var(--primary-light)" : "#fff",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  남성
                </button>
                <button
                  type="button"
                  onClick={() => setGender("female")}
                  style={{
                    flex: 1,
                    padding: 10,
                    borderRadius: 10,
                    border: gender === "female" ? "2px solid var(--primary)" : "1px solid var(--border)",
                    background: gender === "female" ? "var(--primary-light)" : "#fff",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  여성
                </button>
              </div>
            </div>
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, marginBottom: 10 }}>
              <input
                type="checkbox"
                checked={timeUnknown}
                onChange={(e) => setTimeUnknown(e.target.checked)}
              />
              태어난 시간 모름 (정오 가정)
            </label>
            {!timeUnknown && (
              <div style={{ display: "flex", gap: 8 }}>
                <div style={{ flex: 1 }}>
                  <label style={label}>시</label>
                  <input
                    type="number"
                    min={0}
                    max={23}
                    value={hour}
                    onChange={(e) => setHour(Number(e.target.value))}
                    style={field}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={label}>분</label>
                  <input
                    type="number"
                    min={0}
                    max={59}
                    value={minute}
                    onChange={(e) => setMinute(Number(e.target.value))}
                    style={field}
                  />
                </div>
              </div>
            )}
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
