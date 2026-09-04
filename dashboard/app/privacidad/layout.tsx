import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacidad y almacenamiento local",
  description:
    "Información de privacidad de CyberDailyLog: preferencias locales, métricas automáticas de ChatGPT Sites y servicios de datos.",
  alternates: {
    canonical: "/privacidad",
  },
};

export default function PrivacyLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
