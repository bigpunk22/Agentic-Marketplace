"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Zap, Building2, User, Check } from "lucide-react";

const steps = [
  { id: 1, title: "Create Account", icon: User },
  { id: 2, title: "Workspace", icon: Building2 },
  { id: 3, title: "Activate", icon: Zap },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(2);
  const [workspaceName, setWorkspaceName] = useState("");

  const handleComplete = () => {
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-accent-primary flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-text-primary">Agentic</span>
          </Link>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {steps.map((step, i) => (
            <div key={step.id} className="flex items-center gap-2">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step.id < currentStep
                    ? "bg-accent-success text-white"
                    : step.id === currentStep
                    ? "bg-accent-primary text-white"
                    : "bg-white/5 text-text-muted border border-border-subtle"
                }`}
              >
                {step.id < currentStep ? <Check className="w-4 h-4" /> : step.id}
              </div>
              {i < steps.length - 1 && (
                <div className={`w-12 h-0.5 ${step.id < currentStep ? "bg-accent-success" : "bg-border-subtle"}`} />
              )}
            </div>
          ))}
        </div>

        <div className="glass-card p-8">
          {currentStep === 2 && (
            <>
              <h2 className="text-xl font-bold text-text-primary text-center">
                Set up your workspace
              </h2>
              <p className="text-text-secondary text-center mt-2">
                A workspace is where your team manages workflows
              </p>
              <div className="mt-6">
                <label className="text-text-secondary text-sm mb-1.5 block">Workspace Name</label>
                <input
                  type="text"
                  value={workspaceName}
                  onChange={(e) => setWorkspaceName(e.target.value)}
                  placeholder="My Company"
                  className="glass-input"
                />
              </div>
              <button
                onClick={() => setCurrentStep(3)}
                className="glass-button w-full justify-center mt-6 py-3"
              >
                Continue
              </button>
            </>
          )}

          {currentStep === 3 && (
            <>
              <h2 className="text-xl font-bold text-text-primary text-center">
                Choose a workflow
              </h2>
              <p className="text-text-secondary text-center mt-2">
                Start with a template or skip for now
              </p>
              <div className="mt-6 grid grid-cols-2 gap-3">
                {[
                  { emoji: "📧", name: "Email Auto-Reply" },
                  { emoji: "📊", name: "Data Analysis" },
                  { emoji: "🤖", name: "Chat Bot" },
                  { emoji: "📝", name: "Content Gen" },
                ].map((tpl) => (
                  <button
                    key={tpl.name}
                    onClick={handleComplete}
                    className="p-4 rounded-xl glass hover:border-accent-primary/30 transition-colors text-center"
                  >
                    <span className="text-2xl">{tpl.emoji}</span>
                    <p className="text-text-primary text-sm mt-2">{tpl.name}</p>
                  </button>
                ))}
              </div>
              <button
                onClick={handleComplete}
                className="w-full mt-4 text-text-muted text-sm hover:text-text-secondary transition-colors"
              >
                Skip for now →
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
