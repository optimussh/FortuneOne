"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { getPrimaryFullReport } from "@/lib/api";

export default function SharePage() {
  const [line, setLine] = useState("오늘의 운세를 FortuneOne에서 확인했어요");
  const [score, setScore] = useState<number | null>(null);
  const [dayMaster, setDayMaster] = useState("");
  const [color, setColor] = useState("청색");
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    getPrimaryFullReport()
      .then((d) => {
        setScore(d.report.daily.scores.overall ?? null);
        setDayMaster(d.report.day_master);
        setColor(d.report.daily.lucky.color || "청색");
        const s = d.report.daily.sections[0]?.body?.slice(0, 80) || "";
        setLine(s);
      })
      .catch(() => {
        /* guest */
      });
  }, []);

  const share = async () => {
    const text = `FortuneOne 운세\n일간 ${dayMaster || "?"} · 총운 ${score ?? "—"}\n행운색 ${color}\n${line}\nhttps://localhost:6100`;
    if (navigator.share) {
      try {
        await navigator.share({ title: "FortuneOne", text });
        return;
      } catch {
        /* fallthrough */
      }
    }
    await navigator.clipboard.writeText(text);
    alert("공유 문구를 클립보드에 복사했습니다.");
  };

  return (
    <main className="mx-auto max-w-md px-4 py-10">
      <h1 className="text-center text-2xl font-extrabold">공유 카드</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        카톡·SNS에 붙여 넣을 수 있는 한 장
      </p>

      <div
        ref={cardRef}
        className="mt-8 overflow-hidden rounded-3xl p-6 text-white shadow-xl"
        style={{
          background: "linear-gradient(145deg, #4c1d95 0%, #6366f1 50%, #0f172a 100%)",
          minHeight: 280,
        }}
      >
        <div className="text-xs font-semibold tracking-widest opacity-80">FORTUNEONE</div>
        <div className="mt-6 text-sm opacity-90">일간 {dayMaster || "—"}</div>
        <div className="mt-2 text-5xl font-extrabold">{score ?? "—"}</div>
        <div className="mt-1 text-sm opacity-80">오늘의 총운</div>
        <p className="mt-6 text-sm leading-relaxed opacity-95">{line}</p>
        <div className="mt-8 text-xs opacity-75">행운 색 · {color}</div>
      </div>

      <div className="mt-6 flex flex-col gap-2">
        <Button onClick={() => void share()}>공유 / 복사</Button>
        <Button asChild variant="outline">
          <Link href="/hub">허브로</Link>
        </Button>
      </div>
    </main>
  );
}
