"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface CourseItem {
  id: number;
  title: string;
  description: string | null;
  price: number;
  thumbnail_url: string | null;
  instructor_id: number;
  is_published: boolean;
}

export default function HomePage() {
  const [courses, setCourses] = useState<CourseItem[]>([]);

  useEffect(() => {
    apiFetch("/api/courses/?limit=8")
      .then((r) => r.json())
      .then(setCourses)
      .catch(() => {});
  }, []);

  return (
    <div>
      {/* Hero Section */}
      <section
        className="hero-gradient"
        style={{
          padding: "100px 24px 80px",
          textAlign: "center",
          color: "#fff",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ position: "relative", zIndex: 1, maxWidth: 720, margin: "0 auto" }}>
          <h1
            className="animate-fade-in-up"
            style={{
              fontSize: "clamp(32px, 5vw, 52px)",
              fontWeight: 900,
              lineHeight: 1.2,
              marginBottom: 20,
            }}
          >
            성장을 위한 최고의 선택,
            <br />
            <span style={{ opacity: 0.9 }}>노우브릿지</span>
          </h1>
          <p
            className="animate-fade-in-up"
            style={{
              fontSize: "clamp(16px, 2vw, 20px)",
              opacity: 0.9,
              lineHeight: 1.7,
              marginBottom: 36,
              animationDelay: "0.1s",
            }}
          >
            실무에 바로 적용할 수 있는 프리미엄 강의를 만나보세요.
            <br />
            누구나 자신의 지식을 나눌 수 있습니다.
          </p>
          <div
            className="animate-fade-in-up"
            style={{ display: "flex", gap: 12, justifyContent: "center", animationDelay: "0.2s" }}
          >
            <Link
              href="/courses"
              style={{
                padding: "14px 32px",
                borderRadius: 12,
                background: "#fff",
                color: "#6366f1",
                fontWeight: 700,
                fontSize: 16,
                textDecoration: "none",
                transition: "transform 0.2s",
              }}
            >
              강의 둘러보기
            </Link>
            <Link
              href="/register"
              style={{
                padding: "14px 32px",
                borderRadius: 12,
                background: "rgba(255,255,255,0.2)",
                color: "#fff",
                fontWeight: 700,
                fontSize: 16,
                textDecoration: "none",
                border: "1px solid rgba(255,255,255,0.3)",
                backdropFilter: "blur(8px)",
              }}
            >
              무료 시작하기
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ maxWidth: 1200, margin: "0 auto", padding: "80px 24px" }}>
        <h2
          style={{
            fontSize: 28,
            fontWeight: 800,
            textAlign: "center",
            marginBottom: 48,
          }}
        >
          왜 노우브릿지인가요?
        </h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 24,
          }}
        >
          {[
            {
              icon: "🎯",
              title: "실무 중심 커리큘럼",
              desc: "현업 전문가들이 직접 설계한 커리큘럼으로 실무에 바로 적용할 수 있는 스킬을 배웁니다.",
            },
            {
              icon: "🌍",
              title: "지식 공유 플랫폼",
              desc: "누구나 자신의 전문 지식을 강의로 만들어 공유할 수 있습니다. 가르치면서 더 성장하세요.",
            },
            {
              icon: "⚡",
              title: "평생 수강 & 즉시 시작",
              desc: "한 번 수강하면 평생 접근 가능합니다. 가입 즉시 학습을 시작할 수 있습니다.",
            },
          ].map((f) => (
            <div
              key={f.title}
              className="card-hover"
              style={{
                background: "var(--card-bg, #fff)",
                borderRadius: 16,
                padding: "36px 28px",
                border: "1px solid var(--border)",
                boxShadow: "var(--card-shadow)",
              }}
            >
              <div style={{ fontSize: 36, marginBottom: 16 }}>{f.icon}</div>
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontSize: 14, color: "var(--muted)", lineHeight: 1.7 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Latest Courses */}
      {courses.length > 0 && (
        <section style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px 80px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 32,
            }}
          >
            <h2 style={{ fontSize: 24, fontWeight: 800 }}>최신 강의</h2>
            <Link
              href="/courses"
              style={{ fontSize: 14, color: "var(--primary)", textDecoration: "none", fontWeight: 600 }}
            >
              전체 보기 →
            </Link>
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
              gap: 20,
            }}
          >
            {courses.map((c) => (
              <Link
                key={c.id}
                href={`/courses/${c.id}`}
                className="card-hover"
                style={{
                  textDecoration: "none",
                  color: "inherit",
                  background: "var(--card-bg, #fff)",
                  borderRadius: 14,
                  border: "1px solid var(--border)",
                  overflow: "hidden",
                  boxShadow: "var(--card-shadow)",
                }}
              >
                <div
                  style={{
                    height: 150,
                    background: c.thumbnail_url
                      ? `url(${c.thumbnail_url}) center/cover`
                      : "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#fff",
                    fontSize: 32,
                  }}
                >
                  {!c.thumbnail_url && "📚"}
                </div>
                <div style={{ padding: "16px 18px" }}>
                  <h3
                    style={{
                      fontSize: 15,
                      fontWeight: 700,
                      marginBottom: 6,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {c.title}
                  </h3>
                  <p
                    style={{
                      fontSize: 13,
                      color: "var(--muted)",
                      marginBottom: 8,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {c.description || "강의 설명이 없습니다"}
                  </p>
                  <span
                    style={{
                      fontSize: 15,
                      fontWeight: 800,
                      color: c.price > 0 ? "var(--primary)" : "var(--accent)",
                    }}
                  >
                    {c.price > 0 ? `₩${c.price.toLocaleString()}` : "무료"}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* CTA */}
      <section
        style={{
          background: "var(--primary-light)",
          padding: "64px 24px",
          textAlign: "center",
        }}
      >
        <h2 style={{ fontSize: 28, fontWeight: 800, marginBottom: 16 }}>
          당신의 지식을 세상과 나눠보세요
        </h2>
        <p style={{ fontSize: 16, color: "var(--muted)", marginBottom: 28, maxWidth: 520, margin: "0 auto 28px" }}>
          노우브릿지에서 강의를 만들고 수익을 창출하세요. 전문 지식이 있다면 누구나 강사가 될 수 있습니다.
        </p>
        <Link
          href="/instructor/courses/new"
          style={{
            display: "inline-block",
            padding: "14px 36px",
            borderRadius: 12,
            background: "var(--primary)",
            color: "#fff",
            fontWeight: 700,
            fontSize: 16,
            textDecoration: "none",
          }}
        >
          강의 만들기 시작
        </Link>
      </section>
    </div>
  );
}
