"use client";

import { AuthProvider } from "@/lib/auth-context";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <Header />
      <main style={{ minHeight: "calc(100vh - 64px)" }}>{children}</main>
      <Footer />
    </AuthProvider>
  );
}
