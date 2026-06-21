import type { ApiErrorResponse } from "./contracts";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId: string | null;
  readonly details: unknown;

  constructor({
    status,
    code,
    message,
    requestId,
    details,
  }: {
    status: number;
    code: string;
    message: string;
    requestId: string | null;
    details: unknown;
  }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.requestId = requestId;
    this.details = details;
  }
}

export function toApiError(status: number, payload: ApiErrorResponse | null): ApiError {
  return new ApiError({
    status,
    code: payload?.error_code ?? "API_REQUEST_FAILED",
    message: payload?.message ?? "The backend request failed.",
    requestId: payload?.request_id ?? null,
    details: payload?.details,
  });
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Something went wrong while loading backend data.";
}
