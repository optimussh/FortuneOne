"use client";

import Link from "next/link";
import { SajuForm } from "@/components/fortune/SajuForm";

const FEATURES = [
  {
    href: "/",
    title: "정통 사주 원국",
    desc: "생년월일시 기반 사주팔자 · 오행 · 용신 · 대운",
  },
  {
    href: "/today",
    title: "띠별 오늘의 운세",
    desc: "12띠 일일 점수와 조언, 행운 컬러",
  },
  {
    href: "/tarot",
    title: "타로 스프레드",
    desc: "1·3·5장 스프레드, 정·역방향 해석",
  },
  {
    href: "/compatibility",
    title: "궁합 분석",
    desc: "두 사람의 일간·오행 보완 스코어",
  },
];

export default function HomePage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-4 pb-16 pt-8 sm:pt-12">
      <section className="mb-10 text-center">
        <p className="mb-2 text-sm font-semibold tracking-wide text-[var(--primary)]">
          FortuneOne
        </p>
        <h1 className="text-3xl font-extrabold leading-tight sm:text-4xl">
          나의 사주와
          <br />
          오늘의 운세
        </h1>
        <p className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-[var(--muted)] sm:text-base">
          회원가입 없이 바로 확인하세요. 로그인하면 사주를 저장하고 언제든 다시 볼 수
          있습니다.
        </p>
      </section>

      <section className="mb-10 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {FEATURES.map((f) => (
          <Link
            key={f.title}
            href={f.href}
            className="rounded-2xl border border-[var(--border)] bg-[var(--card-bg)] p-4 text-left transition hover:border-[var(--primary)] hover:shadow-md"
          >
            <div className="text-sm font-bold">{f.title}</div>
            <div className="mt-1 text-xs leading-snug text-[var(--muted)]">{f.desc}</div>
          </Link>
        ))}
      </section>

      <section className="rounded-2xl border border-[var(--border)] bg-[var(--card-bg)] p-4 shadow-sm sm:p-6">
        <h2 className="mb-1 text-center text-lg font-bold">사주 무료 보기</h2>
        <p className="mb-6 text-center text-xs text-[var(--muted)]">
          양력 기준 · 시간 모르면 「시간 모름」 체크
        </p>
        <SajuForm />
      </section>
    </main>
  );
}
