"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import {
  Building2, Users, DollarSign, Zap, TrendingUp,
  CheckCircle2, XCircle, Clock, Search, Filter,
  ChevronRight, Shield,
} from "lucide-react";

const globalMetrics = [
  { label: "Active Tenants", value: "12,847", change: "+156", up: true, icon: Building2 },
  { label: "MRR", value: "$847K", change: "+12%", up: true, icon: DollarSign },
  { label: "Churn Rate", value: "2.3%", change: "-0.5%", up: false, icon: TrendingUp },
  { label: "Token Usage", value: "42.1M", change: "+8%", up: true, icon: Zap },
];

const pendingListings = [
  { id: "1", title: "AI Code Review Bot", creator: "DevTools Inc", category: "Development", submitted: "2 hours ago" },
  { id: "2", title: "Invoice Parser", creator: "FinTech Labs", category: "Finance", submitted: "5 hours ago" },
  { id: "3", title: "SEO Optimizer", creator: "MarketingPro", category: "Marketing", submitted: "1 day ago" },
];

const recentTenants = [
  { id: "1", name: "Acme Corp", plan: "Enterprise", status: "active", mrr: "$2,400", created: "2026-01-15" },
  { id: "2", name: "StartupXYZ", plan: "Pro", status: "trialing", mrr: "$0", created: "2026-05-20" },
  { id: "3", name: "Agency Co", plan: "Business", status: "active", mrr: "$199", created: "2026-03-10" },
  { id: "4", name: "Tech Inc", plan: "Pro", status: "suspended", mrr: "$49", created: "2026-02-28" },
];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState("overview");

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "tenants", label: "Tenants" },
    { id: "marketplace", label: "Marketplace" },
    { id: "payouts", label: "Payouts" },
    { id: "audit", label: "Audit Logs" },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-accent-primary" />
            <h1 className="text-2xl font-bold text-text-primary">Super Admin</h1>
          </div>
          <p className="text-text-secondary mt-1">Global platform governance and operations</p>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 rounded-xl text-sm transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? "bg-accent-primary/15 text-accent-primary border border-accent-primary/30"
                : "glass text-text-secondary hover:text-text-primary"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {globalMetrics.map((metric) => (
              <GlassCard key={metric.label} hover className="p-5">
                <div className="flex items-start justify-between">
                  <div className="p-3 rounded-xl bg-white/5">
                    <metric.icon className="w-5 h-5 text-accent-primary" />
                  </div>
                  <span className={`text-sm ${metric.up ? "text-emerald-400" : "text-red-400"}`}>
                    {metric.change}
                  </span>
                </div>
                <p className="text-2xl font-bold text-text-primary mt-3">{metric.value}</p>
                <p className="text-text-secondary text-sm mt-1">{metric.label}</p>
              </GlassCard>
            ))}
          </div>

          <GlassCard className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Pending Marketplace Approvals</h2>
              <Badge variant="warning">{pendingListings.length} pending</Badge>
            </div>
            <div className="space-y-3">
              {pendingListings.map((listing) => (
                <div key={listing.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent-warning/10 flex items-center justify-center">
                      <Clock className="w-5 h-5 text-accent-warning" />
                    </div>
                    <div>
                      <p className="text-text-primary font-medium text-sm">{listing.title}</p>
                      <p className="text-text-muted text-xs">by {listing.creator} · {listing.category}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-text-muted text-xs">{listing.submitted}</span>
                    <button className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20">
                      <CheckCircle2 className="w-4 h-4" />
                    </button>
                    <button className="p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20">
                      <XCircle className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}

      {activeTab === "tenants" && (
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">All Tenants</h2>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input type="text" placeholder="Search tenants..." className="glass-input pl-10 text-sm py-2 w-64" />
              </div>
              <button className="glass-button p-2"><Filter className="w-4 h-4" /></button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-subtle">
                  <th className="text-left text-text-secondary text-sm font-medium pb-3">Tenant</th>
                  <th className="text-left text-text-secondary text-sm font-medium pb-3">Plan</th>
                  <th className="text-left text-text-secondary text-sm font-medium pb-3">Status</th>
                  <th className="text-left text-text-secondary text-sm font-medium pb-3">MRR</th>
                  <th className="text-left text-text-secondary text-sm font-medium pb-3">Created</th>
                  <th className="text-right text-text-secondary text-sm font-medium pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentTenants.map((tenant) => (
                  <tr key={tenant.id} className="border-b border-border-subtle/50">
                    <td className="py-3 text-text-primary font-medium">{tenant.name}</td>
                    <td className="py-3"><Badge variant={tenant.plan === "Enterprise" ? "info" : "default"}>{tenant.plan}</Badge></td>
                    <td className="py-3"><Badge variant={tenant.status === "active" ? "success" : tenant.status === "trialing" ? "warning" : "danger"}>{tenant.status}</Badge></td>
                    <td className="py-3 text-text-primary">{tenant.mrr}</td>
                    <td className="py-3 text-text-muted text-sm">{tenant.created}</td>
                    <td className="py-3 text-right">
                      <button className="p-1.5 rounded-lg hover:bg-white/5 text-text-muted hover:text-text-primary">
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {activeTab === "marketplace" && (
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">Marketplace Moderation</h2>
            <Badge variant="warning">{pendingListings.length} pending review</Badge>
          </div>
          <div className="space-y-3">
            {pendingListings.map((listing) => (
              <div key={listing.id} className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                <div>
                  <p className="text-text-primary font-medium">{listing.title}</p>
                  <p className="text-text-muted text-sm">by {listing.creator} · {listing.category} · {listing.submitted}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button className="glass-button text-sm py-1.5 px-3">Review</button>
                  <button className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"><CheckCircle2 className="w-4 h-4" /></button>
                  <button className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20"><XCircle className="w-4 h-4" /></button>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {activeTab === "payouts" && (
        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Payout Queue</h2>
          <div className="space-y-3">
            {[
              { creator: "AI Labs", amount: "$2,450.00", status: "pending", method: "Bank Transfer" },
              { creator: "DataCo", amount: "$1,230.00", status: "pending", method: "PayPal" },
              { creator: "SupportAI", amount: "$890.00", status: "scheduled", method: "Bank Transfer" },
            ].map((payout, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                <div>
                  <p className="text-text-primary font-medium">{payout.creator}</p>
                  <p className="text-text-muted text-sm">{payout.method}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-text-primary font-semibold">{payout.amount}</span>
                  <Badge variant={payout.status === "pending" ? "warning" : "info"}>{payout.status}</Badge>
                  <button className="glass-button text-sm py-1.5 px-3">Process</button>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {activeTab === "audit" && (
        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Audit Logs</h2>
          <div className="space-y-2">
            {[
              { action: "listing_approved", user: "Admin", resource: "AI Code Review Bot", time: "2 hours ago" },
              { action: "tenant_suspended", user: "Admin", resource: "SpamCorp", time: "5 hours ago" },
              { action: "payout_processed", user: "System", resource: "$2,450 to AI Labs", time: "1 day ago" },
              { action: "user_role_changed", user: "Admin", resource: "jane@example.com → Operator", time: "2 days ago" },
              { action: "plan_upgraded", user: "Acme Corp", resource: "Pro → Enterprise", time: "3 days ago" },
            ].map((log, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent-primary" />
                  <div>
                    <p className="text-text-primary text-sm">
                      <span className="font-medium">{log.user}</span>{" "}
                      <span className="text-text-secondary">{log.action.replace(/_/g, " ")}</span>
                    </p>
                    <p className="text-text-muted text-xs">{log.resource}</p>
                  </div>
                </div>
                <span className="text-text-muted text-xs">{log.time}</span>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
}
