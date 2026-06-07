"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { apiFetch } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { Workflow } from "@/types";
import {
  Zap, Play, Pause, Plus, Search, Loader2,
  CheckCircle2, XCircle, Edit3, Settings,
} from "lucide-react";

const statusConfig: Record<string, { icon: typeof CheckCircle2; color: string; bg: string }> = {
  active: { icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30" },
  paused: { icon: Pause, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30" },
  draft: { icon: Edit3, color: "text-gray-400", bg: "bg-gray-500/10 border-gray-500/30" },
  archived: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10 border-red-500/30" },
};

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  const fetchWorkflows = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.set("status", statusFilter);
      const data = await apiFetch<Workflow[]>(`/api/v1/workflows?${params}`);
      setWorkflows(data);
    } catch (err: any) {
      setError(err.message || "Failed to load workflows");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) fetchWorkflows();
  }, [isAuthenticated, statusFilter]);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      // First get or create a workspace
      const workspaces = await apiFetch<{ id: string }[]>("/api/v1/workspaces");
      let workspaceId = workspaces[0]?.id;
      if (!workspaceId) {
        const ws = await apiFetch<{ id: string }>("/api/v1/workspaces", {
          method: "POST",
          body: JSON.stringify({ name: "Default Workspace" }),
        });
        workspaceId = ws.id;
      }

      await apiFetch("/api/v1/workflows", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          name: newName,
          description: newDescription || undefined,
          config: { prompt: "", model: "openai/gpt-4o-mini" },
        }),
      });
      setShowCreateModal(false);
      setNewName("");
      setNewDescription("");
      await fetchWorkflows();
    } catch (err: any) {
      alert(err.message || "Failed to create workflow");
    } finally {
      setCreating(false);
    }
  };

  const handleExecute = async (workflowId: string) => {
    try {
      await apiFetch(`/api/v1/workflows/${workflowId}/execute`, {
        method: "POST",
        body: JSON.stringify({ input_data: {} }),
      });
      alert("Workflow execution started!");
    } catch (err: any) {
      alert(err.message || "Failed to execute workflow");
    }
  };

  const filtered = workflows.filter((wf) =>
    wf.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Workflows</h1>
          <p className="text-text-secondary mt-1">
            {workflows.length} workflows · {workflows.filter((w) => w.status === "active").length} active
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="glass-button flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> New Workflow
        </button>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search workflows..."
            className="glass-input pl-10 text-sm"
          />
        </div>
        <div className="flex items-center gap-1 glass p-1 rounded-xl">
          {["all", "active", "paused", "draft"].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-sm capitalize transition-colors ${
                statusFilter === s
                  ? "bg-accent-primary/20 text-accent-primary"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 text-accent-primary animate-spin" />
        </div>
      )}

      {error && <div className="text-center py-16 text-red-400">{error}</div>}

      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-16">
          <Zap className="w-12 h-12 text-text-muted mx-auto mb-4" />
          <h3 className="text-text-primary font-medium">No workflows found</h3>
          <p className="text-text-muted text-sm mt-1">
            {searchQuery ? "Try adjusting your search" : "Create your first workflow to get started"}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((wf) => {
          const config = statusConfig[wf.status] || statusConfig.draft;
          const StatusIcon = config.icon;
          return (
            <GlassCard key={wf.id} hover className="p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-accent-primary" />
                </div>
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border ${config.bg}`}>
                  <StatusIcon className={`w-3 h-3 ${config.color}`} />
                  <span className={config.color}>{wf.status}</span>
                </span>
              </div>
              <h3 className="text-text-primary font-medium">{wf.name}</h3>
              <p className="text-text-muted text-sm mt-1">{wf.category || "Uncategorized"}</p>
              <div className="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-border-subtle">
                <div>
                  <p className="text-text-muted text-xs">Runs</p>
                  <p className="text-text-primary text-sm font-medium">{wf.execution_count}</p>
                </div>
                <div>
                  <p className="text-text-muted text-xs">Version</p>
                  <p className="text-text-primary text-sm font-medium">v{wf.version}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 mt-4">
                <button
                  onClick={() => handleExecute(wf.id)}
                  disabled={wf.status !== "active"}
                  className="glass-button flex-1 flex items-center justify-center gap-2 text-sm py-2 disabled:opacity-50"
                >
                  <Play className="w-4 h-4" /> Run
                </button>
                <button className="p-2 rounded-xl glass hover:border-accent-primary/30 transition-colors">
                  <Settings className="w-4 h-4 text-text-secondary" />
                </button>
              </div>
            </GlassCard>
          );
        })}
      </div>

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <GlassCard className="p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Create New Workflow</h2>
            <div className="space-y-4">
              <div>
                <label className="text-text-secondary text-sm mb-1.5 block">Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="My AI Workflow"
                  className="glass-input"
                />
              </div>
              <div>
                <label className="text-text-secondary text-sm mb-1.5 block">Description</label>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="What does this workflow do?"
                  className="glass-input min-h-[80px] resize-none"
                />
              </div>
              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="glass-button flex-1 justify-center"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreate}
                  disabled={creating || !newName.trim()}
                  className="glass-button flex-1 justify-center bg-accent-primary/20 border-accent-primary/30 disabled:opacity-50"
                >
                  {creating ? "Creating..." : "Create"}
                </button>
              </div>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
