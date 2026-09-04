import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: "https://cyberdailylog.jimblogic.chatgpt.site",
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: "https://cyberdailylog.jimblogic.chatgpt.site/privacidad",
      changeFrequency: "yearly",
      priority: 0.4,
    },
  ];
}
