import Link from "next/link";
import { Zap, ArrowRight, Shield, Globe, Layers } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      {/* ── Navbar ────────────────────────────────────────── */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border-subtle">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent-primary flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-text-primary">Agentic</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-text-secondary hover:text-text-primary transition-colors text-sm"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="glass-button text-sm"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────── */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6">
            <span className="w-2 h-2 rounded-full bg-accent-success animate-pulse" />
            <span className="text-text-secondary text-sm">Now in Beta — Join 1,000+ teams</span>
          </div>
          <h1 className="text-5xl sm:text-6xl font-bold text-text-primary leading-tight">
            AI Workflows
            <br />
            <span className="neon-text">Deployed in Seconds</span>
          </h1>
          <p className="text-text-secondary text-lg mt-6 max-w-2xl mx-auto">
            Browse, buy, and deploy AI agents and automations from the marketplace.
            No engineering required. Enterprise-grade infrastructure included.
          </p>
          <div className="flex items-center justify-center gap-4 mt-8">
            <Link
              href="/register"
              className="glass-button flex items-center gap-2 text-base px-6 py-3"
            >
              Start Free <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/marketplace"
              className="text-text-secondary hover:text-text-primary transition-colors text-base px-6 py-3"
            >
              Browse Marketplace
            </Link>
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-text-primary text-center mb-12">
            Everything you need to automate with AI
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: Zap,
                title: "One-Click Deploy",
                desc: "Browse the marketplace and deploy AI workflows instantly. No code required.",
                color: "text-accent-primary",
              },
              {
                icon: Shield,
                title: "Enterprise Security",
                desc: "SOC 2 compliant. End-to-end encryption. RBAC. SSO. Audit logs.",
                color: "text-accent-secondary",
              },
              {
                icon: Globe,
                title: "Multi-Tenant",
                desc: "Isolated workspaces for every team. Shared infrastructure, separate data.",
                color: "text-accent-success",
              },
              {
                icon: Layers,
                title: "AI Marketplace",
                desc: "Buy and sell AI workflows. Creator payouts. Revenue analytics.",
                color: "text-accent-warning",
              },
            ].map((feature) => (
              <div key={feature.title} className="glass-card p-6 glass-card-hover">
                <div className={`w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4`}>
                  <feature.icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <h3 className="text-text-primary font-semibold text-lg">{feature.title}</h3>
                <p className="text-text-secondary mt-2">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center glass-card p-12 glow">
          <h2 className="text-3xl font-bold text-text-primary">
            Ready to automate your business?
          </h2>
          <p className="text-text-secondary mt-4">
            Start free. No credit card required.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 glass-button mt-6 text-base px-8 py-3"
          >
            Get Started Free <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────── */}
      <footer className="border-t border-border-subtle py-8 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-accent-primary" />
            <span className="text-text-secondary text-sm">Agentic Marketplace</span>
          </div>
          <p className="text-text-muted text-sm">© 2026 Agentic Marketplace. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
