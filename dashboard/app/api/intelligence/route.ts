import { getDashboardData } from "@/lib/data";

export async function GET() {
  const data = await getDashboardData();
  return Response.json(data, {
    headers: {
      "Cache-Control": "public, max-age=60, s-maxage=900, stale-while-revalidate=3600",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
