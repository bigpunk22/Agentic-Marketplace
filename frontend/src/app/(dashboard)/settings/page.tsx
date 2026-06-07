"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import {
  Shield, Users, Key, Globe, Palette,
  Save, Plus, Trash2, Check, X, Copy,
} from "lucide-react";

const roles = ["Admin", "Operator", "Analyst", "Billing Manager", "Auditor"];
const permissions = [
  { key: "view_dashboard", label: "View Dashboard" },
  { key: "execute_workflows", label: "Execute Workflows" },
  { key: "create_workflows", label: "Create/Edit Workflows" },
  { key: "delete_workflows", label: "Delete Workflows" },
  { key: "view_analytics", label: "View Analytics" },
  { key: "export_reports", label: "Export Reports" },
  { key: "manage_users", label: "Manage Users" },
  { key: "assign_roles", label: "Assign Roles" },
  { key: "manage_billing", label: "Manage Billing" },
  { key: "manage_api_keys", label: "Manage API Keys" },
  { key: "configure_sso", label: "Configure SSO" },
  { key: "manage_branding", label: "Manage Branding" },
  { key: "view_audit_logs", label: "View Audit Logs" },
];

const rbacMatrix: Record<string, Record<string, boolean>> = {
  Admin: Object.fromEntries(permissions.map((p) => [p.key, true])),
  Operator: {
    view_dashboard: true, execute_workflows: true, create_workflows: true,
    delete_workflows: false, view_analytics: true, export_reports: true,
    manage_users: false, assign_roles: false, manage_billing: false,
    manage_api_keys: false, configure_sso: false, manage_branding: false, view_audit_logs: false,
  },
  Analyst: {
    view_dashboard: true, execute_workflows: false, create_workflows: false,
    delete_workflows: false, view_analytics: true, export_reports: true,
    manage_users: false, assign_roles: false, manage_billing: false,
    manage_api_keys: false, configure_sso: false, manage_branding: false, view_audit_logs: false,
  },
  "Billing Manager": {
    view_dashboard: true, execute_workflows: false, create_workflows: false,
    delete_workflows: false, view_analytics: true, export_reports: true,
    manage_users: false, assign_roles: false, manage_billing: true,
    manage_api_keys: false, configure_sso: false, manage_branding: false, view_audit_logs: false,
  },
  Auditor: {
    view_dashboard: true, execute_workflows: false, create_workflows: false,
    delete_workflows: false, view_analytics: true, export_reports: true,
    manage_users: false, assign_roles: false, manage_billing: false,
    manage_api_keys: false, configure_sso: false, manage_branding: false, view_audit_logs: true,
  },
};

const teamMembers = [
  { id: "1", name: "John Doe", email: "john@example.com", role: "Admin", joined: "2026-01-15" },
  { id: "2", name: "Jane Smith", email: "jane@example.com", role: "Operator", joined: "2026-02-20" },
  { id: "3", name: "Bob Wilson", email: "bob@example.com", role: "Analyst", joined: "2026-03-10" },
];

const apiKeys = [
  { id: "1", name: "Production API", prefix: "am_prod_...", created: "2026-01-20", lastUsed: "2 hours ago" },
  { id: "2", name: "Development", prefix: "am_dev_...", created: "2026-02-15", lastUsed: "1 day ago" },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("team");
  const [matrix, setMatrix] = useState(rbacMatrix);

  const togglePermission = (role: string, permission: string) => {
    setMatrix((prev) => ({
      ...prev,
      [role]: {
        ...prev[role],
        [permission]: !prev[role]?.[permission],
      },
    }));
  };

  const tabs = [
    { id: "team", label: "Team & RBAC", icon: Users },
    { id: "api", label: "API Keys", icon: Key },
    { id: "branding", label: "Branding", icon: Palette },
    { id: "sso", label: "SSO", icon: Globe },
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Settings</h1>
        <p className="text-text-secondary mt-1">Manage your team, permissions, and configuration</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? "bg-accent-primary/15 text-accent-primary border border-accent-primary/30"
                : "glass text-text-secondary hover:text-text-primary"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Team & RBAC Tab */}
      {activeTab === "team" && (
        <div className="space-y-6">
          {/* RBAC Matrix */}
          <GlassCard className="p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-accent-primary" />
                <h2 className="text-lg font-semibold text-text-primary">Role Permissions</h2>
              </div>
              <button className="glass-button flex items-center gap-2 text-sm">
                <Save className="w-4 h-4" /> Save Changes
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border-subtle">
                    <th className="text-left text-text-secondary text-sm font-medium pb-3 pr-4">Permission</th>
                    {roles.map((role) => (
                      <th key={role} className="text-center text-text-secondary text-sm font-medium pb-3 px-2 min-w-[100px]">
                        {role}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {permissions.map((perm) => (
                    <tr key={perm.key} className="border-b border-border-subtle/50">
                      <td className="py-2.5 pr-4 text-text-primary text-sm">{perm.label}</td>
                      {roles.map((role) => (
                        <td key={role} className="py-2.5 px-2 text-center">
                          <button
                            onClick={() => togglePermission(role, perm.key)}
                            className={`w-6 h-6 rounded-md flex items-center justify-center transition-colors ${
                              matrix[role]?.[perm.key]
                                ? "bg-accent-success/20 text-accent-success"
                                : "bg-white/5 text-text-muted"
                            }`}
                          >
                            {matrix[role]?.[perm.key] ? (
                              <Check className="w-4 h-4" />
                            ) : (
                              <X className="w-3 h-3" />
                            )}
                          </button>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>

          {/* Team Members */}
          <GlassCard className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Team Members</h2>
              <button className="glass-button flex items-center gap-2 text-sm">
                <Plus className="w-4 h-4" /> Invite Member
              </button>
            </div>
            <div className="space-y-3">
              {teamMembers.map((member) => (
                <div key={member.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                      <span className="text-accent-primary font-medium text-sm">
                        {member.name.split(" ").map((n) => n[0]).join("")}
                      </span>
                    </div>
                    <div>
                      <p className="text-text-primary font-medium text-sm">{member.name}</p>
                      <p className="text-text-muted text-xs">{member.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant={member.role === "Admin" ? "info" : "default"}>{member.role}</Badge>
                    <button className="p-1.5 rounded-lg hover:bg-white/5 text-text-muted hover:text-text-secondary">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}

      {/* API Keys Tab */}
      {activeTab === "api" && (
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Key className="w-5 h-5 text-accent-primary" />
              <h2 className="text-lg font-semibold text-text-primary">API Keys</h2>
            </div>
            <button className="glass-button flex items-center gap-2 text-sm">
              <Plus className="w-4 h-4" /> Generate Key
            </button>
          </div>
          <div className="space-y-3">
            {apiKeys.map((key) => (
              <div key={key.id} className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                <div>
                  <p className="text-text-primary font-medium">{key.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <code className="text-text-muted text-xs bg-white/5 px-2 py-0.5 rounded">{key.prefix}</code>
                    <button className="text-text-muted hover:text-text-secondary">
                      <Copy className="w-3 h-3" />
                    </button>
                  </div>
                  <p className="text-text-muted text-xs mt-1">Last used: {key.lastUsed}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="success">Active</Badge>
                  <button className="p-1.5 rounded-lg hover:bg-white/5 text-text-muted hover:text-red-400">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Branding Tab */}
      {activeTab === "branding" && (
        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Tenant Branding</h2>
          <div className="space-y-4">
            <div>
              <label className="text-text-secondary text-sm mb-1.5 block">Logo URL</label>
              <input type="text" placeholder="https://..." className="glass-input" />
            </div>
            <div>
              <label className="text-text-secondary text-sm mb-1.5 block">Primary Color</label>
              <div className="flex items-center gap-3">
                <input type="color" defaultValue="#8B5CF6" className="w-10 h-10 rounded-lg cursor-pointer" />
                <input type="text" defaultValue="#8B5CF6" className="glass-input flex-1" />
              </div>
            </div>
            <div>
              <label className="text-text-secondary text-sm mb-1.5 block">Custom Domain</label>
              <input type="text" placeholder="app.yourcompany.com" className="glass-input" />
            </div>
            <button className="glass-button flex items-center gap-2">
              <Save className="w-4 h-4" /> Save Branding
            </button>
          </div>
        </GlassCard>
      )}

      {/* SSO Tab */}
      {activeTab === "sso" && (
        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Single Sign-On (SSO)</h2>
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-white/5 border border-border-subtle">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-text-primary font-medium">SAML 2.0</p>
                  <p className="text-text-muted text-sm">Configure SAML-based SSO</p>
                </div>
                <Badge variant="default">Not Configured</Badge>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-border-subtle">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-text-primary font-medium">OIDC</p>
                  <p className="text-text-muted text-sm">OpenID Connect configuration</p>
                </div>
                <Badge variant="default">Not Configured</Badge>
              </div>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
