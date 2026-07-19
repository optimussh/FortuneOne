const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  // Don't set Content-Type for FormData (file upload)
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
};

export const FORTUNE_STORAGE_KEY = "fortune:last";

export async function postFortuneSaju(body: SajuRequestBody): Promise<SajuResponse> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${base}/api/fortune/saju`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let message = "사주 계산에 실패했습니다";
    const text = await res.text();
    try {
      const data = JSON.parse(text) as { detail?: string | { msg?: string }[] };
      if (typeof data?.detail === "string") message = data.detail;
      else if (Array.isArray(data?.detail))
        message = data.detail.map((d) => d.msg).filter(Boolean).join(", ") || message;
      else if (text) message = text;
    } catch {
      if (text) message = text;
    }
    throw new Error(message);
  }
  return res.json();
}

export { API_URL };
