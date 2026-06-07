"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { apiFetch } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import {
  Activity, Zap, DollarSign, Clock, TrendingUp, Play,
  Search, Bell, ChevronRight, Loader2,
} from "lucide-react";

interface DashboardStats {
  total_executions: number;
  active_workflows: number;
  monthly_cost: number;
  avg_duration_ms: number;
}

interface RecentExecution {
  id: string;
  workflow_id: string;
  status: string;
  cost: number | null;
  duration_ms: number | null;
  created_at: string | null;
}

interface ActiveWorkflow {
  id: string;
  name: string;
  status: string;
  execution_count: number;
  category: string | null;
  created_at: string | null;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentExecutions, setRecentExecutions] = useState<RecentExecution[]>([]);
  const [activeWorkflows, setActiveWorkflows] = useState<ActiveWorkflow[]>([]);
  const [loading, setLoading] = useState(true);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const [workflows, usage] = await Promise.all([
          apiFetch<ActiveWorkflow[]>("/api/v1/workflows?limit=5"),
          apiFetch<{ daily_usage: { executions: number; cost: number }[]; tenant_id: string }>("/api/v1/billing/usage").catch(() => null),
        ]);
        setActiveWorkflows(workflows.filter((w) => w.status === "active").slice(0, 3));

        const totalExecutions = workflows.reduce((sum, w) => sum + w.execution_count, 0);
        const activeCount = workflows.filter((w) => w.status === "active").length;
        const monthlyCost = usage?.daily_usage ? usage.daily_usage.reduce((s, d) => s + d.cost, 0) : 0;

        setStats({
          total_executions: totalExecutions,
          active_workflows: activeCount,
          monthly_cost: monthlyCost,
          avg_duration_ms: 0,
        });

        // Fetch recent executions for active workflows
        if (workflows.length > 0) {
          try {
            const execs = await apiFetch<RecentExecution[]>(`/api/v1/workflows/${workflows[0].id}/executions?limit=5`);
            setRecentExecutions(execs);
          } catch {
            setRecentExecutions([]);
          }
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
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

  const statsData = [
    {
      label: "Total Executions",
      value: stats ? stats.total_executions.toLocaleString() : "—",
      icon: Zap,
      color: "text-violet-400",
    },
    {
      label: "Active Workflows",
      value: stats ? stats.active_workflows.toString() : "—",
      icon: Activity,
      color: "text-cyan-400",
    },
    {
      label: "Monthly Cost",
      value: stats ? `$${stats.monthly_cost.toFixed(2)}` : "—",
      icon: DollarSign,
      color: "text-emerald-400",
    },
    {
      label: "Avg Duration",
      value: stats && stats.avg_duration_ms > 0 ? `${(stats.avg_duration_ms / 1000).toFixed(1)}s` : "—",
      icon: Clock,
      color: "text-amber-400",
    },
  ];

  const statusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-emerald-400";
      case "running": return "bg-cyan-400";
      case "failed": return "bg-red-400";
      case "pending": return "bg-amber-400";
      default: return "bg-gray-400";
    }
  };

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

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Welcome back</h1>
          <p className="text-text-secondary mt-1">Here&apos;s what&apos;s happening with your AI workflows</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="glass-button flex items-center gap-2">
            <Search className="w-4 h-4" />
            <span className="hidden sm:inline">Search</span>
          </button>
          <button className="glass-button relative">
            <Bell className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-accent-danger rounded-full" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsData.map((stat) => (
          <GlassCard key={stat.label} hover className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-text-secondary text-sm">{stat.label}</p>
                <p className="text-2xl font-bold text-text-primary mt-1">{stat.value}</p>
              </div>
              <div className="p-3 rounded-xl bg-white/5">
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
            </div>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <GlassCard className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Active Workflows</h2>
              <button className="text-accent-primary text-sm flex items-center gap-1 hover:underline">
                View all <ChevronRight className="w-4 h-4" />
              </button>
            </div>
            {activeWorkflows.length === 0 ? (
              <div className="text-center py-8">
                <Zap className="w-10 h-10 text-text-muted mx-auto mb-3" />
                <p className="text-text-secondary">No active workflows yet</p>
                <p className="text-text-muted text-sm mt-1">Create a workflow or browse the marketplace</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activeWorkflows.map((wf) => (
                  <div
                    key={wf.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/8 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                        <Zap className="w-5 h-5 text-accent-primary" />
                      </div>
                      <div>
                        <p className="text-text-primary font-medium">{wf.name}</p>
                        <p className="text-text-muted text-sm">{wf.category || "Uncategorized"}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-text-secondary text-sm">{wf.execution_count} runs</span>
                      <button className="p-2 rounded-lg bg-accent-primary/10 hover:bg-accent-primary/20 transition-colors">
                        <Play className="w-4 h-4 text-accent-primary" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </GlassCard>
        </div>

        <div>
          <GlassCard className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Recent Activity</h2>
            </div>
            {recentExecutions.length === 0 ? (
              <div className="text-center py-8">
                <Activity className="w-10 h-10 text-text-muted mx-auto mb-3" />
                <p className="text-text-secondary">No recent executions</p>
                <p className="text-text-muted text-sm mt-1">Run a workflow to see activity</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentExecutions.map((exec) => (
                  <div key={exec.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/5">
                    <div className={`w-2 h-2 rounded-full ${statusColor(exec.status)}`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-text-primary text-sm font-medium truncate">
                        {exec.status.charAt(0).toUpperCase() + exec.status.slice(1)}
                      </p>
                      <p className="text-text-muted text-xs">{timeAgo(exec.created_at)}</p>
                    </div>
                    <span className="text-text-secondary text-xs">
                      {exec.cost !== null ? `$${exec.cost.toFixed(4)}` : "—"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </GlassCard>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <GlassCard hover glow className="p-5 text-center cursor-pointer">
          <div className="w-12 h-12 rounded-xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-3">
            <Search className="w-6 h-6 text-accent-primary" />
          </div>
          <h3 className="text-text-primary font-medium">Browse Marketplace</h3>
          <p className="text-text-muted text-sm mt-1">Discover AI workflows</p>
        </GlassCard>
        <GlassCard hover className="p-5 text-center cursor-pointer">
          <div className="w-12 h-12 rounded-xl bg-accent-secondary/10 flex items-center justify-center mx-auto mb-3">
            <Zap className="w-6 h-6 text-accent-secondary" />
          </div>
          <h3 className="text-text-primary font-medium">Create Workflow</h3>
          <p className="text-text-muted text-sm mt-1">Build a custom automation</p>
        </GlassCard>
        <GlassCard hover className="p-5 text-center cursor-pointer">
          <div className="w-12 h-12 rounded-xl bg-accent-success/10 flex items-center justify-center mx-auto mb-3">
            <TrendingUp className="w-6 h-6 text-accent-success" />
          </div>
          <h3 className="text-text-primary font-medium">View Analytics</h3>
          <p className="text-text-muted text-sm mt-1">Track your usage</p>
        </GlassCard>
      </div>
    </div>
  );
}
