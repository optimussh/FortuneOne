import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "서비스 이용약관 - 노우브릿지",
  description: "노우브릿지 서비스 이용약관",
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
      <p style={{ color: "var(--muted)", marginBottom: 40 }}>시행일: [시행일 입력]</p>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제1조 (목적)</h2>
        <p>
          본 약관은 <strong>[회사명]</strong>(이하 &quot;회사&quot;)이 운영하는 온라인 교육 플랫폼 <strong>&quot;노우브릿지&quot;</strong>(이하 &quot;서비스&quot;)의 이용조건 및 절차, 회사와 회원 간의 권리·의무 및 책임사항, 기타 필요한 사항을 규정함을 목적으로 합니다.
        </p>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제2조 (정의)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>&quot;서비스&quot;란 회사가 제공하는 온라인 강의 및 지식 공유 플랫폼을 말합니다.</li>
          <li>&quot;회원&quot;이란 서비스에 가입하여 이용계약을 체결한 자를 말합니다.</li>
          <li>&quot;강사&quot;란 서비스를 통해 강의 콘텐츠를 등록하고 제공하는 회원을 말합니다.</li>
          <li>&quot;수강생&quot;이란 서비스를 통해 강의를 수강하는 회원을 말합니다.</li>
          <li>&quot;콘텐츠&quot;란 강의 영상, 교안, 자료 등 강사가 서비스에 등록하는 모든 학습 자료를 말합니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제3조 (약관의 효력 및 변경)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>본 약관은 서비스 화면에 게시하거나 기타의 방법으로 회원에게 공지함으로써 효력이 발생합니다.</li>
          <li>회사는 합리적인 사유가 발생할 경우 관련 법령에 위배되지 않는 범위 안에서 본 약관을 변경할 수 있으며, 약관이 변경된 경우에는 지체 없이 이를 공지합니다.</li>
          <li>회원이 변경된 약관에 동의하지 않는 경우 서비스 이용을 중단하고 탈퇴할 수 있습니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제4조 (이용계약의 체결)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>이용계약은 회원이 되고자 하는 자가 약관의 내용에 동의한 후 회원가입 신청을 하고, 회사가 이를 승낙함으로써 체결됩니다.</li>
          <li>회사는 다음 각 호에 해당하는 신청에 대해서는 승낙을 하지 않거나 사후에 이용계약을 해지할 수 있습니다.
            <ul style={{ paddingLeft: 20, marginTop: 4 }}>
              <li>실명이 아니거나 타인의 정보를 이용한 경우</li>
              <li>허위의 정보를 기재하거나, 회사가 제시하는 내용을 기재하지 않은 경우</li>
              <li>기타 회원으로 등록하는 것이 서비스 운영에 현저히 지장이 있다고 판단되는 경우</li>
            </ul>
          </li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제5조 (서비스의 제공)</h2>
        <p>회사는 회원에게 다음과 같은 서비스를 제공합니다.</p>
        <ol style={{ paddingLeft: 20 }}>
          <li>온라인 강의 열람 및 수강 서비스</li>
          <li>강의 제작 및 등록 서비스 (강사)</li>
          <li>수강 후기 및 평가 서비스</li>
          <li>기타 회사가 정하는 서비스</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제6조 (회원의 의무)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회원은 서비스 이용 시 관련 법령, 본 약관의 규정, 이용안내 및 서비스와 관련하여 공지한 주의사항을 준수하여야 합니다.</li>
          <li>회원은 다음 각 호의 행위를 하여서는 안 됩니다.
            <ul style={{ paddingLeft: 20, marginTop: 4 }}>
              <li>타인의 정보를 도용하는 행위</li>
              <li>서비스에서 얻은 정보를 무단으로 복제, 배포, 방송하는 행위</li>
              <li>회사 또는 제3자의 저작권 등 지적재산권을 침해하는 행위</li>
              <li>서비스의 안정적 운영을 방해하는 행위</li>
            </ul>
          </li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제7조 (강사의 의무 및 책임)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>강사는 서비스에 등록하는 콘텐츠에 대한 저작권 및 관련 법적 권리를 보유하거나 적법한 권한을 가져야 합니다.</li>
          <li>강사는 타인의 저작권, 상표권, 초상권 등의 권리를 침해하는 콘텐츠를 등록하여서는 안 됩니다.</li>
          <li>콘텐츠에 관한 분쟁이 발생한 경우, 강사는 자신의 비용과 책임으로 이를 해결하여야 합니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제8조 (결제 및 환불)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>유료 강의의 결제는 회사가 제공하는 결제 수단을 통해 이루어집니다.</li>
          <li>환불은 콘텐츠를 이용하지 않은 경우 결제일로부터 7일 이내에 전액 환불이 가능합니다.</li>
          <li>콘텐츠의 일부를 이용한 경우, 이용한 부분에 해당하는 금액을 공제한 나머지 금액을 환불합니다.</li>
          <li>환불에 대한 세부 사항은 회사의 환불 정책을 따릅니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제9조 (면책조항)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회사는 천재지변, 전쟁, 기간통신사업자의 서비스 중지 등 불가항력으로 인하여 서비스를 제공할 수 없는 경우에는 책임을 지지 않습니다.</li>
          <li>회사는 회원의 귀책사유로 인한 서비스 이용의 장애에 대해서 책임을 지지 않습니다.</li>
          <li>회사는 강사가 등록한 콘텐츠의 정확성, 신뢰성 등에 대해서 보증하지 않습니다.</li>
        </ol>
      </section>

      <section style={{ marginBottom: 36 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>제10조 (분쟁해결)</h2>
        <ol style={{ paddingLeft: 20 }}>
          <li>회사와 회원 간에 발생한 분쟁에 관한 소송은 대한민국 법을 적용합니다.</li>
          <li>서비스 이용과 관련하여 회사와 회원 사이에 분쟁이 발생한 경우, 양 당사자는 분쟁의 해결을 위해 성실히 협의합니다.</li>
        </ol>
      </section>

      <div
        style={{
          marginTop: 48,
          padding: "20px 24px",
          background: "var(--primary-light)",
          borderRadius: 12,
          fontSize: 13,
          color: "var(--muted)",
        }}
      >
        <strong>부칙</strong>
        <br />
        본 약관은 [시행일 입력]부터 시행합니다.
        <br />
        <br />
        <strong>[회사명]</strong>
        <br />
        주소: [회사 주소 입력]
        <br />
        대표: [대표자명 입력]
        <br />
        사업자등록번호: [사업자등록번호 입력]
        <br />
        이메일: [이메일 주소 입력]
      </div>
    </div>
  );
}
