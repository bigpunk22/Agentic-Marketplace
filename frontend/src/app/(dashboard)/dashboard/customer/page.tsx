"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import {
  Zap, ShoppingBag, DollarSign, Play,
  TrendingUp, Clock, CheckCircle2, Loader2,
  Search, ExternalLink, Download,
} from "lucide-react";

interface CustomerStats {
  total_purchases: number;
  total_spent: number;
  total_workflows: number;
  total_executions: number;
  total_exec_cost: number;
  monthly_executions: number;
  monthly_cost: number;
}

interface Purchase {
  id: string;
  listing_id: string | null;
  amount: number;
  created_at: string | null;
}

interface CustomerWorkflow {
  id: string;
  name: string;
  status: string;
  execution_count: number;
  category: string | null;
  created_at: string | null;
}

export default function CustomerDashboardPage() {
  const [stats, setStats] = useState<CustomerStats | null>(null);
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [workflows, setWorkflows] = useState<CustomerWorkflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("overview");
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await apiFetch<{
          stats: CustomerStats;
          purchases: Purchase[];
          workflows: CustomerWorkflow[];
        }>("/api/v1/dashboard/customer");
        setStats(data.stats);
        setPurchases(data.purchases);
        setWorkflows(data.workflows);
      } catch (err) {
        console.error("Customer dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [isAuthenticated]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="w-8 h-8 text-accent-primary animate-spin" />
      </div>
    );
  }

  const timeAgo = (dateStr: string | null) => {
    if (!dateStr) return "—";
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const statusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge variant="success">Active</Badge>;
      case "paused":
        return <Badge variant="warning">Paused</Badge>;
      case "draft":
        return <Badge variant="default">Draft</Badge>;
      case "archived":
        return <Badge variant="danger">Archived</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  // ── Tab: Purchases ──────────────────────────────────────
  if (activeTab === "purchases") {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">My Purchases</h1>
          <p className="text-text-secondary mt-1">Workflows you've acquired from the marketplace</p>
        </div>

        {purchases.length === 0 ? (
          <GlassCard className="p-8 text-center">
            <ShoppingBag className="w-12 h-12 text-text-muted mx-auto mb-3" />
            <h3 className="text-text-primary font-medium">No purchases yet</h3>
            <p className="text-text-muted text-sm mt-1">Browse the marketplace to find AI workflows</p>
            <a href="/marketplace" className="glass-button mt-4 inline-flex items-center gap-2">
              <Search className="w-4 h-4" /> Browse Marketplace
            </a>
          </GlassCard>
        ) : (
          <div className="space-y-3">
            {purchases.map((p) => (
              <GlassCard key={p.id} hover className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                      <Download className="w-5 h-5 text-accent-primary" />
                    </div>
                    <div>
                      <p className="text-text-primary font-medium">
                        Purchase #{p.id.slice(0, 8)}
                      </p>
                      <p className="text-text-muted text-xs">{timeAgo(p.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-text-primary font-semibold">
                      {p.amount === 0 ? "Free" : `$${p.amount.toFixed(2)}`}
                    </span>
                    <Badge variant="success">Completed</Badge>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </div>
    );
  }

  // ── Default: Overview ────────────────────────────────────
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-text-primary">My Workspace</h1>
            <Badge variant="success">Customer</Badge>
          </div>
          <p className="text-text-secondary mt-1">Manage your AI workflows and usage</p>
        </div>
        <a href="/marketplace" className="glass-button flex items-center gap-2">
          <Search className="w-4 h-4" /> Browse Marketplace
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassCard hover className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-text-secondary text-sm">My Workflows</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                {stats ? stats.total_workflows : 0}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5">
              <Zap className="w-5 h-5 text-violet-400" />
            </div>
          </div>
        </GlassCard>
        <GlassCard hover className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-text-secondary text-sm">Total Executions</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                {stats ? stats.total_executions : 0}
              </p>
              {stats && stats.monthly_executions > 0 && (
                <p className="text-cyan-400 text-xs mt-1">{stats.monthly_executions} this month</p>
              )}
            </div>
            <div className="p-3 rounded-xl bg-white/5">
              <Play className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
        </GlassCard>
        <GlassCard hover className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-text-secondary text-sm">Total Spent</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                ${stats ? stats.total_spent.toFixed(2) : "0.00"}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5">
              <DollarSign className="w-5 h-5 text-emerald-400" />
            </div>
          </div>
        </GlassCard>
        <GlassCard hover className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-text-secondary text-sm">AI Costs</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                ${stats ? stats.total_exec_cost.toFixed(2) : "0.00"}
              </p>
              {stats && stats.monthly_cost > 0 && (
                <p className="text-amber-400 text-xs mt-1">${stats.monthly_cost.toFixed(2)} this month</p>
              )}
            </div>
            <div className="p-3 rounded-xl bg-white/5">
              <TrendingUp className="w-5 h-5 text-amber-400" />
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Two column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* My Workflows */}
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">My Workflows</h2>
            <a href="/workflows" className="text-accent-primary text-sm hover:underline">
              View all
            </a>
          </div>
          {workflows.length === 0 ? (
            <div className="text-center py-8">
              <Zap className="w-10 h-10 text-text-muted mx-auto mb-3" />
              <p className="text-text-secondary">No workflows yet</p>
              <p className="text-text-muted text-sm mt-1">Create one or buy from the marketplace</p>
            </div>
          ) : (
            <div className="space-y-3">
              {workflows.slice(0, 5).map((wf) => (
                <div
                  key={wf.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/8 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                      <Zap className="w-4 h-4 text-accent-primary" />
                    </div>
                    <div>
                      <p className="text-text-primary text-sm font-medium">{wf.name}</p>
                      <p className="text-text-muted text-xs">{wf.category || "Uncategorized"} · {wf.execution_count} runs</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {statusBadge(wf.status)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </GlassCard>

        {/* Recent Purchases */}
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">Recent Purchases</h2>
            <button
              onClick={() => setActiveTab("purchases")}
              className="text-accent-primary text-sm hover:underline"
            >
              View all
            </button>
          </div>
          {purchases.length === 0 ? (
            <div className="text-center py-8">
              <ShoppingBag className="w-10 h-10 text-text-muted mx-auto mb-3" />
              <p className="text-text-secondary">No purchases yet</p>
              <p className="text-text-muted text-sm mt-1">Buy workflows from the marketplace</p>
            </div>
          ) : (
            <div className="space-y-3">
              {purchases.slice(0, 5).map((p) => (
                <div key={p.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-accent-success/10 flex items-center justify-center">
                      <CheckCircle2 className="w-4 h-4 text-accent-success" />
                    </div>
                    <div>
                      <p className="text-text-primary text-sm font-medium">
                        Purchase #{p.id.slice(0, 8)}
                      </p>
                      <p className="text-text-muted text-xs">{timeAgo(p.created_at)}</p>
                    </div>
                  </div>
                  <span className="text-text-primary text-sm font-medium">
                    {p.amount === 0 ? "Free" : `$${p.amount.toFixed(2)}`}
                  </span>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <a href="/marketplace" className="block">
          <GlassCard hover className="p-5 text-center cursor-pointer">
            <div className="w-12 h-12 rounded-xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-3">
              <Search className="w-6 h-6 text-accent-primary" />
            </div>
            <h3 className="text-text-primary font-medium">Browse Marketplace</h3>
            <p className="text-text-muted text-sm mt-1">Discover AI workflows</p>
          </GlassCard>
        </a>
        <a href="/workflows" className="block">
          <GlassCard hover className="p-5 text-center cursor-pointer">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center mx-auto mb-3">
              <Zap className="w-6 h-6 text-cyan-400" />
            </div>
            <h3 className="text-text-primary font-medium">My Workflows</h3>
            <p className="text-text-muted text-sm mt-1">Manage your automations</p>
          </GlassCard>
        </a>
        <GlassCard hover className="p-5 text-center cursor-pointer" onClick={() => setActiveTab("purchases")}>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mx-auto mb-3">
            <ShoppingBag className="w-6 h-6 text-emerald-400" />
          </div>
          <h3 className="text-text-primary font-medium">My Purchases</h3>
          <p className="text-text-muted text-sm mt-1">View acquired workflows</p>
        </GlassCard>
      </div>
    </div>
  );
}
