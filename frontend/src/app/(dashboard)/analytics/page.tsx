"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import {
  Users, DollarSign, Zap, TrendingUp,
  ArrowUpRight, ArrowDownRight, Filter, Download,
  Shield, UserCog, Eye, Settings2,
} from "lucide-react";

// ── Analytics Stats ────────────────────────────────────────
const stats = [
  { label: "Monthly Recurring Revenue", value: "$12,400", change: "+12.5%", up: true, icon: DollarSign },
  { label: "Active Workflows", value: "23", change: "+3", up: true, icon: Zap },
  { label: "Active Users", value: "47", change: "+8", up: true, icon: Users },
  { label: "Churn Rate", value: "2.3%", change: "-0.5%", up: false, icon: TrendingUp },
];

const execTrend = [
  { day: "Mon", value: 120 },
  { day: "Tue", value: 145 },
  { day: "Wed", value: 132 },
  { day: "Thu", value: 168 },
  { day: "Fri", value: 190 },
  { day: "Sat", value: 85 },
  { day: "Sun", value: 95 },
];

const maxExec = Math.max(...execTrend.map((d) => d.value));

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("7d");

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Analytics</h1>
          <p className="text-text-secondary mt-1">Monitor your team&apos;s AI usage and costs</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 glass p-1 rounded-xl">
            {["24h", "7d", "30d", "90d"].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  period === p
                    ? "bg-accent-primary/20 text-accent-primary"
                    : "text-text-secondary hover:text-text-primary"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
          <button className="glass-button flex items-center gap-2 text-sm">
            <Download className="w-4 h-4" /> Export
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <GlassCard key={stat.label} hover className="p-5">
            <div className="flex items-start justify-between">
              <div className="p-3 rounded-xl bg-white/5">
                <stat.icon className="w-5 h-5 text-accent-primary" />
              </div>
              <div className={`flex items-center gap-1 text-sm ${stat.up ? "text-emerald-400" : "text-red-400"}`}>
                {stat.up ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {stat.change}
              </div>
            </div>
            <p className="text-2xl font-bold text-text-primary mt-3">{stat.value}</p>
            <p className="text-text-secondary text-sm mt-1">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {/* Execution Trend Chart */}
      <GlassCard className="p-5">
        <h2 className="text-lg font-semibold text-text-primary mb-4">Workflow Executions</h2>
        <div className="flex items-end gap-3 h-48">
          {execTrend.map((d) => (
            <div key={d.day} className="flex-1 flex flex-col items-center gap-2">
              <span className="text-text-muted text-xs font-medium">{d.value}</span>
              <div
                className="w-full rounded-t-lg bg-gradient-to-t from-accent-primary/60 to-accent-secondary/40 transition-all duration-500 hover:from-accent-primary hover:to-accent-secondary"
                style={{ height: `${(d.value / maxExec) * 100}%` }}
              />
              <span className="text-text-muted text-xs">{d.day}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Health Score */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Tenant Health Score</h2>
          <div className="flex items-center justify-center">
            <div className="relative w-40 h-40">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                <circle
                  cx="50" cy="50" r="40" fill="none" stroke="#8B5CF6" strokeWidth="8"
                  strokeDasharray={`${0.85 * 251.2} ${251.2}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-text-primary">85</span>
                <span className="text-text-muted text-xs">out of 100</span>
              </div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {[
              { label: "Active Users", score: 92 },
              { label: "Error Rate", score: 95 },
              { label: "Cost Efficiency", score: 78 },
              { label: "Retention", score: 82 },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                <span className="text-text-secondary text-xs">{item.label}</span>
                <span className="text-text-primary text-xs font-medium">{item.score}%</span>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-text-primary mb-4">AI Usage Costs</h2>
          <div className="space-y-3">
            {[
              { model: "GPT-4o", cost: 24.50, percent: 45, color: "bg-accent-primary" },
              { model: "GPT-4o-mini", cost: 12.30, percent: 28, color: "bg-accent-secondary" },
              { model: "Claude 3.5", cost: 8.20, percent: 18, color: "bg-accent-success" },
              { model: "Others", cost: 2.40, percent: 9, color: "bg-accent-warning" },
            ].map((item) => (
              <div key={item.model}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-text-secondary text-sm">{item.model}</span>
                  <span className="text-text-primary text-sm font-medium">${item.cost.toFixed(2)}</span>
                </div>
                <div className="h-2 rounded-full bg-white/5 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${item.color} transition-all duration-500`}
                    style={{ width: `${item.percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
