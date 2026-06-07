"use client";

import { useState, useCallback } from "react";
import { useAuthStore } from "@/stores/auth-store";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
  retryCount?: number;
}

export async function apiFetch<T>(
  path: string,
  options: FetchOptions = {}
): Promise<T> {
  const { skipAuth = false, retryCount = 0, headers = {}, ...rest } = options;

  const { accessToken, refreshAccessToken, logout } = useAuthStore.getState();

  const response = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken && !skipAuth ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...headers,
    },
  });

  // Handle 401 by refreshing token once, then retry
  if (response.status === 401 && !skipAuth && retryCount < 1) {
    try {
      await refreshAccessToken();
      // Retry with fresh token (increment retryCount to prevent infinite loops)
      return apiFetch<T>(path, { ...options, retryCount: retryCount + 1 });
    } catch {
      logout();
      throw new Error("Session expired. Please log in again.");
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

/** Typed API helpers */
export const api = {
  marketplace: {
    getListings: (params?: {
      search?: string;
      category?: string;
      sort?: string;
      page?: number;
      limit?: number;
    }) => {
      const searchParams = new URLSearchParams();
      if (params?.search) searchParams.set("search", params.search);
      if (params?.category && params.category !== "all") searchParams.set("category", params.category);
      if (params?.sort) searchParams.set("sort", params.sort);
      if (params?.page) searchParams.set("page", params.page.toString());
      if (params?.limit) searchParams.set("limit", params.limit.toString());
      const query = searchParams.toString();
      return apiFetch(`/api/v1/marketplace/listings${query ? `?${query}` : ""}`);
    },
    getCategories: () => apiFetch<string[]>(`/api/v1/marketplace/categories`),
    getFeatured: () => apiFetch(`/api/v1/marketplace/featured`),
    purchase: (id: string) =>
      apiFetch(`/api/v1/marketplace/listings/${id}/purchase`, { method: "POST" }),
  },
  billing: {
    getUsage: () => apiFetch(`/api/v1/billing/usage`),
  },
  workflows: {
    getAll: () => apiFetch(`/api/v1/workflows`),
    create: (data: { name: string; description?: string; workspace_id?: string }) =>
      apiFetch(`/api/v1/workflows`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },
  workspaces: {
    getAll: () => apiFetch(`/api/v1/workspaces`),
  },
};

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = useCallback(async <T>(path: string, options?: FetchOptions): Promise<T | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFetch<T>(path, options);
      return result;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return { request, loading, error, clearError };
}
