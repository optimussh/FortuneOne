"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface Lesson {
  id: number;
  title: string;
  content_type: string;
  video_source_type: string | null;
  content_url: string | null;
  order_index: number;
}

interface Module {
  id: number;
  title: string;
  order_index: number;
  lessons: Lesson[];
}

interface CourseDetail {
  id: number;
  title: string;
  description: string | null;
  price: number;
  thumbnail_url: string | null;
  instructor_id: number;
  is_published: boolean;
  created_at: string;
  modules: Module[];
  enrollment_count: number | null;
}

export default function CourseDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [enrolled, setEnrolled] = useState(false);
  const [openModules, setOpenModules] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!id) return;
    apiFetch(`/api/courses/${id}`)
      .then((r) => {
        if (!r.ok) throw new Error();
        return r.json();
      })
      .then((data) => {
        setCourse(data);
        // Open first module by default
        if (data.modules?.length > 0) {
          setOpenModules(new Set([data.modules[0].id]));
        }
      })
      .catch(() => setCourse(null))
      .finally(() => setLoading(false));
  }, [id]);

  // Check enrollment status
  useEffect(() => {
    if (!user) return;
    apiFetch("/api/courses/enrolled/my")
      .then((r) => r.json())
      .then((list: { id: number }[]) => {
        if (list.some((c) => c.id === Number(id))) setEnrolled(true);
      })
      .catch(() => {});
  }, [user, id]);

  const handleEnroll = async () => {
    if (!user) {
      router.push("/login");
      return;
    }
    setEnrolling(true);
    try {
      const res = await apiFetch(`/api/courses/${id}/enroll`, { method: "POST" });
      if (res.ok) {
        setEnrolled(true);
      } else {
        const err = await res.json();
        alert(err.detail || "수강 신청에 실패했습니다");
      }
    } catch {
      alert("오류가 발생했습니다");
    } finally {
      setEnrolling(false);
    }
  };

  const toggleModule = (moduleId: number) => {
    setOpenModules((prev) => {
      const next = new Set(prev);
      if (next.has(moduleId)) next.delete(moduleId);
      else next.add(moduleId);
      return next;
    });
  };

  if (loading) {
    return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "60px 24px" }}>
        <div className="skeleton" style={{ height: 40, width: "60%", marginBottom: 16 }} />
        <div className="skeleton" style={{ height: 20, width: "80%", marginBottom: 40 }} />
        <div className="skeleton" style={{ height: 300 }} />
      </div>
    );
  }

  if (!course) {
    return (
      <div style={{ textAlign: "center", padding: "120px 24px", color: "var(--muted)" }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>😢</div>
        <p style={{ fontSize: 18 }}>강의를 찾을 수 없습니다</p>
        <Link
          href="/courses"
          style={{
            display: "inline-block",
            marginTop: 16,
            color: "var(--primary)",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          ← 강의 목록으로
        </Link>
      </div>
    );
  }

  const totalLessons = course.modules.reduce((a, m) => a + m.lessons.length, 0);

  return (
    <div>
      {/* Hero banner */}
      <div
        style={{
          background: "linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)",
          padding: "60px 24px",
          color: "#fff",
        }}
      >
        <div style={{ maxWidth: 1000, margin: "0 auto" }}>
          <Link
            href="/courses"
            style={{ color: "rgba(255,255,255,0.7)", fontSize: 13, textDecoration: "none", marginBottom: 16, display: "inline-block" }}
          >
            ← 강의 목록
          </Link>
          <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 12, lineHeight: 1.3 }}>
            {course.title}
          </h1>
          <p style={{ fontSize: 16, opacity: 0.85, lineHeight: 1.7, maxWidth: 600, marginBottom: 20 }}>
            {course.description || ""}
          </p>
          <div style={{ display: "flex", gap: 20, fontSize: 13, opacity: 0.7 }}>
            <span>📚 {course.modules.length}개 섹션</span>
            <span>🎬 {totalLessons}개 강의</span>
            {course.enrollment_count !== null && (
              <span>👥 {course.enrollment_count}명 수강 중</span>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div
        style={{
          maxWidth: 1000,
          margin: "0 auto",
          padding: "40px 24px 80px",
          display: "grid",
          gridTemplateColumns: "1fr 320px",
          gap: 40,
        }}
      >
        {/* Left: Curriculum */}
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>커리큘럼</h2>
          {course.modules.length === 0 ? (
            <p style={{ color: "var(--muted)", fontSize: 14 }}>아직 커리큘럼이 등록되지 않았습니다.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {course.modules
                .sort((a, b) => a.order_index - b.order_index)
                .map((mod) => (
                  <div
                    key={mod.id}
                    style={{
                      border: "1px solid var(--border)",
                      borderRadius: 12,
                      overflow: "hidden",
                    }}
                  >
                    <button
                      onClick={() => toggleModule(mod.id)}
                      style={{
                        width: "100%",
                        padding: "14px 18px",
                        background: "var(--secondary)",
                        border: "none",
                        cursor: "pointer",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        fontSize: 14,
                        fontWeight: 600,
                      }}
                    >
                      <span>{mod.title}</span>
                      <span style={{ fontSize: 12, color: "var(--muted)" }}>
                        {mod.lessons.length}개 강의 {openModules.has(mod.id) ? "▲" : "▼"}
                      </span>
                    </button>
                    {openModules.has(mod.id) && (
                      <div>
                        {mod.lessons
                          .sort((a, b) => a.order_index - b.order_index)
                          .map((lesson) => (
                            <div
                              key={lesson.id}
                              style={{
                                padding: "12px 18px 12px 32px",
                                borderTop: "1px solid var(--border)",
                                fontSize: 13,
                                display: "flex",
                                alignItems: "center",
                                gap: 10,
                              }}
                            >
                              <span>{lesson.content_type === "video" ? "🎬" : "📝"}</span>
                              <span>{lesson.title}</span>
                            </div>
                          ))}
                        {mod.lessons.length === 0 && (
                          <div style={{ padding: "12px 18px 12px 32px", fontSize: 13, color: "var(--muted)" }}>
                            아직 강의가 없습니다
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Right: Enroll Card */}
        <div>
          <div
            style={{
              position: "sticky",
              top: 88,
              background: "var(--card-bg, #fff)",
              border: "1px solid var(--border)",
              borderRadius: 16,
              padding: 24,
              boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
            }}
          >
            {/* Thumbnail */}
            <div
              style={{
                height: 160,
                borderRadius: 10,
                marginBottom: 20,
                background: course.thumbnail_url
                  ? `url(${course.thumbnail_url}) center/cover`
                  : "linear-gradient(135deg, #6366f1, #8b5cf6)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontSize: 40,
              }}
            >
              {!course.thumbnail_url && "📚"}
            </div>

            <div style={{ fontSize: 28, fontWeight: 800, marginBottom: 20, textAlign: "center" }}>
              {course.price > 0 ? (
                <span style={{ color: "var(--primary)" }}>₩{course.price.toLocaleString()}</span>
              ) : (
                <span style={{ color: "var(--accent)" }}>무료</span>
              )}
            </div>

            {enrolled ? (
              <div
                style={{
                  width: "100%",
                  padding: "14px",
                  borderRadius: 12,
                  background: "var(--accent)",
                  color: "#fff",
                  textAlign: "center",
                  fontWeight: 700,
                  fontSize: 15,
                }}
              >
                ✓ 수강 중
              </div>
            ) : (
              <button
                onClick={handleEnroll}
                disabled={enrolling}
                style={{
                  width: "100%",
                  padding: "14px",
                  borderRadius: 12,
                  border: "none",
                  background: "var(--primary)",
                  color: "#fff",
                  fontWeight: 700,
                  fontSize: 15,
                  cursor: enrolling ? "not-allowed" : "pointer",
                  opacity: enrolling ? 0.7 : 1,
                }}
              >
                {enrolling ? "처리 중..." : course.price > 0 ? "수강 신청" : "무료 수강하기"}
              </button>
            )}

            <div
              style={{
                marginTop: 20,
                fontSize: 12,
                color: "var(--muted)",
                lineHeight: 1.8,
              }}
            >
              <div>✓ 평생 무제한 수강</div>
              <div>✓ 모바일 지원</div>
              <div>✓ 수료증 제공</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
