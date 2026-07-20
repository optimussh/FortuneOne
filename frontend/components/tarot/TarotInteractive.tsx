"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TarotCardBack, TarotCardFace, type TarotVisualCard } from "./TarotCardVisual";
import {
  getDailyTarotToday,
  tarotReveal,
  tarotShuffle,
  type TarotRevealCard,
} from "@/lib/api";

type Phase = "idle" | "shuffling" | "picking" | "revealing" | "done";

const SPREADS = [
  { id: "daily_one" as const, label: "오늘의 1장" },
  { id: "three" as const, label: "3장 (과거·현재·미래)" },
  { id: "five" as const, label: "5장 조언" },
  { id: "yesno" as const, label: "예·아니오" },
];

export function TarotInteractive({
  mode = "free",
}: {
  mode?: "free" | "daily";
}) {
  const [spread, setSpread] = useState<(typeof SPREADS)[number]["id"]>(
    mode === "daily" ? "daily_one" : "three"
  );
  const [question, setQuestion] = useState("");
  const [phase, setPhase] = useState<Phase>("idle");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [need, setNeed] = useState(3);
  const [slots, setSlots] = useState<{ slot_id: string }[]>([]);
  const [picked, setPicked] = useState<string[]>([]);
  const [result, setResult] = useState<TarotRevealCard[] | null>(null);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [spreadTitle, setSpreadTitle] = useState("");
  const [dailyDone, setDailyDone] = useState(false);

  const needLabel = useMemo(() => `${picked.length}/${need}`, [picked, need]);

  const loadDaily = useCallback(async () => {
    if (mode !== "daily") return;
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) {
      try {
        const d = await getDailyTarotToday();
        if (d.drawn && d.card) {
          setDailyDone(true);
          setResult([
            {
              id: d.card.id,
              name: d.card.name,
              arcana: d.card.arcana || "major",
              reversed: d.card.reversed,
              meaning: d.card.meaning,
              position: "현재",
              image_key: d.card.image_key || "",
              color: d.card.color || "#6366f1",
              symbol: d.card.symbol || "✦",
            },
          ]);
          setSummary("오늘의 카드는 이미 뽑았어요. 내일 다시 만나요.");
          setPhase("done");
        }
      } catch {
        /* ignore */
      }
    } else {
      const key = `tarot:daily:${new Date().toISOString().slice(0, 10)}`;
      const saved = localStorage.getItem(key);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setDailyDone(true);
          setResult(parsed.cards);
          setSummary(parsed.summary || "오늘의 카드는 이미 뽑았어요.");
          setPhase("done");
        } catch {
          /* ignore */
        }
      }
    }
  }, [mode]);

  useEffect(() => {
    void loadDaily();
  }, [loadDaily]);

  const startShuffle = async () => {
    setError(null);
    setPhase("shuffling");
    setPicked([]);
    setResult(null);
    try {
      if (mode === "daily") {
        const key = `tarot:daily:${new Date().toISOString().slice(0, 10)}`;
        if (!localStorage.getItem("token") && localStorage.getItem(key)) {
          await loadDaily();
          return;
        }
      }

      await new Promise((r) => setTimeout(r, 1100));
      const data = await tarotShuffle({
        spread: mode === "daily" ? "daily_one" : spread,
        question,
        is_daily: mode === "daily",
      });
      setSessionId(data.session_id);
      setNeed(data.need);
      setSlots(data.deck_face_down);
      setSpreadTitle(data.spread_title);
      setPhase("picking");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "섞기에 실패했습니다";
      setError(
        msg.includes("구슬")
          ? `${msg} · 상점에서 구슬을 충전할 수 있어요 (/shop)`
          : msg
      );
      setPhase("idle");
    }
  };

  const togglePick = (slotId: string) => {
    if (phase !== "picking") return;
    setPicked((prev) => {
      if (prev.includes(slotId)) return prev.filter((x) => x !== slotId);
      if (prev.length >= need) return prev;
      return [...prev, slotId];
    });
  };

  const confirmReveal = async () => {
    if (!sessionId || picked.length !== need) return;
    setPhase("revealing");
    setError(null);
    try {
      await new Promise((r) => setTimeout(r, 350));
      const data = await tarotReveal(sessionId, picked);
      setResult(data.cards);
      setSummary(data.summary);
      setPhase("done");
      if (mode === "daily") {
        setDailyDone(true);
        if (!localStorage.getItem("token")) {
          const key = `tarot:daily:${new Date().toISOString().slice(0, 10)}`;
          localStorage.setItem(
            key,
            JSON.stringify({ cards: data.cards, summary: data.summary })
          );
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "공개 실패");
      setPhase("picking");
    }
  };

  const reset = () => {
    if (mode === "daily" && dailyDone) return;
    setPhase("idle");
    setSessionId(null);
    setSlots([]);
    setPicked([]);
    setResult(null);
    setSummary("");
  };

  return (
    <div className="mx-auto w-full max-w-2xl">
      {phase === "idle" && (
        <div className="space-y-4 rounded-2xl border border-[var(--border)] bg-[var(--card-bg)] p-5 shadow-sm">
          <p className="text-center text-sm text-[var(--muted)]">
            카드를 섞은 뒤, 펼쳐진 뒷면 중에서 직감으로 골라 주세요.
          </p>
          {mode !== "daily" && (
            <div className="flex flex-wrap justify-center gap-2">
              {SPREADS.map((s) => (
                <Button
                  key={s.id}
                  type="button"
                  size="sm"
                  variant={spread === s.id ? "default" : "outline"}
                  onClick={() => setSpread(s.id)}
                >
                  {s.label}
                </Button>
              ))}
            </div>
          )}
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="질문을 마음에 떠올려 보세요 (선택)"
          />
          <Button className="w-full" onClick={() => void startShuffle()}>
            카드 섞고 펼치기
          </Button>
        </div>
      )}

      {phase === "shuffling" && (
        <div className="flex flex-col items-center gap-4 py-16">
          <div className="relative h-28 w-24">
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className="absolute left-0 top-0"
                style={{
                  transform: `translate(${i * 5}px, ${i * -3}px) rotate(${i * 5}deg)`,
                  animation: "pulse 0.8s ease infinite",
                  animationDelay: `${i * 0.08}s`,
                }}
              >
                <TarotCardBack />
              </div>
            ))}
          </div>
          <p className="text-sm font-medium text-[var(--primary)]">카드를 섞는 중…</p>
        </div>
      )}

      {phase === "picking" && (
        <div className="space-y-4">
          <div className="text-center">
            <p className="font-bold">{spreadTitle || "카드 선택"}</p>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {need}장을 골라 주세요 · 선택 {needLabel}
              <br />
              <span className="text-xs">순서가 포지션이 됩니다. 다시 누르면 선택 해제.</span>
            </p>
          </div>
          <div
            className="rounded-2xl p-4 sm:p-6"
            style={{
              background: "radial-gradient(ellipse at center, #312e81 0%, #0f172a 72%)",
              minHeight: 300,
            }}
          >
            <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
              {slots.map((s, idx) => {
                const order = picked.indexOf(s.slot_id);
                const rot = ((idx % 6) - 2.5) * 2.8;
                return (
                  <TarotCardBack
                    key={s.slot_id}
                    selected={order >= 0}
                    order={order >= 0 ? order + 1 : undefined}
                    onClick={() => togglePick(s.slot_id)}
                    style={{ transform: `rotate(${rot}deg)` }}
                  />
                );
              })}
            </div>
          </div>
          <Button
            className="w-full"
            disabled={picked.length !== need}
            onClick={() => void confirmReveal()}
          >
            선택 확정 · 카드 뒤집기
          </Button>
        </div>
      )}

      {(phase === "revealing" || phase === "done") && result && (
        <div className="space-y-6">
          <p className="text-center text-sm text-[var(--muted)]">
            {phase === "revealing" ? "카드를 뒤집는 중…" : summary}
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            {result.map((c, i) => (
              <div key={`${c.id}-${i}`} className="flex flex-col items-center gap-2">
                <p className="text-xs font-semibold text-[var(--primary)]">{c.position}</p>
                <TarotCardFace card={c as TarotVisualCard} size="md" />
                <p className="max-w-[120px] text-center text-xs font-bold">
                  {c.name}
                  {c.reversed ? " (역)" : ""}
                </p>
              </div>
            ))}
          </div>
          <div className="space-y-3">
            {result.map((c, i) => (
              <div
                key={`m-${c.id}-${i}`}
                className="rounded-xl border border-[var(--border)] bg-[var(--card-bg)] p-4 text-sm"
              >
                <div className="font-bold text-[var(--primary)]">
                  {c.position} · {c.name}
                  {c.reversed ? " (역방향)" : ""}
                </div>
                <p className="mt-2 leading-relaxed text-[var(--muted)]">{c.meaning}</p>
              </div>
            ))}
          </div>
          {mode !== "daily" && (
            <Button variant="outline" className="w-full" onClick={reset}>
              다시 섞기
            </Button>
          )}
          {mode === "daily" && dailyDone && (
            <p className="text-center text-xs text-[var(--muted)]">오늘의 타로는 하루 한 번입니다.</p>
          )}
        </div>
      )}

      {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}
    </div>
  );
}
