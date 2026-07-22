import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "사업자 정보 - FortuneOne",
  description: "전자상거래 사업자 고지 템플릿",
};

/** Replace [brackets] with real business registration info before go-live. */
export default function BusinessInfoPage() {
  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "60px 24px 80px", lineHeight: 1.8, fontSize: 14 }}>
      <Link href="/" style={{ fontSize: 13, color: "var(--muted)", textDecoration: "none" }}>
        ← 홈
      </Link>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginTop: 24 }}>사업자 정보</h1>
      <p style={{ color: "var(--muted)" }}>
        전자상거래 등에서의 소비자보호에 관한 법률에 따른 사업자 고지 (템플릿)
      </p>

      <table style={{ width: "100%", marginTop: 32, borderCollapse: "collapse", fontSize: 14 }}>
        <tbody>
          {[
            ["상호", "[상호 / FortuneOne]"],
            ["대표자", "[대표자명]"],
            ["사업자등록번호", "[000-00-00000]"],
            ["통신판매업 신고번호", "[제OOOO-OOOO-OOOO호]"],
            ["사업장 소재지", "[주소]"],
            ["고객센터", "[전화] / [이메일]"],
            ["호스팅", "[호스팅 제공자]"],
            ["개인정보보호 책임자", "[성명 / 연락처]"],
          ].map(([k, v]) => (
            <tr key={k} style={{ borderBottom: "1px solid var(--border)" }}>
              <th
                style={{
                  textAlign: "left",
                  padding: "12px 8px",
                  width: 160,
                  color: "var(--muted)",
                  fontWeight: 600,
                }}
              >
                {k}
              </th>
              <td style={{ padding: "12px 8px" }}>{v}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p style={{ marginTop: 24, fontSize: 12, color: "var(--muted)" }}>
        백엔드 환경변수 <code>BUSINESS_*</code> 와 동일 내용으로 맞추면 API{" "}
        <code>/api/payments/config</code> 에도 반영됩니다. 배포 전 반드시 실정보로 교체하세요.
      </p>

      <p style={{ marginTop: 16 }}>
        <Link href="/policy" style={{ color: "var(--primary)" }}>
          이용약관
        </Link>
        {" · "}
        <Link href="/policy/privacy" style={{ color: "var(--primary)" }}>
          개인정보
        </Link>
        {" · "}
        <Link href="/policy/refund" style={{ color: "var(--primary)" }}>
          환불
        </Link>
      </p>
    </div>
  );
}
