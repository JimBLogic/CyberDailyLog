import type { Metadata } from "next";
import "@fontsource/archivo-black/400.css";
import "@fontsource-variable/inter";
import "@fontsource-variable/source-serif-4";
import "./globals.css";

export const metadata: Metadata = {
  title: "CyberDailyLog — Daily Blue Team Intelligence",
  description:
    "A transparent, source-backed Blue Team intelligence dashboard powered by the CyberDailyLog repository.",
  other: {
    "theme-color": "#f3f0e8",
    "color-scheme": "light",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: "CyberDailyLog — Daily Blue Team Intelligence",
    description:
      "Prioritized vulnerabilities, collector health and analyst context from a reproducible open-source pipeline.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
