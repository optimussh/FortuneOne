"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface CourseItem {
  id: number;
  title: string;
  description: string | null;
  price: number;
  thumbnail_url: string | null;
}

export default function MyLearningPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [courses, setCourses] = useState<CourseItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    apiFetch("/api/courses/enrolled/my")
      .then((r) => r.json())
      .then(setCourses)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, authLoading, router]);

  if (authLoading || loading) {
    return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "60px 24px" }}>
        <div className="skeleton" style={{ height: 36, width: 200, marginBottom: 32 }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 20 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ borderRadius: 14, overflow: "hidden" }}>
              <div className="skeleton" style={{ height: 150 }} />
              <div style={{ padding: 16 }}>
                <div className="skeleton" style={{ height: 20, marginBottom: 8 }} />
                <div className="skeleton" style={{ height: 14, width: "60%" }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 24px 80px" }}>
      <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 32 }}>내 학습</h1>

      {courses.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "80px 0",
            background: "var(--card-bg, #fff)",
            borderRadius: 16,
            border: "1px solid var(--border)",
          }}
        >
          <div style={{ fontSize: 48, marginBottom: 16 }}>📖</div>
          <p style={{ fontSize: 16, color: "var(--muted)", marginBottom: 16 }}>
            아직 수강 중인 강의가 없습니다
          </p>
          <Link
            href="/courses"
            style={{
              display: "inline-block",
              padding: "10px 24px",
              borderRadius: 10,
              background: "var(--primary)",
              color: "#fff",
              fontWeight: 600,
              fontSize: 14,
              textDecoration: "none",
            }}
          >
            강의 둘러보기
          </Link>
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
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
                    : "linear-gradient(135deg, #6366f1, #8b5cf6)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#fff",
                  fontSize: 36,
                }}
              >
                {!c.thumbnail_url && "📚"}
              </div>
              <div style={{ padding: "16px 18px" }}>
                <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>{c.title}</h3>
                <div
                  style={{
                    display: "inline-block",
                    padding: "4px 10px",
                    borderRadius: 6,
                    background: "#dcfce7",
                    color: "#16a34a",
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                >
                  수강 중
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
