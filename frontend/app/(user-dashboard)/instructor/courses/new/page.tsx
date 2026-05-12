"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function NewCoursePage() {
  const { user } = useAuth();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState(0);
  const [thumbnailUrl, setThumbnailUrl] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      router.push("/login");
      return;
    }
    if (!title.trim()) {
      setError("강의 제목을 입력해주세요");
      return;
    }

    setSaving(true);
    setError("");
    try {
      const res = await apiFetch("/api/courses/", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          price,
          thumbnail_url: thumbnailUrl || null,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "강의 생성에 실패했습니다");
      }
      const course = await res.json();
      router.push(`/instructor/courses/${course.id}/edit`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "오류가 발생했습니다");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", padding: "40px 24px 80px" }}>
      <Link
        href="/instructor/courses"
        style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none", marginBottom: 24, display: "inline-block" }}
      >
        ← 내 강의 목록
      </Link>

      <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 32 }}>새 강의 만들기</h1>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {error && (
          <div style={{ padding: "12px 16px", borderRadius: 10, background: "#fef2f2", color: "#dc2626", fontSize: 13 }}>
            {error}
          </div>
        )}

        <div>
          <label style={{ fontSize: 14, fontWeight: 600, display: "block", marginBottom: 8 }}>
            강의 제목 <span style={{ color: "var(--danger)" }}>*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="예: React 완벽 가이드 2026"
            required
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: 10,
              border: "1px solid var(--border)",
              fontSize: 14,
              background: "var(--card-bg, #fff)",
              outline: "none",
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: 14, fontWeight: 600, display: "block", marginBottom: 8 }}>강의 설명</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="이 강의에서 어떤 것을 배울 수 있는지 설명해주세요..."
            rows={5}
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: 10,
              border: "1px solid var(--border)",
              fontSize: 14,
              background: "var(--card-bg, #fff)",
              outline: "none",
              resize: "vertical",
              lineHeight: 1.6,
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: 14, fontWeight: 600, display: "block", marginBottom: 8 }}>
            가격 (원) — 0이면 무료
          </label>
          <input
            type="number"
            value={price}
            onChange={(e) => setPrice(Number(e.target.value))}
            min={0}
            step={1000}
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: 10,
              border: "1px solid var(--border)",
              fontSize: 14,
              background: "var(--card-bg, #fff)",
              outline: "none",
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: 14, fontWeight: 600, display: "block", marginBottom: 8 }}>
            썸네일 URL (선택)
          </label>
          <input
            type="url"
            value={thumbnailUrl}
            onChange={(e) => setThumbnailUrl(e.target.value)}
            placeholder="https://example.com/thumbnail.jpg"
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: 10,
              border: "1px solid var(--border)",
              fontSize: 14,
              background: "var(--card-bg, #fff)",
              outline: "none",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: 12,
            border: "none",
            background: "var(--primary)",
            color: "#fff",
            fontSize: 16,
            fontWeight: 700,
            cursor: saving ? "not-allowed" : "pointer",
            opacity: saving ? 0.7 : 1,
          }}
        >
          {saving ? "생성 중..." : "강의 생성하기"}
        </button>
      </form>
    </div>
  );
}
