/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // ── Base ──────────────────────────────────────
        bg: {
          primary: "#0A0A0F",
          secondary: "#12121A",
          tertiary: "#1A1A2E",
        },
        // ── Accents ───────────────────────────────────
        accent: {
          primary: "#8B5CF6",
          secondary: "#06B6D4",
          success: "#10B981",
          warning: "#F59E0B",
          danger: "#EF4444",
        },
        // ── Text ──────────────────────────────────────
        text: {
          primary: "#F0F0F5",
          secondary: "#8B8B9E",
          muted: "#5A5A6E",
        },
        // ── Borders ───────────────────────────────────
        border: {
          subtle: "rgba(255,255,255,0.08)",
          accent: "rgba(139,92,246,0.5)",
          focus: "rgba(139,92,246,0.8)",
        },
      },
      backdropBlur: {
        glass: "12px",
        "glass-lg": "20px",
      },
      boxShadow: {
        glow: "0 0 20px rgba(139,92,246,0.3)",
        "glow-lg": "0 0 40px rgba(139,92,246,0.4)",
        "glow-cyan": "0 0 20px rgba(6,182,212,0.3)",
        card: "0 4px 24px rgba(0,0,0,0.4)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "slide-up": "slide-up 0.3s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
        shimmer: "shimmer 2s linear infinite",
      },
      keyframes: {
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(139,92,246,0.3)" },
          "50%": { boxShadow: "0 0 40px rgba(139,92,246,0.6)" },
        },
        "slide-up": {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        sm: "8px",
        md: "12px",
        lg: "16px",
        xl: "24px",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
};
