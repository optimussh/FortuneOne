"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { SajuForm } from "@/components/fortune/SajuForm";
import { useAuth } from "@/lib/auth-context";

const FEATURES = [
  {
    href: "/hub",
    title: "데일리 허브",
    desc: "출석 · 오늘 운세 · 일기 · 주제 운세",
  },
  {
    href: "/tarot",
    title: "타로 직접 뽑기",
    desc: "카드 펼침 후 직감으로 선택 · 이미지 공개",
  },
  {
    href: "/today",
    title: "띠별 오늘의 운세",
    desc: "12띠 일일 점수와 조언, 행운 컬러",
  },
  {
    href: "/ask",
    title: "질문형 운세",
    desc: "이직·연애·재물 등 골라 묻기",
  },
];

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) router.replace("/hub");
  }, [user, loading, router]);

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
          회원가입 없이 바로 확인하세요. 로그인하면 매일 허브·스트릭·일기로 다시 찾게 됩니다.
        </p>
        <p className="mt-3 text-xs text-[var(--muted)]">
          이미 회원이신가요?{" "}
          <Link href="/login" className="font-semibold text-[var(--primary)] underline">
            로그인 → 허브
          </Link>
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
