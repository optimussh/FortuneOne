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

export type CompatPersonInput = SajuRequestBody & {
  calendar_type?: "solar" | "lunar";
  display_name?: string;
  time_slot?: string;
  is_leap_month?: boolean;
};

export type CompatReport = {
  score: number;
  grade: string;
  summary: string;
  a_day_master: string;
  b_day_master: string;
  relation: { label: string; a_sees_b: string; b_sees_a: string };
  breakdown: {
    day_master: number;
    five_elements: number;
    day_branch: number;
    year_month: number;
    hour: number | null;
  };
  a: {
    display_name: string;
    gender_ko: string;
    calendar_label: string;
    birth_input: string;
    solar_used: string;
    time_text: string;
    day_master: string;
    day_master_nature: string;
    pillars_line: string;
    elements_line: string;
    strong: string;
    weak: string;
  };
  b: CompatReport["a"];
  sections: { id: string; title: string; body: string }[];
  notes: string[];
  disclaimer: string;
};

export async function postCompatibility(a: CompatPersonInput, b: CompatPersonInput) {
  return publicJson<CompatReport>("/api/fortune/compatibility", {
    method: "POST",
    body: JSON.stringify({
      a: {
        solar_date: a.solar_date,
        hour: a.hour,
        minute: a.minute,
        gender: a.gender,
        time_unknown: a.time_unknown,
        calendar_type: a.calendar_type || "solar",
        display_name: a.display_name || "",
        time_slot: a.time_slot || undefined,
        is_leap_month: a.is_leap_month || false,
      },
      b: {
        solar_date: b.solar_date,
        hour: b.hour,
        minute: b.minute,
        gender: b.gender,
        time_unknown: b.time_unknown,
        calendar_type: b.calendar_type || "solar",
        display_name: b.display_name || "",
        time_slot: b.time_slot || undefined,
        is_leap_month: b.is_leap_month || false,
      },
    }),
  });
}

export type FortuneProfile = {
  id: number;
  user_id: number;
  label: string;
  display_name?: string;
  solar_date: string;
  hour: number | null;
  minute: number | null;
  time_unknown: boolean;
  time_slot?: string;
  gender: string;
  calendar_type?: string;
  is_self?: boolean;
  created_at: string;
  birth_year?: number;
  birth_month?: number;
  birth_day?: number;
};

export type FortuneProfileCreateBody = {
  label: string;
  display_name?: string;
  birth_year?: number;
  birth_month?: number;
  birth_day?: number;
  time_slot?: string;
  calendar_type?: "solar" | "lunar";
  solar_date?: string;
  hour?: number | null;
  minute?: number | null;
  time_unknown?: boolean;
  gender: "male" | "female";
  is_self?: boolean;
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

export async function updateFortuneProfile(
  id: number,
  body: Partial<FortuneProfileCreateBody>
): Promise<FortuneProfile> {
  // PUT for wider compatibility (some proxies reject PATCH)
  const res = await apiFetch(`/api/profiles/${id}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "프로필 수정에 실패했습니다"));
  }
  return res.json();
}

export async function deleteFortuneProfile(id: number): Promise<void> {
  const res = await apiFetch(`/api/profiles/${id}`, { method: "DELETE" });
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "프로필 삭제에 실패했습니다"));
  }
}

export async function getProfileFullReport(profileId: number): Promise<{
  profile: FortuneProfile;
  report: FullReport;
}> {
  const res = await apiFetch(`/api/profiles/${profileId}/full-report`);
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), "리포트를 불러오지 못했습니다"));
  }
  return res.json();
}

export type ReportSection = { id: string; title: string; body: string };
export type ReportGroup = {
  id: string;
  title: string;
  body?: string;
  sections?: ReportSection[];
};

export type MingshiColumn = {
  key: string;
  label: string;
  stem: string;
  branch: string;
  stem_god: string;
  branch_god: string;
};

export type MingshiTable = {
  day_master: string;
  columns: MingshiColumn[];
};

export type TojeongReport = {
  year: number;
  title: string;
  subtitle: string;
  header: {
    display_name: string;
    birth_text: string;
    time_text: string;
    pillars_line: string;
    day_master: string;
    elements_line: string;
  };
  mingshi: MingshiTable;
  elements: Record<string, number>;
  overall: { title: string; body: string };
  months: { month: number; title: string; body: string }[];
  domains: { id: string; title: string; body: string }[];
  lucky: {
    lucky_number: number;
    unlucky_number: number;
    lucky_color: string;
    unlucky_color: string;
    body: string;
  };
};

export type ChartFacts = {
  primary_engine: string;
  day_master: string;
  agreement: boolean;
  warnings: string[];
  licenses: {
    engine_id: string;
    license: string;
    package: string;
    homepage?: string;
    commercial_use?: string;
    role?: string;
  }[];
  engines: {
    engine_id: string;
    license: string;
    package: string;
    ok: boolean;
    error?: string | null;
    signature?: string | null;
  }[];
  pillars?: {
    year: StemBranch;
    month: StemBranch;
    day: StemBranch;
    hour: StemBranch | null;
  };
};

export type FullReport = {
  day_master: string;
  elements: Record<string, number>;
  weak_elements: string[];
  strong_elements: string[];
  chart_facts?: ChartFacts | null;
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
  mingshi?: MingshiTable;
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
  tojeong?: TojeongReport;
  wealth_year?: WealthYearReport;
};

export type WealthGrade = {
  id: string;
  label: string;
  rank: number;
  color: string;
};

export type WealthDay = {
  day: number;
  date: string;
  weekday: string;
  weekday_index: number;
  score: number;
  score_label: string;
  shinsal: string[];
  body: string;
  body_long?: string | null;
  long_locked?: boolean;
};

export type WealthYearReport = {
  year: number;
  title: string;
  subtitle: string;
  header: {
    display_name: string;
    gender: string;
    gender_ko: string;
    age: number;
    age_text: string;
    solar_text: string;
    lunar_text: string;
    time_text: string;
    calendar_type: string;
    pillars_line: string;
    day_master: string;
    year_ganzhi: string;
  };
  mingshi: MingshiTable;
  elements: {
    counts: Record<string, number>;
    scaled: Record<string, number>;
    labels: Record<string, string>;
    day_master_element: string;
    day_master_element_ko: string;
    strength_ratio: string;
    strength: string;
    display_line: string;
  };
  daeun: {
    start_base_age: number;
    intro: string;
    periods: {
      index: number;
      start_age: number;
      end_age: number;
      age_label: string;
      stem: string;
      branch: string;
      stem_branch: string;
      stem_line: string;
      branch_line: string;
      note: string;
      is_current: boolean;
    }[];
  };
  overview: { title: string; body: string; locked?: boolean };
  year_money: { title: string; body: string; locked?: boolean };
  month_guide: {
    title: string;
    intro: string;
    grades_legend: WealthGrade[];
    months: {
      month: number;
      title: string;
      body: string;
      grade: string;
      grade_label: string;
      grade_rank: number;
      grade_color: string;
      ganzhi: string;
      locked?: boolean;
    }[];
  };
  calendar: {
    title: string;
    note: string;
    score_legend: { score: number; label: string }[];
    months: {
      month: number;
      year: number;
      title: string;
      ganzhi: string;
      grade_label: string;
      days: WealthDay[];
      locked?: boolean;
      preview?: boolean;
      preview_note?: string;
      lock_reason?: string;
    }[];
  };
  access?: {
    unlocked: boolean;
    tier: string;
    message: string;
    price_krw?: number;
    free_calendar_days?: number;
  };
  monetization: Record<string, unknown> & {
    enabled?: boolean;
    mode?: string;
    message?: string;
    unlocked?: boolean;
    price_krw?: number;
    packs?: {
      id: string;
      count: number;
      bonus_pct: number;
      bonus_count: number;
      total_beads: number;
      price_krw: number;
      label: string;
    }[];
    costs?: Record<string, number>;
    wealth_year?: { price_krw: number; label: string; covers: string };
  };
  export: {
    format: string;
    filename_hint: string;
    body: string;
    locked?: boolean;
    message?: string;
  };
  disclaimer: string;
};

export type WalletInfo = {
  beads: number;
  starter_beads: number;
  catalog: Record<string, unknown>;
  unlocks: Record<string, boolean>;
  costs: Record<string, number>;
  mock_payment: boolean;
  note: string;
};

export async function getWallet(): Promise<WalletInfo> {
  const res = await apiFetch("/api/shop/wallet");
  if (!res.ok) throw new Error(parseApiError(await res.text(), "지갑 조회 실패"));
  return res.json();
}

export async function buyBeadPack(pack_id: string) {
  const res = await apiFetch("/api/shop/buy/beads", {
    method: "POST",
    body: JSON.stringify({ pack_id }),
  });
  if (!res.ok) throw new Error(parseApiError(await res.text(), "구슬 구매 실패"));
  return res.json() as Promise<{ ok: boolean; beads: number; message: string; pack: unknown }>;
}

export async function buyWealthYear(year = 2026) {
  const res = await apiFetch("/api/shop/buy/wealth-year", {
    method: "POST",
    body: JSON.stringify({ year }),
  });
  if (!res.ok) throw new Error(parseApiError(await res.text(), "부자되기 해금 실패"));
  return res.json() as Promise<{ ok: boolean; message: string; beads: number }>;
}

export async function spendBeads(body: {
  action: "tarot_extra" | "ask" | "profile_deep";
  year?: number;
  profile_id?: number;
  force_paid?: boolean;
}) {
  const res = await apiFetch("/api/shop/spend", {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(parseApiError(await res.text(), "구슬 사용 실패"));
  return res.json() as Promise<{
    ok: boolean;
    charged: number;
    free?: boolean;
    beads: number;
    message: string;
  }>;
}

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
    display_name?: string;
    label?: string;
    birth_year?: number;
    birth_month?: number;
    birth_day?: number;
    time_slot?: string;
    calendar_type?: "solar" | "lunar";
    solar_date?: string;
    hour?: number;
    minute?: number;
    time_unknown?: boolean;
    gender: "male" | "female";
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
    beads_charged?: number;
    beads?: number | null;
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

// --- Store (benchmark catalog products) ---

export type StoreProduct = {
  id: string;
  title: string;
  price_krw: number;
  category_id: string;
  category_label: string;
  needs_profile?: boolean;
  needs_partner?: boolean;
  is_free?: boolean;
  preview_sections?: string[];
  result_sections?: string[];
  tone?: string;
  payment?: Record<string, unknown>;
  intro_blurbs?: string[];
};

export async function getStoreMenu() {
  return publicJson<{
    menu: { id: string; label: string; href: string }[];
    categories: { id: string; label: string }[];
    payment_module: Record<string, unknown>;
    engine_plan: Record<string, unknown>;
  }>("/api/store/menu");
}

export async function getStoreProducts(category?: string) {
  const q = category ? `?category=${encodeURIComponent(category)}` : "";
  return publicJson<{ count: number; products: StoreProduct[] }>(
    `/api/store/products${q}`
  );
}

export async function getStoreProduct(id: string) {
  const res = await apiFetch(`/api/store/products/${id}`);
  if (!res.ok) throw new Error(parseApiError(await res.text(), "상품 조회 실패"));
  return res.json() as Promise<{
    product: StoreProduct;
    unlocked: boolean;
    payment_module: Record<string, unknown>;
  }>;
}

export async function checkoutStoreProduct(body: {
  product_id: string;
  profile_id: number;
  partner_profile_id?: number;
  buyer_name?: string;
  email?: string;
  phone?: string;
  method?: string;
  agree_privacy: boolean;
  agree_age14: boolean;
}) {
  const res = await apiFetch("/api/store/checkout", {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(parseApiError(await res.text(), "결제 실패"));
  return res.json() as Promise<{
    ok: boolean;
    mock: boolean;
    message: string;
    result_path: string;
    price_krw: number;
  }>;
}

export async function getStoreProductResult(
  productId: string,
  profileId: number,
  partnerId?: number
) {
  const q = new URLSearchParams({ profile_id: String(profileId) });
  if (partnerId) q.set("partner_id", String(partnerId));
  const res = await apiFetch(`/api/store/products/${productId}/result?${q}`);
  if (!res.ok) throw new Error(parseApiError(await res.text(), "결과 조회 실패"));
  return res.json() as Promise<{
    unlocked: boolean;
    profile_id: number;
    report: {
      product: { id: string; title: string; price_krw?: number };
      header: Record<string, unknown>;
      intro: string;
      sections: { id: string; title: string; body: string }[];
      preview: string;
      disclaimer: string;
      engine_note: string;
      partner?: Record<string, unknown> | null;
      chart_facts?: ChartFacts | null;
    };
  }>;
}

export async function getFortuneEngines() {
  return publicJson<{
    policy: string;
    engines: {
      engine_id: string;
      license: string;
      package: string;
      homepage?: string;
      commercial_use?: boolean;
      role?: string;
      notes?: string;
    }[];
  }>("/api/fortune/engines");
}

export { API_URL };
