import type { Metadata } from "next";
import "@fontsource/archivo-black/400.css";
import "@fontsource-variable/inter";
import "@fontsource-variable/source-serif-4";
import "./globals.css";

const siteUrl = "https://cyberdailylog.jimblogic.chatgpt.site";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "CyberDailyLog — Inteligencia Blue Team diaria",
    template: "%s | CyberDailyLog",
  },
  description:
    "Panel diario de inteligencia Blue Team con vulnerabilidades priorizadas, CISA KEV, EPSS, salud de fuentes y contexto verificable para saber qué revisar primero.",
  applicationName: "CyberDailyLog",
  authors: [{ name: "JimBLogic", url: "https://github.com/JimBLogic" }],
  creator: "JimBLogic",
  publisher: "JimBLogic",
  keywords: [
    "inteligencia de amenazas",
    "Blue Team",
    "ciberseguridad",
    "vulnerabilidades",
    "CISA KEV",
    "EPSS",
    "SOC",
    "threat intelligence",
  ],
  alternates: {
    canonical: "/",
    languages: {
      "es-ES": "/",
      "x-default": "/",
    },
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
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
      "Vulnerabilidades priorizadas, CISA KEV, EPSS, salud de fuentes y contexto verificable desde un sistema abierto y reproducible.",
    url: siteUrl,
    siteName: "CyberDailyLog",
    locale: "es_ES",
    alternateLocale: ["en_GB"],
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "CyberDailyLog — Inteligencia Blue Team diaria",
    description:
      "Prioridades defensivas diarias respaldadas por fuentes y una metodología reproducible.",
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
