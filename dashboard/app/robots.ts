import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/"],
    },
    sitemap:
      "https://cyberdailylog.jimblogic.chatgpt.site/sitemap.xml",
    host: "https://cyberdailylog.jimblogic.chatgpt.site",
  };
}
