const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  return res;
}

export type StemBranch = {
  stem: string;
  branch: string;
};

export type SajuRequestBody = {
  solar_date: string;
  hour: number;
  minute: number;
  gender: "male" | "female";
  time_unknown: boolean;
};

export type AffiliateItem = {
  id: string;
  title: string;
  reason: string;
  price_hint: string;
  url: string;
  partner: string;
  element: string;
};

export type SajuResponse = {
  input: {
    solar_date: string;
    hour: number;
    minute: number;
    gender: string;
    time_assumed: boolean;
  };
  pillars: {
    year: StemBranch;
    month: StemBranch;
    day: StemBranch;
    hour: StemBranch | null;
  };
  day_master: string;
  elements: Record<string, number>;
  daily: {
    date: string;
    summary: string;
    scores: Record<string, number>;
    lucky: Record<string, string>;
  };
  weak_elements?: string[];
  strong_elements?: string[];
  yongsin?: {
    element: string;
    element_ko: string;
    reason: string;
    lifestyle: string[];
  } | null;
  daeun?: {
    start_age: number;
    end_age: number;
    label: string;
    note: string;
    is_current: boolean;
  }[];
  lucky_items?: AffiliateItem[];
};

export const FORTUNE_STORAGE_KEY = "fortune:last";

function parseApiError(text: string, fallback: string): string {
  try {
    const data = JSON.parse(text) as { detail?: string | { msg?: string }[] };
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail))
      return data.detail.map((d) => d.msg).filter(Boolean).join(", ") || fallback;
  } catch {
    /* ignore */
  }
  return text || fallback;
}

async function publicJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers as Record<string, string>),
    },
  });
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "요청에 실패했습니다"));
  }
  return res.json();
}

export async function postFortuneSaju(body: SajuRequestBody): Promise<SajuResponse> {
  return publicJson<SajuResponse>("/api/fortune/saju", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export type TarotCard = {
  id: string;
  name: string;
  arcana: string;
  reversed: boolean;
  meaning: string;
  position: string;
};

export async function postTarot(count: number, question: string) {
  return publicJson<{ question: string; cards: TarotCard[]; summary: string }>(
    "/api/fortune/tarot",
    { method: "POST", body: JSON.stringify({ count, question }) }
  );
}

export type ZodiacItem = {
  zodiac: string;
  zodiac_en: string;
  date: string;
  score: number;
  summary: string;
  lucky_color: string;
  do: string;
  dont: string;
};

export async function getZodiacToday() {
  return publicJson<{ date: string; items: ZodiacItem[] }>("/api/fortune/zodiac/today");
}

export async function postCompatibility(a: SajuRequestBody, b: SajuRequestBody) {
  return publicJson<{
    score: number;
    summary: string;
    a_day_master: string;
    b_day_master: string;
  }>("/api/fortune/compatibility", {
    method: "POST",
    body: JSON.stringify({
      a: {
        solar_date: a.solar_date,
        hour: a.hour,
        minute: a.minute,
        gender: a.gender,
        time_unknown: a.time_unknown,
      },
      b: {
        solar_date: b.solar_date,
        hour: b.hour,
        minute: b.minute,
        gender: b.gender,
        time_unknown: b.time_unknown,
      },
    }),
  });
}

export type FortuneProfile = {
  id: number;
  user_id: number;
  label: string;
  solar_date: string;
  hour: number | null;
  minute: number | null;
  time_unknown: boolean;
  gender: string;
  created_at: string;
};

export type FortuneProfileCreateBody = {
  label: string;
  solar_date: string;
  hour?: number | null;
  minute?: number | null;
  time_unknown: boolean;
  gender: "male" | "female";
};

export async function listFortuneProfiles(): Promise<FortuneProfile[]> {
  const res = await apiFetch("/api/profiles");
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "프로필 목록을 불러오지 못했습니다"));
  }
  return res.json();
}

export async function createFortuneProfile(
  body: FortuneProfileCreateBody
): Promise<FortuneProfile> {
  const res = await apiFetch("/api/profiles", {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "프로필 저장에 실패했습니다"));
  }
  return res.json();
}

export async function deleteFortuneProfile(id: number): Promise<void> {
  const res = await apiFetch(`/api/profiles/${id}`, { method: "DELETE" });
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "프로필 삭제에 실패했습니다"));
  }
}

export type ReportSection = { id: string; title: string; body: string };
export type ReportGroup = {
  id: string;
  title: string;
  body?: string;
  sections?: ReportSection[];
};

export type FullReport = {
  day_master: string;
  elements: Record<string, number>;
  weak_elements: string[];
  strong_elements: string[];
  yongsin: {
    element: string;
    element_ko: string;
    reason: string;
    lifestyle: string[];
  } | null;
  pillars: {
    year: StemBranch;
    month: StemBranch;
    day: StemBranch;
    hour: StemBranch | null;
  };
  daily: {
    date: string;
    title: string;
    scores: Record<string, number>;
    lucky: Record<string, string>;
    sections: ReportSection[];
  };
  new_year_2026: {
    year: number;
    title: string;
    subtitle: string;
    sections: ReportSection[];
  };
  five_element: {
    title: string;
    day_master: string;
    elements: Record<string, number>;
    groups: { id: string; title: string; body: string }[];
  };
  life_reading: {
    title: string;
    subtitle: string;
    groups: {
      id: string;
      title: string;
      sections: ReportSection[];
    }[];
  };
};

export async function getPrimaryFullReport(): Promise<{
  profile: FortuneProfile;
  report: FullReport;
}> {
  const res = await apiFetch("/api/profiles/primary/full-report");
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "리포트를 불러오지 못했습니다"));
  }
  return res.json();
}

export async function postFullReport(body: SajuRequestBody): Promise<{
  report: FullReport;
  input: SajuResponse["input"];
}> {
  return publicJson("/api/fortune/full-report", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export type RegisterWithSajuBody = {
  email: string;
  password: string;
  password_confirm: string;
  saju: {
    solar_date: string;
    hour: number;
    minute: number;
    time_unknown: boolean;
    gender: "male" | "female";
    label?: string;
  };
};

export async function registerWithSaju(body: RegisterWithSajuBody): Promise<{
  access_token: string;
  profile: FortuneProfile | null;
}> {
  const res = await apiFetch("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "회원가입에 실패했습니다"));
  }
  return res.json();
}

// --- Engagement / journal / tarot interactive / topics ---

export type StreakInfo = {
  current_streak: number;
  longest_streak: number;
  last_checkin_date: string | null;
  already_checked_in_today: boolean;
  recent_7: boolean[];
};

export async function getStreak(): Promise<StreakInfo> {
  const res = await apiFetch("/api/engagement/streak");
  if (!res.ok) throw new Error(parseApiError(await res.text(), "스트릭 조회 실패"));
  return res.json();
}

export async function postCheckin(source: "hub" | "daily" | "tarot" | "journal" = "hub") {
  const res = await apiFetch("/api/engagement/checkin", {
    method: "POST",
    body: JSON.stringify({ source }),
  });
  if (!res.ok) throw new Error(parseApiError(await res.text(), "출석 실패"));
  return res.json() as Promise<StreakInfo>;
}

export type JournalEntry = {
  id: number;
  entry_date: string;
  mood: number | null;
  body: string;
  linked_overall_score: number | null;
};

export async function listJournal(): Promise<JournalEntry[]> {
  const res = await apiFetch("/api/journal");
  if (!res.ok) throw new Error(parseApiError(await res.text(), "일기 목록 실패"));
  return res.json();
}

export async function upsertJournal(
  entryDate: string,
  body: { mood?: number | null; body: string }
): Promise<JournalEntry> {
  const res = await apiFetch(`/api/journal/${entryDate}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(parseApiError(await res.text(), "일기 저장 실패"));
  return res.json();
}

export async function postTopicFortune(
  topic: "love" | "money" | "work" | "health",
  saju: SajuRequestBody
) {
  return publicJson<{
    topic: string;
    title: string;
    score: number;
    headline: string;
    sections: ReportSection[];
    lucky: { color: string; action: string };
  }>("/api/fortune/topic", {
    method: "POST",
    body: JSON.stringify({ ...saju, topic }),
  });
}

export type TarotRevealCard = {
  id: string;
  name: string;
  arcana: string;
  reversed: boolean;
  meaning: string;
  position: string;
  image_key: string;
  color: string;
  symbol: string;
};

export async function tarotShuffle(body: {
  spread: "daily_one" | "three" | "five" | "yesno";
  question?: string;
  is_daily?: boolean;
}) {
  // apiFetch attaches Bearer when logged in (daily tarot persistence)
  const res = await apiFetch("/api/fortune/tarot/shuffle", {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "카드 섞기 실패"));
  }
  return res.json() as Promise<{
    session_id: string;
    spread: string;
    spread_title: string;
    need: number;
    labels: string[];
    deck_face_down: { slot_id: string }[];
  }>;
}

export async function tarotReveal(sessionId: string, picked_slot_ids: string[]) {
  return publicJson<{
    question: string;
    spread: string;
    cards: TarotRevealCard[];
    summary: string;
  }>("/api/fortune/tarot/reveal", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, picked_slot_ids }),
  });
}

export async function getDailyTarotToday() {
  const res = await apiFetch("/api/fortune/tarot/daily/today");
  if (!res.ok) throw new Error(parseApiError(await res.text(), "일일 타로 조회 실패"));
  return res.json() as Promise<{
    drawn: boolean;
    date: string;
    card?: TarotRevealCard;
    question?: string;
  }>;
}

export { API_URL };
