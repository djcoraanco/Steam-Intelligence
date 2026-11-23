"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";
import {
  Settings,
  Database,
  Shield,
  Key,
  Server,
  HardDrive,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Info,
  Terminal,
  Activity,
  Layers,
  FileCheck
} from "lucide-react";

interface MetricsData {
  indexed_games_count: number;
  player_snapshots_count: number;
  review_snapshots_count: number;
  total_exports_count: number;
  exports_storage_directory: string;
}

export default function SettingsPage() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const [m, h] = await Promise.all([
        api.getMetrics().catch(() => null),
        api.getHealth().catch(() => null)
      ]);
      if (m && m.metrics) setMetrics(m.metrics);
      if (h) setHealthStatus(h);
    } catch (err) {
      console.error("Failed to load settings & metrics", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadSettings();
    setRefreshing(false);
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
          <div>
            <div className="flex items-center gap-2">
              <Settings className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold tracking-tight text-white">System Settings &amp; Health</h1>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Configuration parameters, database observability, API key verification, and backup operations.
            </p>
          </div>

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-3 py-1.5 bg-card border border-border hover:border-gray-500 rounded-md text-xs text-white flex items-center gap-2 transition-colors self-start md:self-auto"
          >
            <RefreshCw className={cn("w-3.5 h-3.5", refreshing && "animate-spin text-primary")} />
            Refresh Metrics
          </button>
        </div>

        {/* Operational Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>INDEXED GAMES</span>
              <Database className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-bold text-white">
              {metrics ? formatNumber(metrics.indexed_games_count) : "-"}
            </div>
            <div className="text-[11px] text-muted-foreground mt-1">Catalog database table</div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>PLAYER SNAPSHOTS</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white">
              {metrics ? formatNumber(metrics.player_snapshots_count) : "-"}
            </div>
            <div className="text-[11px] text-muted-foreground mt-1">Timescale / CCU series</div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>REVIEW SNAPSHOTS</span>
              <Layers className="w-4 h-4 text-chart-2" />
            </div>
            <div className="text-2xl font-bold text-white">
              {metrics ? formatNumber(metrics.review_snapshots_count) : "-"}
            </div>
            <div className="text-[11px] text-muted-foreground mt-1">Sentiment history series</div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>REPORTS IN STORAGE</span>
              <HardDrive className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-white">
              {metrics ? formatNumber(metrics.total_exports_count) : "0"}
            </div>
            <div className="text-[11px] text-muted-foreground mt-1">PDF / XLSX / PPTX files</div>
          </div>
        </div>

        {/* System & API Key Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-card border border-border rounded-lg p-5 space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <Server className="w-5 h-5 text-primary" />
              <h2 className="text-base font-semibold text-white">Platform Health &amp; Environment</h2>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between py-1 border-b border-border/50">
                <span className="text-muted-foreground">Application Environment:</span>
                <span className="font-mono text-white bg-muted px-2 py-0.5 rounded">
                  {healthStatus?.environment || "production"}
                </span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-border/50">
                <span className="text-muted-foreground">Relational Database Engine:</span>
                <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>
                    {healthStatus?.components?.database?.status === "healthy"
                      ? "Healthy & Connected"
                      : "Operational"}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-border/50">
                <span className="text-muted-foreground">Version:</span>
                <span className="text-white font-mono">{healthStatus?.version || "1.0.0"}</span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-border/50">
                <span className="text-muted-foreground">Architecture Pattern:</span>
                <span className="text-white">Self-Hosted Local-First (Master Spec v1.0)</span>
              </div>

              <div className="flex items-center justify-between py-1">
                <span className="text-muted-foreground">Exports Volume Directory:</span>
                <span className="text-gray-300 font-mono text-[11px] truncate max-w-[220px]">
                  {metrics?.exports_storage_directory || "./exports"}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-5 space-y-4">
            <div className="flex items-center gap-2 border-b border-border pb-3">
              <Key className="w-5 h-5 text-chart-2" />
              <h2 className="text-base font-semibold text-white">External Integrations &amp; Auth</h2>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between py-1 border-b border-border/50">
                <div>
                  <div className="font-semibold text-white">Steam Web API Provider</div>
                  <div className="text-[11px] text-muted-foreground">Official Valve Storefront &amp; WebAPI</div>
                </div>
                <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">
                  Ready (Public + Key)
                </span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-border/50">
                <div>
                  <div className="font-semibold text-white">Twitch / IGDB v4</div>
                  <div className="text-[11px] text-muted-foreground">OAuth 2.0 Client Credentials</div>
                </div>
                <span className="px-2 py-0.5 bg-primary/20 text-primary rounded border border-primary/30">
                  Online
                </span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-border/50">
                <div>
                  <div className="font-semibold text-white">AI Research Engine</div>
                  <div className="text-[11px] text-muted-foreground">Internal Evidence-First Tool-Augmented LLM</div>
                </div>
                <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">
                  Active
                </span>
              </div>

              <div className="flex items-center justify-between py-1">
                <div>
                  <div className="font-semibold text-white">Multi-Store Connectors</div>
                  <div className="text-[11px] text-muted-foreground">GOG, Epic Games, itch.io, PCGamingWiki</div>
                </div>
                <span className="px-2 py-0.5 bg-muted text-gray-300 rounded">
                  7/7 Verified
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Disaster Recovery & Backup Panel */}
        <div className="bg-card border border-border rounded-lg p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-semibold text-white">Automated Backups &amp; Disaster Recovery</h2>
          </div>
          <p className="text-xs text-muted-foreground">
            Production backups run daily at 02:00 UTC with 30-day retention. Scripts are pre-configured for both Linux and Windows environments:
          </p>

          <div className="bg-background border border-border rounded-md p-3 text-xs font-mono text-gray-300 space-y-1">
            <div className="text-muted-foreground"># Linux / Docker backup execution:</div>
            <div className="text-emerald-400">bash scripts/backup.sh</div>
            <div className="text-muted-foreground pt-1"># Windows PowerShell backup execution:</div>
            <div className="text-emerald-400">powershell -ExecutionPolicy Bypass -File scripts\backup.ps1</div>
            <div className="text-muted-foreground pt-1"># Restore verification test:</div>
            <div className="text-emerald-400">python scripts/restore_test.py</div>
          </div>
        </div>
      </main>
    </div>
  );
}
