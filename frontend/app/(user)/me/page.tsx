"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  FORTUNE_STORAGE_KEY,
  deleteFortuneProfile,
  listFortuneProfiles,
  postFortuneSaju,
  type FortuneProfile,
} from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function MePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [profiles, setProfiles] = useState<FortuneProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const list = await listFortuneProfiles();
      setProfiles(list);
    } catch (err) {
      setError(err instanceof Error ? err.message : "목록을 불러오지 못했습니다");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    void load();
  }, [user, authLoading, router, load]);

  const handleReplay = async (p: FortuneProfile) => {
    setBusyId(p.id);
    setError("");
    try {
      const gender = p.gender === "female" ? "female" : "male";
      const data = await postFortuneSaju({
        solar_date: p.solar_date,
        hour: p.hour ?? 12,
        minute: p.minute ?? 0,
        gender,
        time_unknown: p.time_unknown,
      });
      sessionStorage.setItem(FORTUNE_STORAGE_KEY, JSON.stringify(data));
      router.push("/fortune/result");
    } catch (err) {
      setError(err instanceof Error ? err.message : "사주 계산에 실패했습니다");
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("이 프로필을 삭제할까요?")) return;
    setBusyId(id);
    setError("");
    try {
      await deleteFortuneProfile(id);
      setProfiles((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "삭제에 실패했습니다");
    } finally {
      setBusyId(null);
    }
  };

  if (authLoading || (!user && !error)) {
    return (
      <div className="flex items-center justify-center py-24 text-sm text-[var(--muted)]">
        불러오는 중…
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-8 sm:py-12">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-extrabold sm:text-3xl">내 사주 프로필</h1>
          <p className="mt-2 text-sm text-[var(--muted)]">
            저장한 생년월일로 다시 볼 수 있습니다.
          </p>
        </div>
        <Button asChild variant="outline" size="sm">
          <Link href="/">새 사주 보기</Link>
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <p className="py-12 text-center text-sm text-[var(--muted)]">목록 로딩 중…</p>
      ) : profiles.length === 0 ? (
        <Card className="border-[var(--border)] bg-[var(--card-bg)]">
          <CardHeader>
            <CardTitle className="text-lg">저장된 프로필이 없습니다</CardTitle>
            <CardDescription className="text-[var(--muted)]">
              사주 결과 화면에서 로그인한 뒤 &quot;프로필 저장&quot;을 눌러 주세요.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/">사주 입력하기</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <ul className="flex flex-col gap-3">
          {profiles.map((p) => (
            <li key={p.id}>
              <Card className="border-[var(--border)] bg-[var(--card-bg)]">
                <CardContent className="flex flex-col gap-3 pt-6 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="font-semibold">{p.label}</div>
                    <div className="mt-1 text-sm text-[var(--muted)]">
                      양력 {p.solar_date}
                      {p.time_unknown
                        ? " · 시간 미상"
                        : p.hour != null
                          ? ` · ${String(p.hour).padStart(2, "0")}:${String(p.minute ?? 0).padStart(2, "0")}`
                          : ""}
                      {" · "}
                      {p.gender === "female" ? "여성" : "남성"}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      disabled={busyId === p.id}
                      onClick={() => void handleReplay(p)}
                    >
                      {busyId === p.id ? "계산 중…" : "다시 보기"}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={busyId === p.id}
                      onClick={() => void handleDelete(p.id)}
                    >
                      삭제
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
