import { getDashboardData } from "@/lib/data";

export async function GET() {
  const data = await getDashboardData();
  return Response.json(data, {
    headers: {
      // The collector already shares a 15-minute cache. Do not stack a second
      // cache that can conceal updates and return an expired refresh time.
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
