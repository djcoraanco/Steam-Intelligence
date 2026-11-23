import React from "react";
import { cn } from "@/lib/utils";
import { Info } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  period?: string;
  source?: string;
  dataType?: "official" | "third_party" | "estimated" | "derived" | "synthetic";
  freshnessStatus?: "fresh" | "stale" | "unavailable" | "outdated";
  icon?: React.ReactNode;
}

export function MetricCard({
  title,
  value,
  subtitle,
  period = "Último corte",
  source = "Steam Intelligence",
  dataType = "derived",
  freshnessStatus = "fresh",
  icon,
}: MetricCardProps) {
  const getBadgeStyle = () => {
    switch (dataType) {
      case "official":
        return "bg-sky-950/80 text-sky-400 border-sky-800";
      case "estimated":
        return "bg-amber-950/80 text-amber-400 border-amber-800";
      case "third_party":
        return "bg-purple-950/80 text-purple-400 border-purple-800";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-4 flex flex-col justify-between hover:border-gray-700 transition">
      <div className="flex items-center justify-between text-muted-foreground mb-2">
        <span className="text-xs font-medium text-gray-400 flex items-center gap-1.5">
          {icon}
          {title}
        </span>
        <span className={cn("text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded border", getBadgeStyle())}>
          {dataType}
        </span>
      </div>

      <div className="my-1">
        <div className="text-2xl font-bold tracking-tight text-white">{value}</div>
        {subtitle && <div className="text-xs text-muted-foreground mt-0.5">{subtitle}</div>}
      </div>

      <div className="mt-3 pt-2 border-t border-border/60 flex items-center justify-between text-[10px] text-gray-500">
        <span>{period}</span>
        <span className="flex items-center gap-1 text-gray-400">
          <Info className="w-2.5 h-2.5" />
          {source}
        </span>
      </div>
    </div>
  );
}
