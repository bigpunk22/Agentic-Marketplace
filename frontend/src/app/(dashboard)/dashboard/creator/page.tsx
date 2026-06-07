"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import {
  DollarSign, Package, TrendingUp, ShoppingCart,
  CheckCircle2, Clock, XCircle, Eye, Plus,
  Loader2, Zap,
} from "lucide-react";

interface CreatorStats {
  total_listings: number;
  approved_listings: number;
  pending_listings: number;
  total_sales: number;
  total_earnings: number;
  monthly_earnings: number;
}

interface CreatorListing {
  id: string;
  title: string;
  status: string;
  price: number;
  price_type: string;
  category: string | null;
  tags: string[];
  rating_avg: number;
  rating_count: number;
  purchase_count: number;
  revenue_total: number;
  created_at: string | null;
}

interface RecentSale {
  id: string;
  listing_id: string | null;
  buyer_id: string | null;
  amount: number;
  creator_amount: number;
  created_at: string | null;
}

export default function CreatorDashboardPage() {
  const [stats, setStats] = useState<CreatorStats | null>(null);
  const [listings, setListings] = useState<CreatorListing[]>([]);
  const [recentSales, setRecentSales] = useState<RecentSale[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("overview");
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await apiFetch<{
          stats: CreatorStats;
          listings: CreatorListing[];
          recent_sales: RecentSale[];
        }>("/api/v1/dashboard/creator");
        setStats(data.stats);
        setListings(data.listings);
        setRecentSales(data.recent_sales);
      } catch (err) {
        console.error("Creator dashboard fetch error:", err);
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

  const statusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return <Badge variant="success">Approved</Badge>;
      case "pending_review":
        return <Badge variant="warning">Pending Review</Badge>;
      case "rejected":
        return <Badge variant="danger">Rejected</Badge>;
      case "draft":
        return <Badge variant="default">Draft</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
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

  // ── Tab: Listings ───────────────────────────────────────
  if (activeTab === "listings") {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">My Listings</h1>
            <p className="text-text-secondary mt-1">Manage your marketplace listings</p>
          </div>
          <button className="glass-button flex items-center gap-2">
            <Plus className="w-4 h-4" /> Publish New
          </button>
        </div>

        {listings.length === 0 ? (
          <GlassCard className="p-8 text-center">
            <Package className="w-12 h-12 text-text-muted mx-auto mb-3" />
            <h3 className="text-text-primary font-medium">No listings yet</h3>
            <p className="text-text-muted text-sm mt-1">Publish your first workflow to the marketplace</p>
            <button className="glass-button mt-4 inline-flex items-center gap-2">
              <Plus className="w-4 h-4" /> Create Listing
            </button>
          </GlassCard>
        ) : (
          <div className="space-y-3">
            {listings.map((l) => (
              <GlassCard key={l.id} hover className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center flex-shrink-0">
                      <Zap className="w-5 h-5 text-accent-primary" />
                    </div>
                    <div>
                      <h3 className="text-text-primary font-medium">{l.title}</h3>
                      <p className="text-text-muted text-sm">{l.category || "Uncategorized"}</p>
                      <div className="flex items-center gap-2 mt-2">
                        {statusBadge(l.status)}
                        <span className="text-text-secondary text-sm">
                          {l.price === 0 ? "Free" : `$${l.price}`}
                        </span>
                      </div>
                      {l.tags.length > 0 && (
                        <div className="flex gap-1 mt-2 flex-wrap">
                          {l.tags.slice(0, 3).map((tag) => (
                            <span key={tag} className="px-2 py-0.5 rounded-full text-xs bg-white/5 text-text-muted">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0 ml-4">
                    <p className="text-text-primary font-semibold">{l.purchase_count} sales</p>
                    <p className="text-text-muted text-xs">${l.revenue_total.toFixed(2)} earned</p>
                    <div className="flex items-center gap-1 mt-1 justify-end">
                      <Eye className="w-3 h-3 text-text-muted" />
                      <span className="text-text-muted text-xs">⭐ {l.rating_avg.toFixed(1)} ({l.rating_count})</span>
                    </div>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </div>
    );
  }

  // ── Tab: Earnings ───────────────────────────────────────
  if (activeTab === "earnings") {
    return (
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Earnings</h1>
          <p className="text-text-secondary mt-1">Track your marketplace revenue</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard hover className="p-5">
            <div className="flex items-start justify-between">
              <p className="text-text-secondary text-sm">Total Earnings</p>
              <div className="p-3 rounded-xl bg-white/5">
                <DollarSign className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <p className="text-2xl font-bold text-text-primary mt-3">
              ${stats ? stats.total_earnings.toFixed(2) : "0.00"}
            </p>
          </GlassCard>
          <GlassCard hover className="p-5">
            <div className="flex items-start justify-between">
              <p className="text-text-secondary text-sm">This Month</p>
              <div className="p-3 rounded-xl bg-white/5">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <p className="text-2xl font-bold text-text-primary mt-3">
              ${stats ? stats.monthly_earnings.toFixed(2) : "0.00"}
            </p>
          </GlassCard>
          <GlassCard hover className="p-5">
            <div className="flex items-start justify-between">
              <p className="text-text-secondary text-sm">Total Sales</p>
              <div className="p-3 rounded-xl bg-white/5">
                <ShoppingCart className="w-5 h-5 text-violet-400" />
              </div>
            </div>
            <p className="text-2xl font-bold text-text-primary mt-3">
              {stats ? stats.total_sales : 0}
            </p>
          </GlassCard>
          <GlassCard hover className="p-5">
            <div className="flex items-start justify-between">
              <p className="text-text-secondary text-sm">Active Listings</p>
              <div className="p-3 rounded-xl bg-white/5">
                <Package className="w-5 h-5 text-amber-400" />
              </div>
            </div>
            <p className="text-2xl font-bold text-text-primary mt-3">
              {stats ? stats.approved_listings : 0}
            </p>
          </GlassCard>
        </div>

        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Recent Sales</h2>
          {recentSales.length === 0 ? (
            <div className="text-center py-8">
              <ShoppingCart className="w-10 h-10 text-text-muted mx-auto mb-3" />
              <p className="text-text-secondary">No sales yet</p>
              <p className="text-text-muted text-sm mt-1">When customers buy your listings, sales will appear here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentSales.map((sale) => (
                <div key={sale.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                      <DollarSign className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-text-primary text-sm font-medium">
                        Sale #{sale.id.slice(0, 8)}
                      </p>
                      <p className="text-text-muted text-xs">{timeAgo(sale.created_at)}</p>
                    </div>
                  </div>
                  <span className="text-emerald-400 font-semibold">+${sale.creator_amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </div>
    );
  }

  // ── Default: Overview ────────────────────────────────────
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-text-primary">Creator Studio</h1>
            <Badge variant="info">Creator</Badge>
          </div>
          <p className="text-text-secondary mt-1">Build, publish, and earn from AI workflows</p>
        </div>
        <button className="glass-button flex items-center gap-2">
          <Plus className="w-4 h-4" /> Publish Workflow
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassCard hover className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-text-secondary text-sm">Total Earnings</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                ${stats ? stats.total_earnings.toFixed(2) : "0.00"}
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
              <p className="text-text-secondary text-sm">Monthly Earnings</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                ${stats ? stats.monthly_earnings.toFixed(2) : "0.00"}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
        </GlassCard>
        <GlassCard hover className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-text-secondary text-sm">Total Sales</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                {stats ? stats.total_sales : 0}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5">
              <ShoppingCart className="w-5 h-5 text-violet-400" />
            </div>
          </div>
        </GlassCard>
        <GlassCard hover className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-text-secondary text-sm">Listings</p>
              <p className="text-2xl font-bold text-text-primary mt-1">
                {stats ? `${stats.approved_listings}/${stats.total_listings}` : "0/0"}
              </p>
              {stats && stats.pending_listings > 0 && (
                <p className="text-amber-400 text-xs mt-1">{stats.pending_listings} pending review</p>
              )}
            </div>
            <div className="p-3 rounded-xl bg-white/5">
              <Package className="w-5 h-5 text-amber-400" />
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Two column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* My Listings */}
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">My Listings</h2>
            <button
              onClick={() => setActiveTab("listings")}
              className="text-accent-primary text-sm hover:underline"
            >
              View all
            </button>
          </div>
          {listings.length === 0 ? (
            <div className="text-center py-8">
              <Package className="w-10 h-10 text-text-muted mx-auto mb-3" />
              <p className="text-text-secondary">No listings yet</p>
              <p className="text-text-muted text-sm mt-1">Publish your first workflow</p>
            </div>
          ) : (
            <div className="space-y-3">
              {listings.slice(0, 5).map((l) => (
                <div key={l.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                      <Zap className="w-4 h-4 text-accent-primary" />
                    </div>
                    <div>
                      <p className="text-text-primary text-sm font-medium">{l.title}</p>
                      <p className="text-text-muted text-xs">{statusBadge(l.status)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-text-primary text-sm">{l.purchase_count} sold</p>
                    <p className="text-emerald-400 text-xs">${l.revenue_total.toFixed(2)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </GlassCard>

        {/* Recent Sales */}
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">Recent Sales</h2>
            <button
              onClick={() => setActiveTab("earnings")}
              className="text-accent-primary text-sm hover:underline"
            >
              View earnings
            </button>
          </div>
          {recentSales.length === 0 ? (
            <div className="text-center py-8">
              <ShoppingCart className="w-10 h-10 text-text-muted mx-auto mb-3" />
              <p className="text-text-secondary">No sales yet</p>
              <p className="text-text-muted text-sm mt-1">Sales will appear here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentSales.slice(0, 5).map((sale) => (
                <div key={sale.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                      <DollarSign className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-text-primary text-sm font-medium">
                        Sale #{sale.id.slice(0, 8)}
                      </p>
                      <p className="text-text-muted text-xs">{timeAgo(sale.created_at)}</p>
                    </div>
                  </div>
                  <span className="text-emerald-400 font-semibold text-sm">+${sale.creator_amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <GlassCard hover className="p-5 text-center cursor-pointer" onClick={() => setActiveTab("listings")}>
          <div className="w-12 h-12 rounded-xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-3">
            <Package className="w-6 h-6 text-accent-primary" />
          </div>
          <h3 className="text-text-primary font-medium">My Listings</h3>
          <p className="text-text-muted text-sm mt-1">Manage published workflows</p>
        </GlassCard>
        <GlassCard hover className="p-5 text-center cursor-pointer" onClick={() => setActiveTab("earnings")}>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mx-auto mb-3">
            <DollarSign className="w-6 h-6 text-emerald-400" />
          </div>
          <h3 className="text-text-primary font-medium">Earnings</h3>
          <p className="text-text-muted text-sm mt-1">Track your revenue</p>
        </GlassCard>
        <GlassCard hover className="p-5 text-center cursor-pointer" onClick={() => setActiveTab("listings")}>
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center mx-auto mb-3">
            <Plus className="w-6 h-6 text-cyan-400" />
          </div>
          <h3 className="text-text-primary font-medium">Publish New</h3>
          <p className="text-text-muted text-sm mt-1">List a workflow on marketplace</p>
        </GlassCard>
      </div>
    </div>
  );
}
