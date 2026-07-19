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

export { API_URL };
