"use client";

import {
  DAYS,
  MONTHS,
  RELATION_OPTIONS,
  SAJU_HOURS,
  YEARS,
  type SajuFormValue,
} from "@/lib/saju-form";

const selectStyle: React.CSSProperties = {
  width: "100%",
  padding: "11px 12px",
  borderRadius: 10,
  border: "1px solid var(--border)",
  fontSize: 14,
  background: "#fff",
};

const labelStyle: React.CSSProperties = {
  fontSize: 12,
  fontWeight: 600,
  color: "var(--muted)",
  display: "block",
  marginBottom: 6,
};

type Props = {
  value: SajuFormValue;
  onChange: (v: SajuFormValue) => void;
  showRelation?: boolean;
  compact?: boolean;
};

export function SajuDetailForm({ value, onChange, showRelation = true, compact }: Props) {
  const set = <K extends keyof SajuFormValue>(key: K, val: SajuFormValue[K]) =>
    onChange({ ...value, [key]: val });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: compact ? 10 : 14 }}>
      {showRelation && (
        <div>
          <label style={labelStyle}>관계</label>
          <select
            style={selectStyle}
            value={value.label}
            onChange={(e) => set("label", e.target.value)}
          >
            {RELATION_OPTIONS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
      )}

      <div>
        <label style={labelStyle}>이름</label>
        <input
          style={{ ...selectStyle }}
          placeholder="이름을 입력하세요"
          value={value.display_name}
          onChange={(e) => set("display_name", e.target.value)}
        />
      </div>

      <div>
        <label style={labelStyle}>성별</label>
        <div style={{ display: "flex", gap: 8 }}>
          {(
            [
              ["male", "남자"],
              ["female", "여자"],
            ] as const
          ).map(([k, lab]) => (
            <button
              key={k}
              type="button"
              onClick={() => set("gender", k)}
              style={{
                flex: 1,
                padding: "11px 8px",
                borderRadius: 10,
                border:
                  value.gender === k ? "2px solid var(--primary)" : "1px solid var(--border)",
                background: value.gender === k ? "var(--primary-light)" : "#fff",
                fontWeight: 600,
                fontSize: 14,
                cursor: "pointer",
              }}
            >
              {lab}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label style={labelStyle}>생년월일</label>
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 1fr", gap: 8 }}>
          <select
            style={selectStyle}
            value={value.birth_year}
            onChange={(e) => set("birth_year", Number(e.target.value))}
          >
            {YEARS.map((y) => (
              <option key={y} value={y}>
                {y}년
              </option>
            ))}
          </select>
          <select
            style={selectStyle}
            value={value.birth_month}
            onChange={(e) => set("birth_month", Number(e.target.value))}
          >
            {MONTHS.map((m) => (
              <option key={m} value={m}>
                {String(m).padStart(2, "0")}월
              </option>
            ))}
          </select>
          <select
            style={selectStyle}
            value={value.birth_day}
            onChange={(e) => set("birth_day", Number(e.target.value))}
          >
            {DAYS.map((d) => (
              <option key={d} value={d}>
                {String(d).padStart(2, "0")}일
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label style={labelStyle}>태어난 시간 · 12시진 (KST)</label>
        <select
          style={selectStyle}
          value={value.time_slot}
          onChange={(e) => set("time_slot", e.target.value)}
        >
          {SAJU_HOURS.map((h) => (
            <option key={h.key} value={h.key}>
              {h.label}
            </option>
          ))}
        </select>
        <p style={{ marginTop: 6, fontSize: 11, color: "var(--muted)", lineHeight: 1.5 }}>
          자시 23:30 시작 표(일반 통용). 한국 표준시(동경 135°) 기준이며, 지역 진태양시 보정은
          포함하지 않습니다.
        </p>
      </div>

      <div>
        <label style={labelStyle}>달력</label>
        <div style={{ display: "flex", gap: 8 }}>
          {(
            [
              ["solar", "양력"],
              ["lunar", "음력"],
            ] as const
          ).map(([k, lab]) => (
            <button
              key={k}
              type="button"
              onClick={() => set("calendar_type", k)}
              style={{
                flex: 1,
                padding: "11px 8px",
                borderRadius: 10,
                border:
                  value.calendar_type === k
                    ? "2px solid var(--primary)"
                    : "1px solid var(--border)",
                background: value.calendar_type === k ? "var(--primary-light)" : "#fff",
                fontWeight: 600,
                fontSize: 14,
                cursor: "pointer",
              }}
            >
              {lab}
            </button>
          ))}
        </div>
        {value.calendar_type === "lunar" && (
          <p style={{ marginTop: 6, fontSize: 11, color: "var(--muted)" }}>
            음력 입력은 저장되며, 계산 엔진은 입력일을 기준으로 사용합니다 (로컬 MVP).
          </p>
        )}
      </div>
    </div>
  );
}
