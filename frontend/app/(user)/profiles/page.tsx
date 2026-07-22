"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  createFortuneProfile,
  deleteFortuneProfile,
  listFortuneProfiles,
  updateFortuneProfile,
  type FortuneProfile,
} from "@/lib/api";
import { SajuDetailForm } from "@/components/fortune/SajuDetailForm";
import {
  ACTIVE_PROFILE_KEY,
  defaultSajuForm,
  formToHour,
  formToSolarDate,
  formatTimeSlotLabel,
  getActiveProfileId,
  setActiveProfileId,
  type SajuFormValue,
} from "@/lib/saju-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function profileToForm(p: FortuneProfile): SajuFormValue {
  const [y, m, d] = p.solar_date.split("-").map(Number);
  return {
    label: p.label || "본인",
    display_name: p.display_name || "",
    gender: p.gender === "female" ? "female" : "male",
    birth_year: p.birth_year || y,
    birth_month: p.birth_month || m,
    birth_day: p.birth_day || d,
    time_slot: p.time_slot || (p.time_unknown ? "unknown" : "wu"),
    calendar_type: p.calendar_type === "lunar" ? "lunar" : "solar",
  };
}

export default function ProfilesPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [list, setList] = useState<FortuneProfile[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [editing, setEditing] = useState<FortuneProfile | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState<SajuFormValue>(defaultSajuForm());
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const rows = await listFortuneProfiles();
    setList(rows);
    let aid = getActiveProfileId();
    if (!aid || !rows.some((r) => r.id === aid)) {
      const self = rows.find((r) => r.is_self || r.label === "본인" || r.label === "나");
      aid = self?.id ?? rows[0]?.id ?? null;
      if (aid) setActiveProfileId(aid);
    }
    setActiveId(aid);
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace("/login?next=/profiles");
      return;
    }
    load().catch((e) => setError(e instanceof Error ? e.message : "실패"));
  }, [user, authLoading, router, load]);

  const selectProfile = (id: number) => {
    setActiveProfileId(id);
    setActiveId(id);
    setMsg("선택 프로필로 전환했습니다. 허브·상세 사주에서 이 사람 기준으로 봅니다.");
  };

  const openEdit = (p: FortuneProfile) => {
    setCreating(false);
    setEditing(p);
    setForm(profileToForm(p));
    setError("");
    setMsg("");
  };

  const openCreate = () => {
    setEditing(null);
    setCreating(true);
    setForm({ ...defaultSajuForm(), label: "친구", display_name: "" });
    setError("");
    setMsg("");
  };

  const save = async () => {
    if (!form.display_name.trim()) {
      setError("이름을 입력하세요");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const { hour, time_unknown } = formToHour(form);
      const body = {
        label: form.label,
        display_name: form.display_name.trim(),
        birth_year: form.birth_year,
        birth_month: form.birth_month,
        birth_day: form.birth_day,
        time_slot: form.time_slot,
        calendar_type: form.calendar_type,
        gender: form.gender,
        solar_date: formToSolarDate(form),
        hour,
        minute: 0,
        time_unknown,
        is_self: form.label === "본인" || form.label === "나",
      };
      if (creating) {
        const p = await createFortuneProfile(body);
        setActiveProfileId(p.id);
        setMsg("새 사주 프로필이 등록되었습니다.");
      } else if (editing) {
        await updateFortuneProfile(editing.id, body);
        setMsg("사주 정보가 저장되었습니다.");
      }
      setCreating(false);
      setEditing(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "저장 실패");
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id: number) => {
    if (!confirm("이 사주 프로필을 삭제할까요?")) return;
    setBusy(true);
    try {
      await deleteFortuneProfile(id);
      if (getActiveProfileId() === id) {
        localStorage.removeItem(ACTIVE_PROFILE_KEY);
      }
      await load();
      setMsg("삭제했습니다.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "삭제 실패");
    } finally {
      setBusy(false);
    }
  };

  if (authLoading) {
    return <main className="py-20 text-center text-sm text-[var(--muted)]">로딩…</main>;
  }

  return (
    <main className="mx-auto max-w-lg px-4 py-10 pb-20">
      <h1 className="text-center text-2xl font-extrabold">사주 프로필</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        본인·가족·지인 사주를 등록하고, 선택해 운세를 봅니다
      </p>

      <div className="mt-6 space-y-3">
        {list.map((p) => (
          <Card
            key={p.id}
            className={`border ${activeId === p.id ? "border-[var(--primary)]" : "border-[var(--border)]"}`}
          >
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-base">
                <span>
                  {p.label} · {p.display_name || "(이름 없음)"}
                  {activeId === p.id && (
                    <span className="ml-2 text-xs font-normal text-[var(--primary)]">선택됨</span>
                  )}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-[var(--muted)]">
              <div>
                {p.gender === "female" ? "여자" : "남자"} · {p.solar_date} ·{" "}
                {p.calendar_type === "lunar" ? "음력" : "양력"} ·{" "}
                {formatTimeSlotLabel(p.time_slot, p.hour, p.time_unknown)}
              </div>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" variant={activeId === p.id ? "default" : "outline"} onClick={() => selectProfile(p.id)}>
                  이 사람으로 보기
                </Button>
                <Button size="sm" variant="outline" onClick={() => openEdit(p)}>
                  사주 수정
                </Button>
                <Button size="sm" variant="outline" onClick={() => void remove(p.id)} disabled={busy}>
                  삭제
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Button className="mt-6 w-full" variant="secondary" onClick={openCreate}>
        + 다른 사람 사주 등록
      </Button>

      {(creating || editing) && (
        <Card className="mt-8 border-[var(--border)]">
          <CardHeader>
            <CardTitle className="text-base">
              {creating ? "새 사주 등록" : "사주 정보 수정"}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <SajuDetailForm value={form} onChange={setForm} showRelation />
            {error && <p className="text-center text-sm text-red-600">{error}</p>}
            {msg && <p className="text-center text-sm text-green-700">{msg}</p>}
            <div className="flex gap-2">
              <Button className="flex-1" onClick={() => void save()} disabled={busy}>
                {busy ? "저장 중…" : "저장"}
              </Button>
              <Button
                className="flex-1"
                variant="outline"
                onClick={() => {
                  setCreating(false);
                  setEditing(null);
                }}
              >
                취소
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {!creating && !editing && msg && (
        <p className="mt-4 text-center text-sm text-green-700">{msg}</p>
      )}
      {error && !creating && !editing && (
        <p className="mt-4 text-center text-sm text-red-600">{error}</p>
      )}

      <div className="mt-8 flex justify-center gap-4 text-sm">
        <Link href="/hub" className="text-[var(--primary)] underline">
          허브에서 운세 보기
        </Link>
        <Link href="/me" className="text-[var(--primary)] underline">
          상세 사주
        </Link>
      </div>
    </main>
  );
}
