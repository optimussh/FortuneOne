"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useEffect, useState } from "react";
import { getWallet } from "@/lib/api";

const NAV = [
  { href: "/hub", label: "허브" },
  { href: "/store", label: "스토어" },
  { href: "/", label: "사주" },
  { href: "/tarot", label: "타로" },
  { href: "/today", label: "띠별" },
  { href: "/compatibility", label: "궁합" },
];

export function Header() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [beads, setBeads] = useState<number | null>(null);

  useEffect(() => {
    if (!user) {
      setBeads(null);
      return;
    }
    getWallet()
      .then((w) => setBeads(w.beads))
      .catch(() => setBeads(null));
  }, [user]);

  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        backdropFilter: "blur(12px)",
        backgroundColor: "rgba(255,255,255,0.9)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <nav
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          padding: "0 16px",
          height: 64,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
        }}
      >
        <Link
          href="/"
          style={{
            fontSize: 20,
            fontWeight: 800,
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            textDecoration: "none",
            flexShrink: 0,
          }}
        >
          FortuneOne
        </Link>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            flexWrap: "wrap",
            justifyContent: "flex-end",
          }}
        >
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: "var(--foreground)",
                textDecoration: "none",
                padding: "6px 8px",
              }}
            >
              {item.label}
            </Link>
          ))}

          {user ? (
            <div style={{ position: "relative", display: "flex", alignItems: "center", gap: 8 }}>
              <Link
                href="/shop"
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: "#b45309",
                  textDecoration: "none",
                  padding: "4px 8px",
                  borderRadius: 999,
                  background: "#fef3c7",
                  border: "1px solid #fcd34d",
                }}
                title="구슬 상점"
              >
                ✦ {beads ?? "…"}
              </Link>
              <button
                type="button"
                onClick={() => setMenuOpen(!menuOpen)}
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                  color: "#fff",
                  border: "none",
                  cursor: "pointer",
                  fontSize: 13,
                  fontWeight: 700,
                }}
              >
                {user.email[0].toUpperCase()}
              </button>
              {menuOpen && (
                <div
                  style={{
                    position: "absolute",
                    right: 0,
                    top: 42,
                    background: "#fff",
                    border: "1px solid var(--border)",
                    borderRadius: 12,
                    padding: 8,
                    minWidth: 180,
                    boxShadow: "0 8px 30px rgba(0,0,0,0.12)",
                  }}
                >
                  <div
                    style={{
                      padding: "8px 12px",
                      fontSize: 12,
                      color: "var(--muted)",
                      borderBottom: "1px solid var(--border)",
                    }}
                  >
                    {user.email}
                  </div>
                  <Link
                    href="/hub"
                    onClick={() => setMenuOpen(false)}
                    style={{
                      display: "block",
                      padding: "8px 12px",
                      fontSize: 14,
                      textDecoration: "none",
                      color: "var(--foreground)",
                    }}
                  >
                    데일리 허브
                  </Link>
                  <Link
                    href="/profiles"
                    onClick={() => setMenuOpen(false)}
                    style={{
                      display: "block",
                      padding: "8px 12px",
                      fontSize: 14,
                      textDecoration: "none",
                      color: "var(--foreground)",
                    }}
                  >
                    사주 정보 관리
                  </Link>
                  <Link
                    href="/me"
                    onClick={() => setMenuOpen(false)}
                    style={{
                      display: "block",
                      padding: "8px 12px",
                      fontSize: 14,
                      textDecoration: "none",
                      color: "var(--foreground)",
                    }}
                  >
                    상세 사주
                  </Link>
                  <Link
                    href="/library"
                    onClick={() => setMenuOpen(false)}
                    style={{
                      display: "block",
                      padding: "8px 12px",
                      fontSize: 14,
                      textDecoration: "none",
                      color: "var(--foreground)",
                    }}
                  >
                    내 구매 · 다시보기
                  </Link>
                  <Link
                    href="/shop"
                    onClick={() => setMenuOpen(false)}
                    style={{
                      display: "block",
                      padding: "8px 12px",
                      fontSize: 14,
                      textDecoration: "none",
                      color: "var(--foreground)",
                    }}
                  >
                    구슬 · 상점
                  </Link>
                  <button
                    type="button"
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
                      cursor: "pointer",
                    }}
                  >
                    로그아웃
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: "flex", gap: 6 }}>
              <Link
                href="/login"
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  padding: "6px 12px",
                  borderRadius: 8,
                  color: "var(--primary)",
                  border: "1px solid var(--primary)",
                  textDecoration: "none",
                }}
              >
                로그인
              </Link>
              <Link
                href="/register"
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  padding: "6px 12px",
                  borderRadius: 8,
                  color: "#fff",
                  background: "var(--primary)",
                  textDecoration: "none",
                }}
              >
                가입
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
