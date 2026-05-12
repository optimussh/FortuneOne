"use client";

import { useEffect, useState, useCallback } from "react";
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
  course_id: number;
  lessons: Lesson[];
}

interface CourseDetail {
  id: number;
  title: string;
  description: string | null;
  price: number;
  modules: Module[];
}

export default function EditCoursePage() {
  const { id } = useParams();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Module form
  const [newModuleTitle, setNewModuleTitle] = useState("");
  const [addingModule, setAddingModule] = useState(false);

  // Lesson form per module
  const [activeLessonModule, setActiveLessonModule] = useState<number | null>(null);
  const [lessonTitle, setLessonTitle] = useState("");
  const [lessonType, setLessonType] = useState<"LINK" | "UPLOAD">("LINK");
  const [lessonUrl, setLessonUrl] = useState("");
  const [lessonFile, setLessonFile] = useState<File | null>(null);
  const [addingLesson, setAddingLesson] = useState(false);

  const fetchCourse = useCallback(async () => {
    try {
      const res = await apiFetch(`/api/courses/${id}`);
      if (res.ok) setCourse(await res.json());
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.push("/login"); return; }
    fetchCourse();
  }, [user, authLoading, router, fetchCourse]);

  const handleAddModule = async () => {
    if (!newModuleTitle.trim()) return;
    setAddingModule(true);
    try {
      const res = await apiFetch(`/api/courses/${id}/modules`, {
        method: "POST",
        body: JSON.stringify({ title: newModuleTitle, order_index: (course?.modules.length ?? 0) }),
      });
      if (res.ok) {
        setNewModuleTitle("");
        await fetchCourse();
      }
    } catch {
      /* ignore */
    } finally {
      setAddingModule(false);
    }
  };

  const handleAddLesson = async (moduleId: number) => {
    if (!lessonTitle.trim()) return;
    setAddingLesson(true);
    try {
      if (lessonType === "UPLOAD" && lessonFile) {
        const formData = new FormData();
        formData.append("file", lessonFile);
        formData.append("title", lessonTitle);
        formData.append("order_index", "0");

        const res = await apiFetch(
          `/api/courses/${id}/modules/${moduleId}/lessons/upload?title=${encodeURIComponent(lessonTitle)}&order_index=0`,
          { method: "POST", body: formData }
        );
        if (res.ok) {
          resetLessonForm();
          await fetchCourse();
        }
      } else {
        const res = await apiFetch(`/api/courses/${id}/modules/${moduleId}/lessons`, {
          method: "POST",
          body: JSON.stringify({
            title: lessonTitle,
            content_type: "video",
            video_source_type: "LINK",
            content_url: lessonUrl,
            order_index: 0,
          }),
        });
        if (res.ok) {
          resetLessonForm();
          await fetchCourse();
        }
      }
    } catch {
      /* ignore */
    } finally {
      setAddingLesson(false);
    }
  };

  const resetLessonForm = () => {
    setLessonTitle("");
    setLessonUrl("");
    setLessonFile(null);
    setActiveLessonModule(null);
  };

  if (loading || authLoading) {
    return (
      <div style={{ maxWidth: 800, margin: "0 auto", padding: "60px 24px" }}>
        <div className="skeleton" style={{ height: 36, width: 300, marginBottom: 32 }} />
        <div className="skeleton" style={{ height: 200, borderRadius: 12 }} />
      </div>
    );
  }

  if (!course) {
    return (
      <div style={{ textAlign: "center", padding: "120px 24px", color: "var(--muted)" }}>
        강의를 찾을 수 없습니다
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "40px 24px 80px" }}>
      <Link
        href="/instructor/courses"
        style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none", marginBottom: 24, display: "inline-block" }}
      >
        ← 내 강의 목록
      </Link>

      <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8 }}>커리큘럼 관리</h1>
      <p style={{ color: "var(--muted)", fontSize: 14, marginBottom: 32 }}>{course.title}</p>

      {/* Modules */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {course.modules
          .sort((a, b) => a.order_index - b.order_index)
          .map((mod) => (
            <div
              key={mod.id}
              style={{
                background: "var(--card-bg, #fff)",
                border: "1px solid var(--border)",
                borderRadius: 14,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  padding: "14px 18px",
                  background: "var(--secondary)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <h3 style={{ fontSize: 15, fontWeight: 700 }}>{mod.title}</h3>
                <button
                  onClick={() => setActiveLessonModule(activeLessonModule === mod.id ? null : mod.id)}
                  style={{
                    padding: "6px 12px",
                    borderRadius: 6,
                    border: "1px solid var(--border)",
                    background: "var(--card-bg, #fff)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  + 강의 추가
                </button>
              </div>

              {/* Lessons */}
              {mod.lessons.sort((a, b) => a.order_index - b.order_index).map((lesson) => (
                <div
                  key={lesson.id}
                  style={{
                    padding: "10px 18px 10px 32px",
                    borderTop: "1px solid var(--border)",
                    fontSize: 13,
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                  }}
                >
                  <span>{lesson.content_type === "video" ? "🎬" : "📝"}</span>
                  <span style={{ flex: 1 }}>{lesson.title}</span>
                  <span
                    style={{
                      fontSize: 11,
                      padding: "2px 6px",
                      borderRadius: 4,
                      background: lesson.video_source_type === "UPLOAD" ? "#dbeafe" : "#fef3c7",
                      color: lesson.video_source_type === "UPLOAD" ? "#2563eb" : "#d97706",
                    }}
                  >
                    {lesson.video_source_type === "UPLOAD" ? "업로드" : "링크"}
                  </span>
                </div>
              ))}

              {mod.lessons.length === 0 && (
                <div style={{ padding: "12px 18px 12px 32px", fontSize: 13, color: "var(--muted)" }}>
                  아직 강의가 없습니다
                </div>
              )}

              {/* Add lesson form */}
              {activeLessonModule === mod.id && (
                <div style={{ padding: 18, borderTop: "1px solid var(--border)", background: "var(--primary-light)" }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    <input
                      type="text"
                      value={lessonTitle}
                      onChange={(e) => setLessonTitle(e.target.value)}
                      placeholder="강의 제목"
                      style={{
                        width: "100%",
                        padding: "10px 14px",
                        borderRadius: 8,
                        border: "1px solid var(--border)",
                        fontSize: 13,
                        outline: "none",
                      }}
                    />

                    {/* Type toggle */}
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        type="button"
                        onClick={() => setLessonType("LINK")}
                        style={{
                          padding: "6px 14px",
                          borderRadius: 6,
                          border: "1px solid var(--border)",
                          background: lessonType === "LINK" ? "var(--primary)" : "var(--card-bg, #fff)",
                          color: lessonType === "LINK" ? "#fff" : "inherit",
                          fontSize: 12,
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        🔗 외부 링크
                      </button>
                      <button
                        type="button"
                        onClick={() => setLessonType("UPLOAD")}
                        style={{
                          padding: "6px 14px",
                          borderRadius: 6,
                          border: "1px solid var(--border)",
                          background: lessonType === "UPLOAD" ? "var(--primary)" : "var(--card-bg, #fff)",
                          color: lessonType === "UPLOAD" ? "#fff" : "inherit",
                          fontSize: 12,
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        📤 파일 업로드
                      </button>
                    </div>

                    {lessonType === "LINK" ? (
                      <input
                        type="url"
                        value={lessonUrl}
                        onChange={(e) => setLessonUrl(e.target.value)}
                        placeholder="유튜브, 비메오 또는 직접 링크 URL"
                        style={{
                          width: "100%",
                          padding: "10px 14px",
                          borderRadius: 8,
                          border: "1px solid var(--border)",
                          fontSize: 13,
                          outline: "none",
                        }}
                      />
                    ) : (
                      <input
                        type="file"
                        accept="video/*"
                        onChange={(e) => setLessonFile(e.target.files?.[0] ?? null)}
                        style={{ fontSize: 13 }}
                      />
                    )}

                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        onClick={() => handleAddLesson(mod.id)}
                        disabled={addingLesson}
                        style={{
                          padding: "8px 20px",
                          borderRadius: 8,
                          border: "none",
                          background: "var(--primary)",
                          color: "#fff",
                          fontSize: 13,
                          fontWeight: 600,
                          cursor: addingLesson ? "not-allowed" : "pointer",
                        }}
                      >
                        {addingLesson ? "추가 중..." : "강의 추가"}
                      </button>
                      <button
                        onClick={resetLessonForm}
                        style={{
                          padding: "8px 16px",
                          borderRadius: 8,
                          border: "1px solid var(--border)",
                          background: "var(--card-bg, #fff)",
                          fontSize: 13,
                          cursor: "pointer",
                        }}
                      >
                        취소
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
      </div>

      {/* Add module form */}
      <div
        style={{
          marginTop: 24,
          padding: 20,
          background: "var(--card-bg, #fff)",
          border: "1px dashed var(--border)",
          borderRadius: 14,
          display: "flex",
          gap: 10,
        }}
      >
        <input
          type="text"
          value={newModuleTitle}
          onChange={(e) => setNewModuleTitle(e.target.value)}
          placeholder="새 섹션(모듈) 제목"
          style={{
            flex: 1,
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid var(--border)",
            fontSize: 13,
            outline: "none",
          }}
        />
        <button
          onClick={handleAddModule}
          disabled={addingModule}
          style={{
            padding: "10px 20px",
            borderRadius: 8,
            border: "none",
            background: "var(--primary)",
            color: "#fff",
            fontSize: 13,
            fontWeight: 600,
            cursor: addingModule ? "not-allowed" : "pointer",
            whiteSpace: "nowrap",
          }}
        >
          {addingModule ? "추가 중..." : "섹션 추가"}
        </button>
      </div>
    </div>
  );
}
