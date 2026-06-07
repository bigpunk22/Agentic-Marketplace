import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "danger" | "info";
  className?: string;
}

const variantStyles = {
  default: "bg-white/5 border-white/10 text-text-secondary",
  success: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
  warning: "bg-amber-500/10 border-amber-500/30 text-amber-400",
  danger: "bg-red-500/10 border-red-500/30 text-red-400",
  info: "bg-cyan-500/10 border-cyan-500/30 text-cyan-400",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
