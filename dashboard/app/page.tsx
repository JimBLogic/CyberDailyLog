import { Dashboard } from "./components/dashboard";
import { getDashboardData } from "@/lib/data";

export const dynamic = "force-dynamic";

export default async function Home() {
  const data = await getDashboardData();
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "CyberDailyLog",
    url: "https://cyberdailylog.jimblogic.chatgpt.site",
    description:
      "Panel diario de inteligencia Blue Team con vulnerabilidades priorizadas y fuentes verificables.",
    applicationCategory: "SecurityApplication",
    operatingSystem: "Web",
    inLanguage: ["es", "en"],
    dateModified: data.generatedAt,
    isBasedOn: data.repositoryUrl,
    author: {
      "@type": "Person",
      name: "JimBLogic",
      url: "https://github.com/JimBLogic",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData).replace(/</g, "\\u003c"),
        }}
      />
      <Dashboard initialData={data} />
    </>
  );
}
