"use client";

import { cn } from "@/lib/utils";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Zap,
  Store,
  History,
  Settings,
  BarChart3,
  Shield,
  LogOut,
  ChevronLeft,
  ChevronRight,
  DollarSign,
  Package,
  ShoppingBag,
  Users,
  ClipboardCheck,
  Wallet,
} from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { SidebarNavItem } from "@/types/sidebar";

function getNavItems(user: ReturnType<typeof useAuthStore.getState>["user"]): SidebarNavItem[] {
  if (user?.is_super_admin) {
    return [
      { href: "/admin", icon: LayoutDashboard, label: "Overview" },
      { href: "/admin?tab=tenants", icon: Users, label: "Tenants" },
      { href: "/admin?tab=marketplace", icon: ClipboardCheck, label: "Approvals" },
      { href: "/admin?tab=payouts", icon: Wallet, label: "Payouts" },
      { href: "/admin?tab=audit", icon: Shield, label: "Audit Logs" },
      { href: "/analytics", icon: BarChart3, label: "Analytics" },
      { href: "/settings", icon: Settings, label: "Settings" },
    ];
  }

  if (user?.user_type === "creator") {
    return [
      { href: "/dashboard/creator", icon: LayoutDashboard, label: "Dashboard" },
      { href: "/workflows", icon: Zap, label: "My Workflows" },
      { href: "/dashboard/creator?tab=listings", icon: Package, label: "My Listings" },
      { href: "/dashboard/creator?tab=earnings", icon: DollarSign, label: "Earnings" },
      { href: "/marketplace", icon: Store, label: "Marketplace" },
      { href: "/analytics", icon: BarChart3, label: "Analytics" },
      { href: "/settings", icon: Settings, label: "Settings" },
    ];
  }

  // Customer (default)
  return [
    { href: "/dashboard/customer", icon: LayoutDashboard, label: "Dashboard" },
    { href: "/workflows", icon: Zap, label: "My Workflows" },
    { href: "/dashboard/customer?tab=purchases", icon: ShoppingBag, label: "My Purchases" },
    { href: "/marketplace", icon: Store, label: "Marketplace" },
    { href: "/history", icon: History, label: "History" },
    { href: "/analytics", icon: BarChart3, label: "Usage & Costs" },
    { href: "/settings", icon: Settings, label: "Settings" },
  ];
}

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const user = useAuthStore((s) => s.user);
  const navItems = getNavItems(user);

  const roleLabel = user?.is_super_admin
    ? "Super Admin"
    : user?.user_type === "creator"
    ? "Creator"
    : "Customer";

  const roleColor = user?.is_super_admin
    ? "text-accent-warning"
    : user?.user_type === "creator"
    ? "text-accent-primary"
    : "text-accent-success";

  return (
    <aside
      className={cn(
        "h-screen bg-bg-secondary border-r border-border-subtle flex flex-col transition-all duration-300 sticky top-0",
        collapsed ? "w-16" : "w-60"
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-border-subtle">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent-primary flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-text-primary">Agentic</span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-white/5 transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4 text-text-secondary" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-text-secondary" />
          )}
        </button>
      </div>

      {/* Role badge */}
      {!collapsed && (
        <div className="px-3 pt-3 pb-1">
          <span className={cn("text-[10px] font-semibold uppercase tracking-wider", roleColor)}>
            {roleLabel}
          </span>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href.split("?")[0]));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm",
                isActive
                  ? "bg-accent-primary/10 text-accent-primary border border-accent-primary/20"
                  : "text-text-secondary hover:bg-white/5 hover:text-text-primary"
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-2 border-t border-border-subtle">
        <button className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-text-secondary hover:bg-white/5 hover:text-text-primary transition-colors w-full text-sm">
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
