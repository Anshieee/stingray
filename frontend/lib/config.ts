/** One place for the browser's local backend origin; the API contract remains OpenAPI. */
export const BACKEND_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://127.0.0.1:8000";
