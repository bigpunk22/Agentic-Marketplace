"use client";

import { Bell, Search, User, ChevronDown, LogOut, Settings } from "lucide-react";
import { useState } from "react";

export function Topbar() {
  const [showProfile, setShowProfile] = useState(false);

  return (
    <header className="h-16 border-b border-border-subtle bg-bg-secondary/50 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-40">
      {/* Search */}
      <div className="relative w-96">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        <input
          type="text"
          placeholder="Search workflows, marketplace..."
          className="glass-input pl-10 text-sm py-2"
        />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Notifications */}
        <button className="relative p-2 rounded-xl hover:bg-white/5 transition-colors">
          <Bell className="w-5 h-5 text-text-secondary" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent-danger rounded-full" />
        </button>

        {/* Profile */}
        <div className="relative">
          <button
            onClick={() => setShowProfile(!showProfile)}
            className="flex items-center gap-2 p-2 rounded-xl hover:bg-white/5 transition-colors"
          >
            <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center">
              <User className="w-4 h-4 text-accent-primary" />
            </div>
            <span className="text-text-primary text-sm hidden sm:inline">User</span>
            <ChevronDown className="w-4 h-4 text-text-muted" />
          </button>

          {showProfile && (
            <div className="absolute right-0 top-full mt-2 w-48 glass-card py-2 z-50">
              <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-text-secondary hover:bg-white/5 hover:text-text-primary transition-colors">
                <Settings className="w-4 h-4" /> Settings
              </button>
              <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-text-secondary hover:bg-white/5 hover:text-text-primary transition-colors">
                <LogOut className="w-4 h-4" /> Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
