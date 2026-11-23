"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Compass,
  TrendingUp,
  Shapes,
  Crosshair,
  Gamepad2,
  Users2,
  Activity,
  CalendarDays,
  CalendarCheck2,
  Sparkles,
  FlaskConical,
  Bot,
  FileSpreadsheet,
  Database,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Market Explorer", href: "/market", icon: Compass },
  { name: "Trending", href: "/trending", icon: TrendingUp },
  { name: "Genre Analytics", href: "/genres", icon: Shapes },
  { name: "Niche Finder", href: "/niches", icon: Crosshair },
  { name: "Game Explorer", href: "/games", icon: Gamepad2 },
  { name: "Competitor Analyzer", href: "/competitors", icon: Users2 },
  { name: "Player Analytics", href: "/players", icon: Activity },
  { name: "Seasonality", href: "/seasonality", icon: CalendarDays },
  { name: "Release Calendar", href: "/releases", icon: CalendarCheck2 },
  { name: "Store Optimizer", href: "/optimizer", icon: Sparkles },
  { name: "Research Center", href: "/research", icon: FlaskConical },
  { name: "AI Analyst", href: "/ai", icon: Bot },
  { name: "Reports", href: "/reports", icon: FileSpreadsheet },
  { name: "Data Sources", href: "/sources", icon: Database },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border bg-[#0e1422] flex flex-col h-screen select-none">
      <div className="p-5 border-b border-border flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-primary/20 border border-primary/40 flex items-center justify-center text-primary font-bold text-lg">
          SI
        </div>
        <div>
          <h1 className="font-semibold text-sm tracking-wide text-white">STEAM INTELLIGENCE</h1>
          <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Market Platform</p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors",
                isActive
                  ? "bg-primary/15 text-primary border border-primary/30"
                  : "text-gray-400 hover:text-white hover:bg-card/60"
              )}
            >
              <Icon className={cn("w-4 h-4", isActive ? "text-primary" : "text-gray-400")} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border text-[11px] text-gray-500 text-center">
        v1.0 · Self-Hosted Local-First
      </div>
    </aside>
  );
}
