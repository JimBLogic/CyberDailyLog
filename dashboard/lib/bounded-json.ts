export const MAX_SOURCE_JSON_BYTES = 8 * 1024 * 1024;

export class ResponseLimitError extends Error {
  constructor() { super("Source response exceeds byte limit"); }
}

/** Count streamed bytes even when Content-Length is absent or inaccurate. */
export async function readBoundedJson<T = unknown>(response: Response, maxBytes = MAX_SOURCE_JSON_BYTES): Promise<T> {
  if (!Number.isSafeInteger(maxBytes) || maxBytes <= 0) throw new RangeError("Invalid JSON byte limit");
  const declared = Number(response.headers.get("content-length"));
  if (Number.isFinite(declared) && declared > maxBytes) {
    await response.body?.cancel().catch(() => {});
    throw new ResponseLimitError();
  }
  if (!response.body) return JSON.parse("") as T;
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  // Small feeds reserve only 64 KiB; geometric growth stays bounded for large feeds.
  let buffer = new Uint8Array(Math.min(maxBytes, 64 * 1024));
  let received = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if (value.byteLength > maxBytes - received) throw new ResponseLimitError();
      const required = received + value.byteLength;
      if (required > buffer.byteLength) {
        const capacity = Math.min(maxBytes, Math.max(required, buffer.byteLength * 2));
        const expanded = new Uint8Array(capacity);
        expanded.set(buffer.subarray(0, received));
        buffer = expanded;
      }
      buffer.set(value, received);
      received += value.byteLength;
    }
  } catch (error) {
    await reader.cancel().catch(() => {});
    throw error;
  } finally {
    reader.releaseLock();
  }
  return JSON.parse(decoder.decode(buffer.subarray(0, received))) as T;
}
