import type { Metadata } from "next";
import { Instrument_Serif } from "next/font/google";
import "./globals.css";

const fontSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-serif",
});

export const metadata: Metadata = {
  title: "NomadNavigator AI — 나에게 맞는 도시를 찾아드립니다",
  description: "AI 기반 디지털 노마드 이민 설계 서비스",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={`${fontSerif.variable} antialiased`}>{children}</body>
    </html>
  );
}
