import type { Metadata } from "next";
import { DM_Sans, Fraunces } from "next/font/google";
import { AuthProvider } from "@/lib/auth";
import { AppHeader } from "@/components/AppHeader";
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  weight: ["400", "500", "600", "700"],
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
});

export const metadata: Metadata = {
  title: "Maoni Yangu — sahanno leh goobta",
  description:
    "Samee sahanno, ururi jawaabo, oo qor meesha jawaabaha ka yimaadeen.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="so">
      <body
        className={`${dmSans.variable} ${fraunces.variable} antialiased`}
        style={
          {
            "--font-body": "var(--font-dm-sans), system-ui, sans-serif",
            "--font-display": "var(--font-fraunces), Georgia, serif",
          } as React.CSSProperties
        }
      >
        <AuthProvider>
          <AppHeader />
          <main style={{ maxWidth: 960, margin: "0 auto", padding: "1.5rem" }}>
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
