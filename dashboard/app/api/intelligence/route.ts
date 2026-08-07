import { getDashboardData } from "@/lib/data";

export async function GET() {
  const data = await getDashboardData();
  return Response.json(data, {
    headers: {
      "Cache-Control": "public, max-age=60, s-maxage=300, stale-while-revalidate=900",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
