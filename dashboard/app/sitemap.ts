import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: "https://cyberdailylog.jimblogic.chatgpt.site",
      changeFrequency: "daily",
      priority: 1,
    },
  ];
}
