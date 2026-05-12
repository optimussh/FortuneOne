"use client";

import { AuthProvider } from "@/lib/auth-context";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <Header />
      <main style={{ minHeight: "calc(100vh - 64px)", background: "var(--background)" }}>
        {children}
      </main>
      <Footer />
    </AuthProvider>
  );
}
