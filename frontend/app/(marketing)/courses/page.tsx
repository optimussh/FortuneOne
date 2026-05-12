"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";

interface CourseItem {
  id: number;
  title: string;
  description: string | null;
  price: number;
  thumbnail_url: string | null;
  instructor_id: number;
  is_published: boolean;
  created_at: string;
}

export default function CoursesPage() {
  const [courses, setCourses] = useState<CourseItem[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchCourses = async (q: string = "") => {
    setLoading(true);
    try {
      const res = await apiFetch(`/api/courses/?limit=50&q=${encodeURIComponent(q)}`);
      if (res.ok) setCourses(await res.json());
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCourses(search);
  };

  return (
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: "40px 24px 80px" }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 12 }}>강의 탐색</h1>
        <p style={{ fontSize: 16, color: "var(--muted)", marginBottom: 28 }}>
          다양한 분야의 실무 강의를 둘러보세요
        </p>
        <form
          onSubmit={handleSearch}
          style={{
            display: "flex",
            maxWidth: 520,
            margin: "0 auto",
            gap: 8,
          }}
        >
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="배우고 싶은 기술을 검색해보세요"
            style={{
              flex: 1,
              padding: "12px 18px",
              borderRadius: 12,
              border: "1px solid var(--border)",
              fontSize: 14,
              background: "var(--card-bg, #fff)",
              outline: "none",
            }}
          />
          <button
            type="submit"
            style={{
              padding: "12px 24px",
              borderRadius: 12,
              border: "none",
              background: "var(--primary)",
              color: "#fff",
              fontWeight: 700,
              fontSize: 14,
              cursor: "pointer",
            }}
          >
            검색
          </button>
        </form>
      </div>

      {/* Course Grid */}
      {loading ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: 20,
          }}
        >
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} style={{ borderRadius: 14, overflow: "hidden" }}>
              <div className="skeleton" style={{ height: 160 }} />
              <div style={{ padding: 16 }}>
                <div className="skeleton" style={{ height: 20, marginBottom: 8 }} />
                <div className="skeleton" style={{ height: 14, width: "60%" }} />
              </div>
            </div>
          ))}
        </div>
      ) : courses.length === 0 ? (
        <div style={{ textAlign: "center", padding: "80px 0", color: "var(--muted)" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📚</div>
          <p style={{ fontSize: 16 }}>아직 등록된 강의가 없습니다</p>
          <Link
            href="/instructor/courses/new"
            style={{
              display: "inline-block",
              marginTop: 16,
              padding: "10px 24px",
              borderRadius: 10,
              background: "var(--primary)",
              color: "#fff",
              fontWeight: 600,
              fontSize: 14,
              textDecoration: "none",
            }}
          >
            첫 강의 만들기
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
                  height: 160,
                  background: c.thumbnail_url
                    ? `url(${c.thumbnail_url}) center/cover`
                    : "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#fff",
                  fontSize: 40,
                }}
              >
                {!c.thumbnail_url && "📚"}
              </div>
              <div style={{ padding: "18px 20px" }}>
                <h3
                  style={{
                    fontSize: 16,
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
                    marginBottom: 12,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    lineHeight: 1.5,
                    height: 39,
                  }}
                >
                  {c.description || "강의 설명이 없습니다"}
                </p>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span
                    style={{
                      fontSize: 16,
                      fontWeight: 800,
                      color: c.price > 0 ? "var(--primary)" : "var(--accent)",
                    }}
                  >
                    {c.price > 0 ? `₩${c.price.toLocaleString()}` : "무료"}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
