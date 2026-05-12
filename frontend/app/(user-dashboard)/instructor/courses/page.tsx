"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface CourseItem {
  id: number;
  title: string;
  description: string | null;
  price: number;
  thumbnail_url: string | null;
  is_published: boolean;
  created_at: string;
}

export default function InstructorCoursesPage() {
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
    apiFetch("/api/courses/instructor/my")
      .then((r) => r.json())
      .then(setCourses)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, authLoading, router]);

  const togglePublish = async (courseId: number) => {
    const res = await apiFetch(`/api/courses/${courseId}/publish`, { method: "PATCH" });
    if (res.ok) {
      const updated = await res.json();
      setCourses((prev) => prev.map((c) => (c.id === courseId ? { ...c, is_published: updated.is_published } : c)));
    }
  };

  if (authLoading || loading) {
    return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "60px 24px" }}>
        <div className="skeleton" style={{ height: 40, width: 300, marginBottom: 32 }} />
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton" style={{ height: 80, marginBottom: 12, borderRadius: 12 }} />
        ))}
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 24px 80px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800 }}>내 강의 관리</h1>
        <Link
          href="/instructor/courses/new"
          style={{
            padding: "10px 24px",
            borderRadius: 10,
            background: "var(--primary)",
            color: "#fff",
            fontWeight: 700,
            fontSize: 14,
            textDecoration: "none",
          }}
        >
          + 새 강의 만들기
        </Link>
      </div>

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
          <div style={{ fontSize: 48, marginBottom: 16 }}>🎓</div>
          <p style={{ fontSize: 16, color: "var(--muted)", marginBottom: 16 }}>아직 만든 강의가 없습니다</p>
          <Link
            href="/instructor/courses/new"
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
            첫 번째 강의 만들기
          </Link>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {courses.map((c) => (
            <div
              key={c.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                padding: "16px 20px",
                background: "var(--card-bg, #fff)",
                border: "1px solid var(--border)",
                borderRadius: 14,
                boxShadow: "var(--card-shadow)",
              }}
            >
              {/* Thumbnail mini */}
              <div
                style={{
                  width: 80,
                  height: 56,
                  borderRadius: 8,
                  flexShrink: 0,
                  background: c.thumbnail_url
                    ? `url(${c.thumbnail_url}) center/cover`
                    : "linear-gradient(135deg, #6366f1, #8b5cf6)",
                }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 4, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {c.title}
                </h3>
                <span
                  style={{
                    fontSize: 12,
                    padding: "2px 8px",
                    borderRadius: 6,
                    background: c.is_published ? "#dcfce7" : "var(--secondary)",
                    color: c.is_published ? "#16a34a" : "var(--muted)",
                    fontWeight: 600,
                  }}
                >
                  {c.is_published ? "공개" : "비공개"}
                </span>
              </div>
              <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                <button
                  onClick={() => togglePublish(c.id)}
                  style={{
                    padding: "8px 14px",
                    borderRadius: 8,
                    border: "1px solid var(--border)",
                    background: "var(--card-bg, #fff)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  {c.is_published ? "비공개로" : "공개하기"}
                </button>
                <Link
                  href={`/instructor/courses/${c.id}/edit`}
                  style={{
                    padding: "8px 14px",
                    borderRadius: 8,
                    background: "var(--primary)",
                    color: "#fff",
                    fontSize: 12,
                    fontWeight: 600,
                    textDecoration: "none",
                  }}
                >
                  관리
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
