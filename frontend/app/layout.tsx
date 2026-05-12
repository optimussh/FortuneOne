import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "노우브릿지 - 지식의 다리를 잇다",
  description: "노우브릿지에서 실무 중심의 온라인 강의를 만나보세요. 누구나 강의를 만들고, 배울 수 있는 지식 공유 플랫폼입니다.",
  keywords: ["온라인 강의", "프로그래밍", "지식 공유", "노우브릿지", "개발 강의"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          as="style"
          crossOrigin="anonymous"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
        />
      </head>
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
