import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Devanshu Verma — AI Persona | ML Engineer",
  description:
    "Chat with Devanshu's AI representative. Ask about his experience in LLM systems, RAG pipelines, and MLOps. Book a meeting directly.",
  keywords: ["AI Engineer", "LLM", "RAG", "Machine Learning", "Devanshu Verma", "IIIT Una"],
  openGraph: {
    title: "Devanshu Verma — AI Persona",
    description: "Powered by RAG. Grounded in real data. Book a meeting instantly.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
