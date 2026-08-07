import type { Metadata } from "next";
import "@fontsource/archivo-black/400.css";
import "@fontsource-variable/inter";
import "@fontsource-variable/source-serif-4";
import "./globals.css";

export const metadata: Metadata = {
  title: "CyberDailyLog — Inteligencia Blue Team diaria",
  description:
    "Un panel Blue Team transparente y respaldado por fuentes para saber qué revisar primero.",
  other: {
    "theme-color": "#f3f0e8",
    "color-scheme": "light",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: "CyberDailyLog — Inteligencia Blue Team diaria",
    description:
      "Vulnerabilidades priorizadas, estado de fuentes y contexto de analistas desde un sistema abierto y reproducible.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
