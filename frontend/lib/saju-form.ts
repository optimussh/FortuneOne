/** Shared saju form constants (2-hour 시 branches). */

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

export const SAJU_HOURS = [
  { key: "unknown", label: "모름 (태어난 시간)", hour: null as number | null },
  { key: "zi", label: "자시 (23:00–01:00)", hour: 0 },
  { key: "chou", label: "축시 (01:00–03:00)", hour: 2 },
  { key: "yin", label: "인시 (03:00–05:00)", hour: 4 },
  { key: "mao", label: "묘시 (05:00–07:00)", hour: 6 },
  { key: "chen", label: "진시 (07:00–09:00)", hour: 8 },
  { key: "si", label: "사시 (09:00–11:00)", hour: 10 },
  { key: "wu", label: "오시 (11:00–13:00)", hour: 12 },
  { key: "wei", label: "미시 (13:00–15:00)", hour: 14 },
  { key: "shen", label: "신시 (15:00–17:00)", hour: 16 },
  { key: "you", label: "유시 (17:00–19:00)", hour: 18 },
  { key: "xu", label: "술시 (19:00–21:00)", hour: 20 },
  { key: "hai", label: "해시 (21:00–23:00)", hour: 22 },
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
