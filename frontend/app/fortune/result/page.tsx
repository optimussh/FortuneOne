"use client";

import { useEffect, useState } from "react";
import {
  FORTUNE_STORAGE_KEY,
  type SajuResponse,
} from "@/lib/api";
import { SajuResult, SajuResultEmpty } from "@/components/fortune/SajuResult";

export default function FortuneResultPage() {
  const [data, setData] = useState<SajuResponse | null | undefined>(undefined);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(FORTUNE_STORAGE_KEY);
      if (!raw) {
        setData(null);
        return;
      }
      setData(JSON.parse(raw) as SajuResponse);
    } catch {
      setData(null);
    }
  }, []);

  if (data === undefined) {
    return (
      <div className="flex items-center justify-center py-24 text-sm text-[var(--muted)]">
        불러오는 중…
      </div>
    );
  }

  if (!data) {
    return <SajuResultEmpty />;
  }

  return <SajuResult data={data} />;
}
