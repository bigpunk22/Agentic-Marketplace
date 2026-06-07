"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";

interface Workspace {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  settings: Record<string, unknown>;
  created_at: string | null;
}

interface UseWorkspacesReturn {
  workspaces: Workspace[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useWorkspaces(): UseWorkspacesReturn {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkspaces = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.workspaces.getAll();
      setWorkspaces(Array.isArray(data) ? data : (data as any)?.data ?? []);
    } catch (err: any) {
      setError(err.message || "Failed to load workspaces");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  return { workspaces, loading, error, refetch: fetchWorkspaces };
}
