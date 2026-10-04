import { BACKEND_BASE_URL } from "./config";

export type TransformRequest = {
  source: { type: "text"; text: string };
  outputs: ["executive_summary"];
  controls: {
    target_audience: string | null;
    tone: string | null;
    language: string | null;
    detail_level: string | null;
    communication_objective: string | null;
    content_style: string | null;
  };
};

export type TransformResponse = {
  status: "ok";
  mode: "DETERMINISTIC_STUB";
  artifacts: [{ output_type: "executive_summary"; content: string }];
  warnings: string[];
};

export class ApiRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiRequestError";
  }
}

function isTransformResponse(value: unknown): value is TransformResponse {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<TransformResponse>;
  const artifact = candidate.artifacts?.[0];
  return (
    candidate.status === "ok" &&
    candidate.mode === "DETERMINISTIC_STUB" &&
    candidate.artifacts?.length === 1 &&
    artifact?.output_type === "executive_summary" &&
    typeof artifact.content === "string" &&
    artifact.content.startsWith("[DETERMINISTIC STUB]") &&
    Array.isArray(candidate.warnings) &&
    candidate.warnings.every((warning) => typeof warning === "string")
  );
}

function errorMessage(body: unknown): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = body.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return "The request was not valid.";
  }
  return "The backend rejected the request.";
}

/**
 * Minimal transport wrapper for this slice. FastAPI's generated OpenAPI remains
 * authoritative; this local type and runtime guard catch obvious contract drift.
 */
export async function requestTransform(request: TransformRequest): Promise<TransformResponse> {
  let response: Response;
  try {
    response = await fetch(`${BACKEND_BASE_URL}/api/v1/transform`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  } catch {
    throw new ApiRequestError(
      "Could not connect to the local backend. Start FastAPI on port 8000 and try again.",
    );
  }

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    throw new ApiRequestError(errorMessage(body));
  }
  if (!isTransformResponse(body)) {
    throw new ApiRequestError("The backend returned an unexpected transform response.");
  }
  return body;
}
