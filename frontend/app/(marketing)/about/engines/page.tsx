"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getFortuneEngines } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AboutEnginesPage() {
  const [policy, setPolicy] = useState("");
  const [engines, setEngines] = useState<
    {
      engine_id: string;
      license: string;
      package: string;
      homepage?: string;
      commercial_use?: boolean;
      role?: string;
      notes?: string;
    }[]
  >([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getFortuneEngines()
      .then((r) => {
        setPolicy(r.policy);
        setEngines(r.engines || []);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "실패"));
  }, []);

  return (
    <main className="mx-auto max-w-lg px-4 py-10 pb-20">
      <h1 className="text-center text-2xl font-extrabold">오픈소스 · 라이선스</h1>
      <p className="mt-2 text-center text-sm text-[var(--muted)]">
        상업화에 문제 없는 허용 라이선스(MIT 등) 엔진만 fact 계산에 사용합니다
      </p>

      {error && <p className="mt-4 text-center text-sm text-red-600">{error}</p>}

      <Card className="mt-6 border-[var(--border)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">정책</CardTitle>
        </CardHeader>
        <CardContent className="text-sm leading-7 text-[var(--muted)]">
          <p>{policy || "MIT/Apache/BSD · 상용 가능 엔진만 등록"}</p>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-xs">
            <li>Primary + 교차검증. 불일치 시 primary 유지 + 경고</li>
            <li>해석 문장은 FortuneOne 자체 템플릿 (상용 카피 미사용)</li>
            <li>GPL/AGPL·라이선스 불명·스크랩 본문 미사용</li>
          </ul>
        </CardContent>
      </Card>

      <div className="mt-4 space-y-3">
        {engines.map((e) => (
          <Card key={e.engine_id} className="border-[var(--border)]">
            <CardHeader className="pb-1">
              <CardTitle className="text-sm">
                {e.engine_id}{" "}
                <span className="text-xs font-normal text-[var(--primary)]">{e.license}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-xs text-[var(--muted)]">
              <p>package: {e.package}</p>
              <p>role: {e.role || "—"}</p>
              {e.notes && <p>{e.notes}</p>}
              {e.homepage && (
                <a
                  href={e.homepage}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[var(--primary)] underline"
                >
                  {e.homepage}
                </a>
              )}
              <p className="pt-1 text-[10px]">
                Commercial use: {e.commercial_use === false ? "No" : "Yes (per MIT terms)"}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="mt-6 text-center text-[10px] leading-relaxed text-[var(--muted)]">
        MIT 고지: 각 패키지의 원 저작권·LICENSE 문구를 존중합니다. 배포 시 About에 출처를 유지하세요.
      </p>

      <div className="mt-8 flex justify-center gap-3">
        <Button asChild variant="outline">
          <Link href="/store">스토어</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/">홈</Link>
        </Button>
      </div>
    </main>
  );
}
