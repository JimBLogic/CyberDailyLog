const ARTICLE_HOSTS = new Set([
  "isc.sans.edu",
  "www.sans.org",
  "sans.org",
  "krebsonsecurity.com",
  "www.krebsonsecurity.com",
  "github.com",
]);

const IMAGE_HOST_SUFFIXES = [
  "sans.edu",
  "sans.org",
  "krebsonsecurity.com",
  "github.com",
  "githubusercontent.com",
];

const MAX_IMAGE_BYTES = 3_000_000;
const MAX_REDIRECTS = 3;

function hostAllowed(hostname: string, suffixes: string[]) {
  return suffixes.some(
    (suffix) => hostname === suffix || hostname.endsWith(`.${suffix}`),
  );
}

function extractOpenGraphImage(html: string) {
  const patterns = [
    /<meta[^>]+property=["']og:image(?::secure_url)?["'][^>]+content=["']([^"']+)["'][^>]*>/i,
    /<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image(?::secure_url)?["'][^>]*>/i,
  ];
  for (const pattern of patterns) {
    const match = html.match(pattern);
    if (match?.[1]) return match[1].replaceAll("&amp;", "&");
  }
  return null;
}

async function fetchWithRedirectPolicy(
  initialUrl: URL,
  isAllowed: (url: URL) => boolean,
  headers: Record<string, string>,
) {
  let currentUrl = initialUrl;
  for (let redirectCount = 0; redirectCount <= MAX_REDIRECTS; redirectCount += 1) {
    if (currentUrl.protocol !== "https:" || !isAllowed(currentUrl)) {
      throw new Error("Blocked redirect destination");
    }
    const response = await fetch(currentUrl, {
      headers,
      redirect: "manual",
      signal: AbortSignal.timeout(5_000),
    });
    if (response.status < 300 || response.status >= 400) return response;

    const location = response.headers.get("location");
    if (!location || redirectCount === MAX_REDIRECTS) {
      throw new Error("Invalid redirect chain");
    }
    currentUrl = new URL(location, currentUrl);
  }
  throw new Error("Redirect limit exceeded");
}

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const rawUrl = requestUrl.searchParams.get("url");
  if (!rawUrl) return new Response(null, { status: 400 });

  let articleUrl: URL;
  try {
    articleUrl = new URL(rawUrl);
  } catch {
    return new Response(null, { status: 400 });
  }
  if (
    articleUrl.protocol !== "https:" ||
    !ARTICLE_HOSTS.has(articleUrl.hostname)
  ) {
    return new Response(null, { status: 403 });
  }

  try {
    const articleResponse = await fetchWithRedirectPolicy(
      articleUrl,
      (url) => ARTICLE_HOSTS.has(url.hostname),
      {
        Accept: "text/html,application/xhtml+xml",
        "User-Agent": "CyberDailyLogDashboard/1.0 (+https://github.com/JimBLogic/CyberDailyLog)",
      },
    );
    if (!articleResponse.ok) return new Response(null, { status: 404 });
    const contentType = articleResponse.headers.get("content-type") ?? "";
    if (!contentType.toLowerCase().includes("text/html")) {
      return new Response(null, { status: 415 });
    }
    const html = (await articleResponse.text()).slice(0, 700_000);
    const imageValue = extractOpenGraphImage(html);
    if (!imageValue) return new Response(null, { status: 404 });

    const imageUrl = new URL(imageValue, articleUrl);
    if (
      imageUrl.protocol !== "https:" ||
      !hostAllowed(imageUrl.hostname, IMAGE_HOST_SUFFIXES)
    ) {
      return new Response(null, { status: 403 });
    }
    const imageResponse = await fetchWithRedirectPolicy(
      imageUrl,
      (url) => hostAllowed(url.hostname, IMAGE_HOST_SUFFIXES),
      { Accept: "image/avif,image/webp,image/png,image/jpeg" },
    );
    if (!imageResponse.ok) return new Response(null, { status: 404 });
    const finalUrl = new URL(imageResponse.url);
    if (
      finalUrl.protocol !== "https:" ||
      !hostAllowed(finalUrl.hostname, IMAGE_HOST_SUFFIXES)
    ) {
      return new Response(null, { status: 403 });
    }
    const imageType = imageResponse.headers.get("content-type") ?? "";
    if (!imageType.toLowerCase().startsWith("image/")) {
      return new Response(null, { status: 415 });
    }
    const declaredLength = Number(
      imageResponse.headers.get("content-length") ?? 0,
    );
    if (declaredLength > MAX_IMAGE_BYTES) {
      return new Response(null, { status: 413 });
    }
    const bytes = await imageResponse.arrayBuffer();
    if (bytes.byteLength > MAX_IMAGE_BYTES) {
      return new Response(null, { status: 413 });
    }
    return new Response(bytes, {
      headers: {
        "Content-Type": imageType,
        "Cache-Control": "public, max-age=86400, s-maxage=604800",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch {
    return new Response(null, { status: 404 });
  }
}
