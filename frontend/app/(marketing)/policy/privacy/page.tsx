import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "개인정보 처리방침 - 노우브릿지",
  description: "노우브릿지 개인정보 처리방침",
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
      <p style={{ color: "var(--muted)", marginBottom: 40 }}>시행일: [시행일 입력]</p>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제1조 (개인정보의 처리목적)</h2>
        <p>
          <strong>[회사명]</strong>(이하 &quot;회사&quot;)은(는) 다음의 목적을 위하여 개인정보를 처리합니다. 처리하고 있는 개인정보는 다음의 목적 이외의 용도로는 이용되지 않으며, 이용 목적이 변경되는 경우에는 별도의 동의를 받는 등 필요한 조치를 이행할 예정입니다.
        </p>
        <ol style={{ paddingLeft: 20, marginTop: 8 }}>
          <li><strong>회원 가입 및 관리:</strong> 회원 가입 의사 확인, 회원제 서비스 제공에 따른 본인 식별·인증, 회원자격 유지·관리, 서비스 부정이용 방지, 각종 고지·통지 등</li>
          <li><strong>서비스 제공:</strong> 콘텐츠 제공, 맞춤 서비스 제공, 본인인증 등</li>
          <li><strong>결제 처리:</strong> 유료 콘텐츠 결제 처리, 환불 처리 등</li>
          <li><strong>마케팅 및 광고 활용:</strong> 신규 서비스 개발 및 맞춤 서비스 제공, 이벤트 및 광고성 정보 제공, 서비스 이용 통계 등</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제2조 (처리하는 개인정보의 항목)</h2>
        <p>회사는 다음의 개인정보 항목을 처리하고 있습니다.</p>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 12 }}>
          <thead>
            <tr style={{ background: "var(--secondary)" }}>
              <th style={{ padding: "10px 12px", border: "1px solid var(--border)", textAlign: "left", fontSize: 13 }}>구분</th>
              <th style={{ padding: "10px 12px", border: "1px solid var(--border)", textAlign: "left", fontSize: 13 }}>수집 항목</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>필수항목</td>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>이메일 주소, 비밀번호(암호화)</td>
            </tr>
            <tr>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>소셜 로그인</td>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>소셜 계정 식별자, 이메일 주소, 프로필 이미지(선택)</td>
            </tr>
            <tr>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>결제 시</td>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>결제 수단 정보, 결제 기록 (카드 번호 등은 PG사에서 관리)</td>
            </tr>
            <tr>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>자동 수집</td>
              <td style={{ padding: "10px 12px", border: "1px solid var(--border)", fontSize: 13 }}>IP주소, 쿠키, 서비스 이용 기록, 접속 로그, 기기 정보</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제3조 (개인정보의 보유 및 이용기간)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회사는 법령에 따른 개인정보 보유·이용기간 또는 정보주체로부터 개인정보를 수집 시에 동의받은 개인정보 보유·이용기간 내에서 개인정보를 처리·보유합니다.</li>
          <li>각각의 개인정보 처리 및 보유 기간은 다음과 같습니다.
            <ul style={{ paddingLeft: 20, marginTop: 4 }}>
              <li><strong>회원 가입 정보:</strong> 회원 탈퇴 시까지 (단, 관련 법령에 의거 일정기간 보존)</li>
              <li><strong>결제 기록:</strong> 전자상거래 등에서의 소비자보호에 관한 법률에 따라 5년</li>
              <li><strong>접속 기록:</strong> 통신비밀보호법에 따라 3개월</li>
            </ul>
          </li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제4조 (개인정보의 제3자 제공)</h2>
        <p>
          회사는 원칙적으로 정보주체의 개인정보를 제1조에서 명시한 범위 내에서 처리하며, 정보주체의 사전 동의 없이는 본래의 범위를 초과하여 처리하거나 제3자에게 제공하지 않습니다. 다만, 다음의 경우에는 예외적으로 제공할 수 있습니다.
        </p>
        <ol style={{ paddingLeft: 20, marginTop: 8 }}>
          <li>정보주체가 사전에 동의한 경우</li>
          <li>법률에 특별한 규정이 있거나 법령상 의무를 준수하기 위하여 불가피한 경우</li>
          <li>정보주체 또는 법정대리인이 의사표시를 할 수 없는 상태에 있거나 주소불명 등으로 사전 동의를 받을 수 없는 경우로서 명백히 정보주체 또는 제3자의 급박한 생명, 신체, 재산의 이익을 위하여 필요하다고 인정되는 경우</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제5조 (개인정보의 파기)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회사는 개인정보 보유기간의 경과, 처리목적 달성 등 개인정보가 불필요하게 되었을 때에는 지체 없이 해당 개인정보를 파기합니다.</li>
          <li>전자적 파일 형태의 개인정보는 기록을 재생할 수 없는 기술적 방법을 사용하여 삭제합니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제6조 (정보주체의 권리·의무 및 행사방법)</h2>
        <p>정보주체는 회사에 대해 언제든지 다음 각 호의 개인정보 보호 관련 권리를 행사할 수 있습니다.</p>
        <ol style={{ paddingLeft: 20, marginTop: 8 }}>
          <li>개인정보 열람 요구</li>
          <li>오류 등이 있을 경우 정정 요구</li>
          <li>삭제 요구</li>
          <li>처리정지 요구</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제7조 (개인정보의 안전성 확보 조치)</h2>
        <p>회사는 개인정보의 안전성 확보를 위해 다음과 같은 조치를 취하고 있습니다.</p>
        <ol style={{ paddingLeft: 20, marginTop: 8 }}>
          <li>비밀번호의 암호화</li>
          <li>해킹 등에 대비한 기술적 대책</li>
          <li>개인정보에 대한 접근 제한</li>
          <li>개인정보를 처리하는 직원의 최소화 및 교육</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제8조 (쿠키의 사용)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회사는 이용자에게 개별적인 맞춤서비스를 제공하기 위해 이용 정보를 저장하고 수시로 불러오는 &quot;쿠키(cookie)&quot;를 사용합니다.</li>
          <li>이용자는 쿠키 설치에 대한 선택권을 가지고 있으며, 웹브라우저에서 옵션을 설정하여 모든 쿠키를 허용하거나 쿠키가 저장될 때마다 확인을 거치거나, 모든 쿠키의 저장을 거부할 수 있습니다.</li>
        </ol>
      </section>

      <div
        style={{
          marginTop: 48,
          padding: "24px",
          background: "var(--primary-light)",
          borderRadius: 12,
          fontSize: 13,
          color: "var(--muted)",
          lineHeight: 2,
        }}
      >
        <strong>제9조 (개인정보 보호책임자)</strong>
        <br />
        <br />
        성명: [개인정보 보호책임자 성명]
        <br />
        직책: [직책]
        <br />
        연락처: [전화번호]
        <br />
        이메일: [이메일 주소]
        <br />
        <br />
        <strong>회사 정보</strong>
        <br />
        상호: [회사명]
        <br />
        주소: [회사 주소]
        <br />
        사업자등록번호: [사업자등록번호]
        <br />
        <br />
        본 개인정보 처리방침은 [시행일 입력]부터 적용됩니다.
      </div>
    </div>
  );
}
