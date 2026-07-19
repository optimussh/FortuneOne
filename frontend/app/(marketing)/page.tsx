import { SajuForm } from "@/components/fortune/SajuForm";

export default function HomePage() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col items-center gap-8 px-4 py-10 sm:py-16">
      <div className="max-w-xl text-center">
        <h1
          className="mb-3 text-4xl font-extrabold tracking-tight sm:text-5xl"
          style={{
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          FortuneOne
        </h1>
        <p className="text-base leading-relaxed text-[var(--muted)] sm:text-lg">
          생년월일을 입력하고 사주 원국과 오늘의 운세를 바로 확인해 보세요.
          <br className="hidden sm:block" />
          로그인 없이 게스트로 이용할 수 있습니다.
        </p>
      </div>
      <SajuForm />
    </div>
  );
}
