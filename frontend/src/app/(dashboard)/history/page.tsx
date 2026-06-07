"use client";

import { GlassCard } from "@/components/ui/glass-card";
import { Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";

const executions = [
  { id: "1", workflow: "Email Auto-Reply", status: "completed", duration: "2.3s", cost: 0.02, time: "2 min ago" },
  { id: "2", workflow: "Data Analysis Report", status: "running", duration: "15.2s", cost: 0.05, time: "Running..." },
  { id: "3", workflow: "Customer Support Bot", status: "completed", duration: "1.1s", cost: 0.01, time: "15 min ago" },
  { id: "4", workflow: "Content Generator", status: "failed", duration: "5.4s", cost: 0.03, time: "1 hour ago" },
  { id: "5", workflow: "Lead Scoring", status: "completed", duration: "3.7s", cost: 0.02, time: "2 hours ago" },
];

const statusIcon = {
  completed: CheckCircle2,
  failed: XCircle,
  running: Loader2,
};

const statusColor = {
  completed: "text-emerald-400",
  failed: "text-red-400",
  running: "text-cyan-400",
};

export default function HistoryPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Execution History</h1>
        <p className="text-text-secondary mt-1">View all your workflow executions</p>
      </div>

      <GlassCard className="p-5">
        <div className="space-y-3">
          {executions.map((exec) => {
            const Icon = statusIcon[exec.status as keyof typeof statusIcon];
            return (
              <div key={exec.id} className="flex items-center gap-4 p-3 rounded-xl bg-white/5 hover:bg-white/8 transition-colors">
                <Icon className={`w-5 h-5 ${statusColor[exec.status as keyof typeof statusColor]} ${exec.status === "running" ? "animate-spin" : ""}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-text-primary font-medium text-sm">{exec.workflow}</p>
                  <p className="text-text-muted text-xs flex items-center gap-2">
                    <Clock className="w-3 h-3" /> {exec.time}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-text-secondary text-sm">{exec.duration}</p>
                  <p className="text-text-muted text-xs">${exec.cost.toFixed(2)}</p>
                </div>
              </div>
            );
          })}
        </div>
      </GlassCard>
    </div>
  );
}
