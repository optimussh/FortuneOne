import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "서비스 이용약관 - FortuneOne",
  description: "FortuneOne 사주·운세 서비스 이용약관",
};

export default function PolicyPage() {
  return (
    <div
      style={{
        maxWidth: 800,
        margin: "0 auto",
        padding: "60px 24px 80px",
        lineHeight: 1.8,
        fontSize: 14,
        color: "var(--foreground)",
      }}
    >
      <div style={{ marginBottom: 40 }}>
        <Link href="/" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
          ← 홈으로 돌아가기
        </Link>
      </div>

      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>서비스 이용약관</h1>
      <p style={{ color: "var(--muted)", marginBottom: 40 }}>
        FortuneOne · 시행일: 2026-07-23 (템플릿 — 사업자 확정 시 상호·주소 등 교체)
      </p>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제1조 (목적)</h2>
        <p>
          본 약관은 <strong>FortuneOne</strong>(이하 &quot;회사&quot;)이 제공하는 사주·운세·타로·궁합 등
          온라인 콘텐츠 서비스(이하 &quot;서비스&quot;)의 이용조건, 회사와 회원 간 권리·의무 및 책임사항을
          규정함을 목적으로 합니다.
        </p>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제2조 (정의)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>&quot;서비스&quot;란 회사가 웹·앱 등으로 제공하는 사주 원국, 일운·연간 리포트, 토정형 풀이, 부자되기, 타로, 궁합, 스토어 상품 및 관련 부가 기능을 말합니다.</li>
          <li>&quot;회원&quot;이란 본 약관에 동의하고 가입하여 서비스를 이용하는 자를 말합니다.</li>
          <li>&quot;사주 프로필&quot;이란 회원이 등록한 생년월일·시진·성별 등 운세 계산 입력 정보를 말합니다.</li>
          <li>&quot;유료 콘텐츠&quot;란 스토어 상품, 부자되기 연간 해금, 구슬 충전 등 결제가 필요한 디지털 콘텐츠를 말합니다.</li>
          <li>&quot;구슬&quot;이란 서비스 내 일부 기능을 이용하기 위한 충전형 이용권을 말합니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제3조 (약관의 게시와 개정)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회사는 본 약관을 서비스 초기화면 또는 연결화면에 게시합니다.</li>
          <li>관련 법령을 위배하지 않는 범위에서 약관을 개정할 수 있으며, 개정 시 적용일자 및 사유를 명시하여 사전에 공지합니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제4조 (서비스의 내용)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>기본 제공: 오늘의 운세, 신년 가이드, 토정형 연간, 부자되기(미리보기 포함), 오행·인생풀이 등 (기능은 변경될 수 있음).</li>
          <li>유료: 스토어 주제 패키지, 연간 해금, 구슬 등.</li>
          <li>서비스는 <strong>엔터테인먼트 및 자기 성찰 목적</strong>의 참고 정보이며, 투자·법률·의료·혼인 등에 대한 전문 자문이 아닙니다.</li>
          <li>원국 계산에는 MIT 라이선스 오픈소스를 사용할 수 있으며, 해석 문장은 회사 자체 생성입니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제5조 (회원가입 및 계정)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회원은 정확한 정보를 제공해야 하며, 타인의 정보를 도용해서는 안 됩니다.</li>
          <li>만 14세 미만은 서비스 유료 이용이 제한될 수 있습니다.</li>
          <li>계정 관리 책임은 회원에게 있으며, 부정 사용이 의심되면 이용을 제한할 수 있습니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제6조 (유료 결제 및 다시보기)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>유료 콘텐츠 가격, 구성, 결제 수단은 상품 페이지 및 결제 화면에 표시됩니다.</li>
          <li>
            <strong>웹 다시보기:</strong> 결제(해금) 시점부터 원칙적으로{" "}
            <strong>7일</strong>간 로그인 후 동일 계정에서 결과를 다시 볼 수 있습니다.
          </li>
          <li>
            <strong>이메일 링크 다시보기:</strong> 제공되는 경우 결제 시점부터 원칙적으로{" "}
            <strong>30일</strong>간 링크를 통해 열람할 수 있습니다. (발송 기능은 단계적 제공)
          </li>
          <li>기간 만료 후 재열람이 필요하면 재결제(또는 회사가 정한 방식)가 필요할 수 있습니다.</li>
          <li>결제 대행(PG) 이용 시 해당 PG 약관이 추가로 적용될 수 있습니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제7조 (환불)</h2>
        <p>
          환불은 별도 <Link href="/policy/refund" style={{ color: "var(--primary)" }}>환불 정책</Link>에
          따릅니다. 디지털 콘텐츠 열람 이후에는 관련 법령이 허용하는 범위에서 청약철회가 제한될 수
          있습니다.
        </p>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제8조 (회원의 의무)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>서비스를 불법·부당한 목적(사기, 스팸, 권리 침해 등)으로 이용해서는 안 됩니다.</li>
          <li>자동화된 수단으로 과도하게 서버에 부하를 주는 행위를 금합니다.</li>
          <li>회사 콘텐츠를 무단 복제·재배포·재판매해서는 안 됩니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제9조 (책임의 제한)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>운세·사주 해석은 확정적 예언이 아니며, 회원 판단과 행동에 대한 책임은 회원에게 있습니다.</li>
          <li>천재지변, 통신 장애, PG 장애 등 회사 합리적 통제 밖의 사유로 인한 손해에 대해 법령이 허용하는 범위에서 책임을 제한합니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제10조 (준거법 및 분쟁)</h2>
        <p>
          본 약관은 대한민국 법령을 준거법으로 하며, 분쟁 시 회사 본점 소재지 관할 법원을 제1심
          관할로 할 수 있습니다. (확정 시 주소 반영)
        </p>
      </section>

      <p style={{ marginTop: 40, fontSize: 12, color: "var(--muted)" }}>
        관련:{" "}
        <Link href="/policy/privacy">개인정보</Link> ·{" "}
        <Link href="/policy/refund">환불</Link> ·{" "}
        <Link href="/policy/business">사업자 정보</Link> ·{" "}
        <Link href="/about/engines">오픈소스</Link>
      </p>
    </div>
  );
}
