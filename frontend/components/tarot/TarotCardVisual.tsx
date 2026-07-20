"use client";

import { CSSProperties } from "react";

export type TarotVisualCard = {
  id?: string;
  name?: string;
  image_key?: string;
  color?: string;
  symbol?: string;
  reversed?: boolean;
  arcana?: string;
};

/** Ornate card back — face-down state */
export function TarotCardBack({
  selected,
  order,
  onClick,
  style,
  className = "",
}: {
  selected?: boolean;
  order?: number;
  onClick?: () => void;
  style?: CSSProperties;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`relative shrink-0 transition-transform duration-200 ${className}`}
      style={{
        width: 72,
        height: 112,
        borderRadius: 10,
        border: selected ? "2px solid #fbbf24" : "1px solid rgba(255,255,255,0.25)",
        boxShadow: selected
          ? "0 8px 24px rgba(251,191,36,0.45)"
          : "0 6px 16px rgba(0,0,0,0.35)",
        transform: selected ? "translateY(-10px) scale(1.05)" : undefined,
        cursor: onClick ? "pointer" : "default",
        padding: 0,
        overflow: "hidden",
        ...style,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          background: "linear-gradient(145deg, #1e1b4b 0%, #4c1d95 45%, #0f172a 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "78%",
            height: "82%",
            border: "1.5px solid rgba(251,191,36,0.55)",
            borderRadius: 6,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background:
              "repeating-linear-gradient(45deg, transparent, transparent 4px, rgba(255,255,255,0.04) 4px, rgba(255,255,255,0.04) 8px)",
          }}
        >
          <span style={{ fontSize: 22, color: "#fbbf24", opacity: 0.9 }}>✦</span>
        </div>
      </div>
      {selected && order != null && (
        <span
          style={{
            position: "absolute",
            top: -8,
            right: -8,
            width: 22,
            height: 22,
            borderRadius: "50%",
            background: "#fbbf24",
            color: "#1e1b4b",
            fontSize: 12,
            fontWeight: 800,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {order}
        </span>
      )}
    </button>
  );
}

/** Face-up card with unique color/symbol art (SVG-like CSS) */
export function TarotCardFace({
  card,
  size = "md",
  flipping,
}: {
  card: TarotVisualCard;
  size?: "sm" | "md" | "lg";
  flipping?: boolean;
}) {
  const dims = size === "lg" ? { w: 140, h: 220 } : size === "sm" ? { w: 80, h: 124 } : { w: 110, h: 170 };
  const color = card.color || "#6366f1";
  const symbol = card.symbol || "✦";
  const name = card.name || "?";
  const rev = !!card.reversed;

  return (
    <div
      style={{
        width: dims.w,
        height: dims.h,
        perspective: 900,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: 12,
          overflow: "hidden",
          border: "2px solid rgba(255,255,255,0.35)",
          boxShadow: "0 12px 28px rgba(0,0,0,0.35)",
          background: `linear-gradient(165deg, ${color} 0%, #0f172a 75%)`,
          transform: rev ? "rotate(180deg)" : undefined,
          transition: flipping ? "transform 0.5s" : undefined,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "space-between",
          padding: 10,
          position: "relative",
        }}
      >
        <div
          style={{
            width: "100%",
            textAlign: "left",
            fontSize: size === "sm" ? 9 : 11,
            fontWeight: 700,
            color: "rgba(255,255,255,0.9)",
            letterSpacing: 0.3,
          }}
        >
          {name}
        </div>
        <div
          style={{
            width: "70%",
            flex: 1,
            margin: "8px 0",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.25)",
            background: "rgba(255,255,255,0.08)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: size === "lg" ? 48 : size === "sm" ? 28 : 40,
            color: "rgba(255,255,255,0.95)",
            textShadow: "0 2px 12px rgba(0,0,0,0.4)",
          }}
        >
          {symbol}
        </div>
        <div
          style={{
            width: "100%",
            textAlign: "right",
            fontSize: 10,
            color: "rgba(255,255,255,0.7)",
            transform: rev ? "rotate(180deg)" : undefined,
          }}
        >
          {card.arcana === "major" ? "MAJOR" : "MINOR"}
          {rev ? " · R" : ""}
        </div>
        {/* corner ornaments */}
        <span style={{ position: "absolute", top: 6, right: 8, opacity: 0.4, fontSize: 10 }}>◇</span>
        <span style={{ position: "absolute", bottom: 6, left: 8, opacity: 0.4, fontSize: 10 }}>◇</span>
      </div>
    </div>
  );
}
