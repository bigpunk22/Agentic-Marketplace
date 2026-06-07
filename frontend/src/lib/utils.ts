import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(amount);
}

export function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60_000).toFixed(1)}m`;
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(date));
}

export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const then = new Date(date);
  const diffMs = now.getTime() - then.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return formatDate(date);
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: "text-emerald-400",
    completed: "text-emerald-400",
    running: "text-cyan-400",
    pending: "text-amber-400",
    failed: "text-red-400",
    cancelled: "text-gray-400",
    suspended: "text-red-400",
    draft: "text-gray-400",
    paused: "text-amber-400",
    approved: "text-emerald-400",
    rejected: "text-red-400",
  };
  return colors[status] || "text-gray-400";
}

export function getStatusBg(status: string): string {
  const colors: Record<string, string> = {
    active: "bg-emerald-500/10 border-emerald-500/30",
    completed: "bg-emerald-500/10 border-emerald-500/30",
    running: "bg-cyan-500/10 border-cyan-500/30",
    pending: "bg-amber-500/10 border-amber-500/30",
    failed: "bg-red-500/10 border-red-500/30",
    cancelled: "bg-gray-500/10 border-gray-500/30",
    suspended: "bg-red-500/10 border-red-500/30",
    draft: "bg-gray-500/10 border-gray-500/30",
    paused: "bg-amber-500/10 border-amber-500/30",
    approved: "bg-emerald-500/10 border-emerald-500/30",
    rejected: "bg-red-500/10 border-red-500/30",
  };
  return colors[status] || "bg-gray-500/10 border-gray-500/30";
}
