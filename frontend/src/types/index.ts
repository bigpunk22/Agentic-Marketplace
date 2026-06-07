/** Type definitions for Agentic Marketplace */

// ── User & Auth ──────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  user_type: "creator" | "customer" | null;
  is_super_admin: boolean;
  mfa_enabled: boolean;
  status: "active" | "suspended" | "pending";
  created_at: string | null;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
}

// ── Tenant & Workspace ───────────────────────────────────
export interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: "free" | "pro" | "business" | "enterprise";
  status: "active" | "suspended" | "trialing" | "cancelled";
  branding_config: Record<string, unknown>;
  created_at: string | null;
}

export interface Workspace {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  settings: Record<string, unknown>;
  created_at: string | null;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: "admin" | "operator" | "analyst" | "billing_manager" | "auditor";
  permissions: Record<string, boolean>;
  joined_at: string;
}

// ── Workflow ─────────────────────────────────────────────
export interface Workflow {
  id: string;
  tenant_id: string;
  workspace_id: string;
  created_by: string;
  name: string;
  description: string | null;
  category: string | null;
  tags: string[];
  config: Record<string, unknown>;
  is_template: boolean;
  is_published: boolean;
  version: number;
  execution_count: number;
  avg_duration_ms: number | null;
  status: "draft" | "active" | "paused" | "archived";
  created_at: string | null;
  updated_at: string | null;
}

export interface WorkflowExecution {
  id: string;
  workflow_id: string;
  triggered_by: string | null;
  trigger_type: "manual" | "scheduled" | "api" | "webhook";
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  input_data: Record<string, unknown> | null;
  output_data: Record<string, unknown> | null;
  error_message: string | null;
  token_usage: Record<string, { input: number; output: number }> | null;
  cost: number | null;
  duration_ms: number | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string | null;
}

// ── Marketplace ──────────────────────────────────────────
export interface MarketplaceListing {
  id: string;
  workflow_id: string;
  creator_id: string;
  tenant_id: string;
  title: string;
  description: string | null;
  price_type: "free" | "one_time" | "subscription";
  price: number;
  billing_period: "monthly" | "yearly" | null;
  category: string | null;
  tags: string[];
  screenshots: string[];
  status: "draft" | "pending_review" | "approved" | "rejected" | "suspended";
  rating_avg: number;
  rating_count: number;
  purchase_count: number;
  revenue_total: number;
  published_at: string | null;
  created_at: string | null;
}

export interface Transaction {
  id: string;
  buyer_id: string | null;
  seller_id: string | null;
  listing_id: string | null;
  tenant_id: string | null;
  type: "purchase" | "subscription" | "refund" | "payout";
  amount: number;
  platform_fee: number;
  creator_amount: number;
  currency: string;
  status: "pending" | "completed" | "failed" | "refunded" | "disputed";
  payment_method: string | null;
  created_at: string | null;
}

// ── Notifications ────────────────────────────────────────
export interface Notification {
  id: string;
  user_id: string;
  type: "execution_complete" | "execution_failed" | "billing_alert" | "system";
  title: string;
  message: string;
  read: boolean;
  data: Record<string, unknown>;
  created_at: string;
}

// ── API Response ─────────────────────────────────────────
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
