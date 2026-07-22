/** Shared saju form constants — 12 시진 (KST 30분 보정 표). */

export const RELATION_OPTIONS = [
  "본인",
  "엄마",
  "아빠",
  "배우자",
  "애인",
  "자녀",
  "친구",
  "기타",
] as const;

/** 널리 쓰이는 KST 기준 12시진 (자시 23:30 시작). hour = 엔진 대표 시각 */
export const SAJU_HOURS = [
  { key: "unknown", label: "모름 (태어난 시간)", hour: null as number | null },
  { key: "zi", label: "자시 (子) 23:30–01:29", hour: 0 },
  { key: "chou", label: "축시 (丑) 01:30–03:29", hour: 2 },
  { key: "yin", label: "인시 (寅) 03:30–05:29", hour: 4 },
  { key: "mao", label: "묘시 (卯) 05:30–07:29", hour: 6 },
  { key: "chen", label: "진시 (辰) 07:30–09:29", hour: 8 },
  { key: "si", label: "사시 (巳) 09:30–11:29", hour: 10 },
  { key: "wu", label: "오시 (午) 11:30–13:29", hour: 12 },
  { key: "wei", label: "미시 (未) 13:30–15:29", hour: 14 },
  { key: "shen", label: "신시 (申) 15:30–17:29", hour: 16 },
  { key: "you", label: "유시 (酉) 17:30–19:29", hour: 18 },
  { key: "xu", label: "술시 (戌) 19:30–21:29", hour: 20 },
  { key: "hai", label: "해시 (亥) 21:30–23:29", hour: 22 },
] as const;

export const YEARS = Array.from({ length: 2026 - 1920 + 1 }, (_, i) => 2026 - i);
export const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);
export const DAYS = Array.from({ length: 31 }, (_, i) => i + 1);

export type SajuFormValue = {
  label: string;
  display_name: string;
  gender: "male" | "female";
  birth_year: number;
  birth_month: number;
  birth_day: number;
  time_slot: string;
  calendar_type: "solar" | "lunar";
};

export const defaultSajuForm = (): SajuFormValue => ({
  label: "본인",
  display_name: "",
  gender: "male",
  birth_year: 1990,
  birth_month: 1,
  birth_day: 1,
  time_slot: "unknown",
  calendar_type: "solar",
});

export function formToSolarDate(v: SajuFormValue): string {
  const m = String(v.birth_month).padStart(2, "0");
  const d = String(v.birth_day).padStart(2, "0");
  return `${v.birth_year}-${m}-${d}`;
}

export function formToHour(v: SajuFormValue): { hour: number; time_unknown: boolean } {
  const hit = SAJU_HOURS.find((h) => h.key === v.time_slot);
  if (!hit || hit.hour === null) return { hour: 12, time_unknown: true };
  return { hour: hit.hour, time_unknown: false };
}

/** Display saved time_slot (e.g. chen → 진시 (辰) 07:30–09:29). */
export function formatTimeSlotLabel(
  time_slot?: string | null,
  hour?: number | null,
  time_unknown?: boolean
): string {
  if (time_unknown || !time_slot || time_slot === "unknown") {
    if (time_unknown) return "시간 모름";
  }
  const hit = SAJU_HOURS.find((h) => h.key === time_slot);
  if (hit) {
    if (hit.hour === null) return "시간 모름";
    return hit.label;
  }
  if (hour != null && Number.isFinite(hour)) {
    // reverse lookup by representative hour
    const byHour = SAJU_HOURS.find((h) => h.hour === hour);
    if (byHour) return byHour.label;
    return `${hour}시`;
  }
  return "시간 모름";
}

export const ACTIVE_PROFILE_KEY = "fortune:activeProfileId";

export function getActiveProfileId(): number | null {
  if (typeof window === "undefined") return null;
  const v = localStorage.getItem(ACTIVE_PROFILE_KEY);
  if (!v) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

export function setActiveProfileId(id: number | null) {
  if (typeof window === "undefined") return;
  if (id == null) localStorage.removeItem(ACTIVE_PROFILE_KEY);
  else localStorage.setItem(ACTIVE_PROFILE_KEY, String(id));
}
