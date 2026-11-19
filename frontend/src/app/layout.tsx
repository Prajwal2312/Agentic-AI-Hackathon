import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRIVESCAN AI — Agentic Data Privacy Discovery & DPDP Compliance Auditor",
  description: "Autonomous multi-agent system discovering personal data, contextual nuance, risk evaluation, and DPDP Act 2023 compliance auditing.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full">
      <head>
        <link rel="stylesheet" href="/styles.css" />
      </head>
      <body className="min-h-full bg-[#080C16] text-slate-100 antialiased selection:bg-blue-500/30 selection:text-blue-200">
        {children}
      </body>
    </html>
  );
}
