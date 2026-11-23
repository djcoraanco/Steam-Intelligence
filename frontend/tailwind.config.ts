import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0b0f19",
        card: "#111827",
        border: "#1f2937",
        primary: {
          DEFAULT: "#0284c7",
          foreground: "#ffffff",
          dark: "#0369a1",
        },
        accent: {
          DEFAULT: "#06b6d4",
          foreground: "#083344",
        },
        muted: {
          DEFAULT: "#6b7280",
          foreground: "#9ca3af",
        }
      },
    },
  },
  plugins: [],
};
export default config;
