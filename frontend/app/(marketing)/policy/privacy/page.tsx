import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "개인정보 처리방침 - FortuneOne",
  description: "FortuneOne 개인정보 처리방침",
};

export default function PrivacyPolicyPage() {
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

      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>개인정보 처리방침</h1>
      <p style={{ color: "var(--muted)", marginBottom: 40 }}>
        FortuneOne · 시행일: 2026-07-23 (템플릿 — 사업자 확정 시 연락처 교체)
      </p>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>1. 처리 목적</h2>
        <p>
          FortuneOne(이하 &quot;회사&quot;)은 다음 목적으로 개인정보를 처리합니다. 목적 외 이용 시 별도
          동의를 받습니다.
        </p>
        <ol style={{ paddingLeft: 20, marginTop: 8 }}>
          <li>
            <strong>회원 가입·관리:</strong> 본인 확인, 계정 유지, 공지, 부정 이용 방지
          </li>
          <li>
            <strong>서비스 제공:</strong> 사주 프로필 기반 운세·타로·궁합·스토어 결과 생성
          </li>
          <li>
            <strong>결제·정산:</strong> 유료 콘텐츠 결제, 환불, 주문 이력, 다시보기 기간 관리
          </li>
          <li>
            <strong>고객 지원:</strong> 문의 응대, 오류 대응
          </li>
          <li>
            <strong>(선택) 마케팅:</strong> 이벤트·혜택 안내 — 별도 동의 시에만
          </li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>2. 수집 항목</h2>
        <ul style={{ paddingLeft: 20 }}>
          <li>
            <strong>필수:</strong> 이메일, 비밀번호(해시 저장), 사주 입력 정보(생년월일, 시진, 성별,
            이름/관계 등 회원이 입력한 값)
          </li>
          <li>
            <strong>결제 시:</strong> 구매자명, 연락처, 이메일, 결제 승인 정보(PG 경유, 카드번호 등
            민감 정보는 PG가 처리)
          </li>
          <li>
            <strong>자동 수집:</strong> 접속 로그, 기기·브라우저 정보, 쿠키(로그인 유지 등)
          </li>
        </ul>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>3. 보유 기간</h2>
        <ul style={{ paddingLeft: 20 }}>
          <li>회원 탈퇴 시까지. 단, 관련 법령에 따른 보존 의무가 있으면 해당 기간 보관</li>
          <li>결제·전자상거래 기록: 관련 법령(전자상거래법 등)에 따른 기간</li>
          <li>
            유료 결과 다시보기: 웹 원칙 <strong>7일</strong>, 이메일 링크 원칙{" "}
            <strong>30일</strong> (정책에 따름)
          </li>
        </ul>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>4. 제3자 제공·처리 위탁</h2>
        <p>
          원칙적으로 외부 제공하지 않습니다. 다만 결제(PG), 호스팅, 이메일 발송 등 서비스 운영에
          필요한 범위에서 위탁할 수 있으며, 위탁 시 목적·업체를 고지합니다.
        </p>
        <ul style={{ paddingLeft: 20, marginTop: 8 }}>
          <li>결제대행(PG): [토스페이먼츠 등 — 계약 후 명시]</li>
          <li>인프라: [호스팅/클라우드 — 배포 후 명시]</li>
        </ul>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>5. 이용자 권리</h2>
        <p>
          회원은 개인정보 열람·정정·삭제·처리정지 등을 요청할 수 있습니다. 문의:{" "}
          <strong>[support@example.com]</strong>
        </p>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>6. 안전 조치</h2>
        <p>
          비밀번호 해시 저장, 전송 구간 HTTPS(배포 환경), 접근 권한 최소화 등 합리적 보호 조치를
          시행합니다.
        </p>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>7. 개인정보 보호책임자</h2>
        <p>
          성명: [성명] · 연락처: [전화/이메일]  
          <br />
          (사업자 확정 시 <Link href="/policy/business">사업자 정보</Link>와 동일하게 기재)
        </p>
      </section>

      <p style={{ marginTop: 40, fontSize: 12, color: "var(--muted)" }}>
        <Link href="/policy">이용약관</Link> · <Link href="/policy/refund">환불</Link> ·{" "}
        <Link href="/policy/business">사업자</Link>
      </p>
    </div>
  );
}
