"use client";

import type { ChartFacts } from "@/lib/api";

/** Shows multi-engine commercial-safe verification status. */
export function ChartFactsBadge({ facts }: { facts?: ChartFacts | null }) {
  if (!facts) return null;
  const okCount = (facts.engines || []).filter((e) => e.ok).length;
  const primary = facts.primary_engine || "sajupy";
  const agreed = Boolean(facts.agreement);

  return (
    <div
      className={`rounded-xl border px-3 py-2 text-left text-[11px] leading-relaxed ${
        agreed
          ? "border-emerald-300 bg-emerald-50 text-emerald-900"
          : "border-amber-300 bg-amber-50 text-amber-950"
      }`}
    >
      <div className="flex flex-wrap items-center gap-2 font-semibold">
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] text-white ${
            agreed ? "bg-emerald-600" : "bg-amber-600"
          }`}
        >
          {agreed ? "엔진 교차검증 OK" : "교차검증 주의"}
        </span>
        <span>
          primary {primary} · 가동 {okCount}개 · MIT 상용 가능 엔진
        </span>
      </div>
      <ul className="mt-1.5 space-y-0.5 text-[10px] opacity-90">
        {(facts.licenses || []).map((l) => (
          <li key={l.engine_id}>
            {l.engine_id} ({l.license}
            {l.role ? ` · ${l.role}` : ""})
          </li>
        ))}
      </ul>
      {!agreed && facts.warnings?.length ? (
        <p className="mt-1 text-[10px] opacity-80">{facts.warnings[0]}</p>
      ) : null}
    </div>
  );
}
