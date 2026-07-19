"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  FORTUNE_STORAGE_KEY,
  postFortuneSaju,
  type SajuRequestBody,
} from "@/lib/api";

export function SajuForm() {
  const router = useRouter();
  const [solarDate, setSolarDate] = useState("");
  const [hour, setHour] = useState("12");
  const [minute, setMinute] = useState("0");
  const [timeUnknown, setTimeUnknown] = useState(false);
  const [gender, setGender] = useState<"male" | "female">("male");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!solarDate) {
      setError("생년월일을 입력해 주세요.");
      return;
    }

    const body: SajuRequestBody = {
      solar_date: solarDate,
      hour: timeUnknown ? 12 : Number(hour),
      minute: timeUnknown ? 0 : Number(minute),
      gender,
      time_unknown: timeUnknown,
    };

    if (!timeUnknown) {
      if (Number.isNaN(body.hour) || body.hour < 0 || body.hour > 23) {
        setError("시는 0–23 사이여야 합니다.");
        return;
      }
      if (Number.isNaN(body.minute) || body.minute < 0 || body.minute > 59) {
        setError("분은 0–59 사이여야 합니다.");
        return;
      }
    }

    setLoading(true);
    try {
      const result = await postFortuneSaju(body);
      sessionStorage.setItem(FORTUNE_STORAGE_KEY, JSON.stringify(result));
      router.push("/fortune/result");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "오류가 발생했습니다");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md border-[var(--border)] bg-[var(--card-bg)] shadow-lg">
      <CardHeader className="space-y-1">
        <CardTitle className="text-xl">사주 원국 · 오늘의 운세</CardTitle>
        <CardDescription className="text-[var(--muted)]">
          양력 생년월일을 입력하면 사주 원국과 일운을 바로 확인할 수 있습니다.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="flex flex-col gap-2">
            <label htmlFor="solar_date" className="text-sm font-medium">
              생년월일 (양력)
            </label>
            <Input
              id="solar_date"
              type="date"
              required
              value={solarDate}
              onChange={(e) => setSolarDate(e.target.value)}
              disabled={loading}
              className="border-[var(--border)] bg-[var(--background)]"
            />
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between gap-3">
              <label className="text-sm font-medium">출생 시각</label>
              <label className="flex cursor-pointer items-center gap-2 text-sm text-[var(--muted)]">
                <input
                  type="checkbox"
                  checked={timeUnknown}
                  onChange={(e) => setTimeUnknown(e.target.checked)}
                  disabled={loading}
                  className="h-4 w-4 accent-[var(--primary)]"
                />
                시간 모름
              </label>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1">
                <span className="text-xs text-[var(--muted)]">시 (0–23)</span>
                <Input
                  type="number"
                  min={0}
                  max={23}
                  value={hour}
                  onChange={(e) => setHour(e.target.value)}
                  disabled={loading || timeUnknown}
                  className="border-[var(--border)] bg-[var(--background)] disabled:opacity-50"
                />
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-xs text-[var(--muted)]">분 (0–59)</span>
                <Input
                  type="number"
                  min={0}
                  max={59}
                  value={minute}
                  onChange={(e) => setMinute(e.target.value)}
                  disabled={loading || timeUnknown}
                  className="border-[var(--border)] bg-[var(--background)] disabled:opacity-50"
                />
              </div>
            </div>
            {timeUnknown && (
              <p className="text-xs text-[var(--muted)]">
                시간을 모를 경우 정오(12:00)로 가정하며, 시주는 표시되지 않을 수 있습니다.
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium">성별</span>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setGender("male")}
                disabled={loading}
                className={`rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
                  gender === "male"
                    ? "border-[var(--primary)] bg-[var(--primary-light)] text-[var(--primary)]"
                    : "border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--secondary)]"
                }`}
              >
                남성
              </button>
              <button
                type="button"
                onClick={() => setGender("female")}
                disabled={loading}
                className={`rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
                  gender === "female"
                    ? "border-[var(--primary)] bg-[var(--primary-light)] text-[var(--primary)]"
                    : "border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--secondary)]"
                }`}
              >
                여성
              </button>
            </div>
          </div>

          {error && (
            <p
              role="alert"
              className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-[var(--danger)]"
            >
              {error}
            </p>
          )}

          <Button type="submit" disabled={loading} className="w-full" size="lg">
            {loading ? "계산 중…" : "사주 보기"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
