"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useState } from "react";

export function Header() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        backdropFilter: "blur(12px)",
        backgroundColor: "rgba(255,255,255,0.85)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <nav
        style={{
          maxWidth: 1200,
          margin: "0 auto",
          padding: "0 24px",
          height: 64,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            fontSize: 22,
            fontWeight: 800,
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            textDecoration: "none",
          }}
        >
          FortuneOne
        </Link>

        {/* Desktop nav */}
        <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
          <Link
            href="/"
            style={{
              fontSize: 15,
              fontWeight: 500,
              color: "var(--foreground)",
              textDecoration: "none",
              transition: "color 0.2s",
            }}
          >
            홈
          </Link>

          {user ? (
            <div style={{ position: "relative" }}>
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                  color: "#fff",
                  border: "none",
                  cursor: "pointer",
                  fontSize: 14,
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {user.email[0].toUpperCase()}
              </button>
              {menuOpen && (
                <div
                  style={{
                    position: "absolute",
                    right: 0,
                    top: 44,
                    background: "var(--card-bg, #fff)",
                    border: "1px solid var(--border)",
                    borderRadius: 12,
                    padding: 8,
                    minWidth: 200,
                    boxShadow: "0 8px 30px rgba(0,0,0,0.12)",
                  }}
                >
                  <div
                    style={{
                      padding: "8px 12px",
                      fontSize: 13,
                      color: "var(--muted)",
                      borderBottom: "1px solid var(--border)",
                      marginBottom: 4,
                    }}
                  >
                    {user.email}
                  </div>
                  <Link
                    href="/"
                    onClick={() => setMenuOpen(false)}
                    style={{
                      display: "block",
                      padding: "8px 12px",
                      fontSize: 14,
                      color: "var(--foreground)",
                      textDecoration: "none",
                      borderRadius: 8,
                    }}
                  >
                    홈
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      setMenuOpen(false);
                    }}
                    style={{
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 12px",
                      fontSize: 14,
                      color: "var(--danger)",
                      background: "none",
                      border: "none",
                      borderRadius: 8,
                      cursor: "pointer",
                    }}
                  >
                    로그아웃
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: "flex", gap: 8 }}>
              <Link
                href="/login"
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  padding: "8px 16px",
                  borderRadius: 8,
                  color: "var(--primary)",
                  textDecoration: "none",
                  border: "1px solid var(--primary)",
                  transition: "all 0.2s",
                }}
              >
                로그인
              </Link>
              <Link
                href="/register"
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  padding: "8px 16px",
                  borderRadius: 8,
                  color: "#fff",
                  background: "var(--primary)",
                  textDecoration: "none",
                  transition: "all 0.2s",
                }}
              >
                회원가입
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
