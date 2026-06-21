import "server-only";

import { cookies } from "next/headers";

import type {
  ApiAIInsight,
  ApiCategory,
  ApiForecast,
  ApiFulfillment,
  ApiInventory,
  ApiOrder,
  ApiProduct,
  ApiRole,
  ApiTokenPair,
  ApiUser,
  PaginatedResponse,
} from "./contracts";
import { toApiError } from "./errors";

const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

type QueryValue = string | number | boolean | null | undefined;

function getApiBaseUrl() {
  return process.env.OMNICORE_API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

function buildUrl(path: string, query?: Record<string, QueryValue>) {
  const url = new URL(`${getApiBaseUrl()}${path}`);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url;
}

async function getAuthToken() {
  const cookieStore = await cookies();
  return process.env.OMNICORE_API_TOKEN ?? cookieStore.get("omnicore_access_token")?.value;
}

async function request<T>(
  path: string,
  query?: Record<string, QueryValue>,
  init?: RequestInit,
): Promise<T> {
  const token = await getAuthToken();
  const response = await fetch(buildUrl(path, query), {
    ...init,
    headers: {
      Accept: "application/json",
      ...init?.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw toApiError(response.status, payload);
  }

  return response.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, undefined, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
}

export const api = {
  getProducts: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiProduct>>("/products", query),
  getProduct: (productId: string) => request<ApiProduct>(`/products/${productId}`),
  getCategories: () => request<PaginatedResponse<ApiCategory>>("/products/categories"),
  getInventory: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiInventory>>("/inventory", query),
  getOrders: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiOrder>>("/orders", query),
  getMyOrders: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiOrder>>("/orders/me", query),
  getForecasts: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiForecast>>("/forecasts", query),
  getFulfillment: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiFulfillment>>("/fulfillment", query),
  getAIInsights: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiAIInsight>>("/ai-insights", query),
  askCopilot: (question: string) => post<ApiAIInsight>("/ai-insights/ask", { question }),
  login: (email: string, password: string) =>
    post<ApiTokenPair>("/auth/login", { email, password }),
  refresh: (refreshToken: string) =>
    post<ApiTokenPair>("/auth/refresh", { refresh_token: refreshToken }),
  getAdminUsers: (query?: Record<string, QueryValue>) =>
    request<PaginatedResponse<ApiUser>>("/admin/users", query),
  getAdminRoles: () => request<PaginatedResponse<ApiRole>>("/admin/roles"),
  getCurrentUser: () => request<ApiUser>("/auth/me"),
};
