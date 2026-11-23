"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/Header";
import { MetricCard } from "@/components/MetricCard";
import { api, DashboardOverview } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import {
  Gamepad2,
  Eye,
  Database,
  Crosshair,
  TrendingUp,
  Clock,
  Layers,
  ArrowUpRight,
  ShieldAlert,
} from "lucide-react";

export default function OverviewPage() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getOverview()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="flex-1 flex flex-col">
      <Header title="Overview · Estado del Mercado PC" />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Compliance Banner */}
        <div className="bg-sky-950/30 border border-sky-800/60 rounded-lg p-3.5 flex items-start gap-3 text-xs text-sky-200">
          <ShieldAlert className="w-4 h-4 text-sky-400 mt-0.5 shrink-0" />
          <div className="leading-relaxed">
            <span className="font-semibold text-sky-300">Principio de Trazabilidad y Confianza: </span>
            Steam Intelligence distingue datos oficiales de la plataforma, estimaciones externas y métricas derivadas. No se infieren ventas ni ingresos netos privados. Toda conclusión se respalda en snapshots históricos fechados.
          </div>
        </div>

        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Catálogo Indexado"
            value={loading ? "..." : formatNumber(data?.indexed_games_count ?? 0)}
            subtitle="Juegos registrados en base de datos"
            icon={<Gamepad2 className="w-3.5 h-3.5 text-primary" />}
            dataType="official"
            source="Steamworks IStoreService"
            period="Diario incremental"
          />
          <MetricCard
            title="Juegos Monitorizados"
            value={loading ? "..." : formatNumber(data?.monitored_games_count ?? 0)}
            subtitle="Seguimiento activo de snapshots"
            icon={<Eye className="w-3.5 h-3.5 text-emerald-400" />}
            dataType="derived"
            source="Watchlist de Sistema"
            period="Cada 15-30 min"
          />
          <MetricCard
            title="Fuentes de Datos"
            value={loading ? "..." : `${data?.active_sources_count ?? 1} Conectores`}
            subtitle="Steam Store / Steamworks Web API"
            icon={<Database className="w-3.5 h-3.5 text-cyan-400" />}
            dataType="official"
            source="Registry de Conectores"
            period="Continuo"
          />
          <MetricCard
            title="Nichos Identificados"
            value={loading ? "..." : formatNumber(data?.detected_niches_count ?? 0)}
            subtitle="Segmentos con score de oportunidad"
            icon={<Crosshair className="w-3.5 h-3.5 text-amber-400" />}
            dataType="derived"
            source="Niche Finder Algorithm"
            period="Semanal"
          />
        </div>

        {/* Main Content: Top Games & Rising Categories */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top Games Section */}
          <div className="lg:col-span-2 bg-card border border-border rounded-lg p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-sm text-white">Actividad Reciente por Título</h3>
                <p className="text-xs text-muted-foreground">Últimos snapshots observables de concurrentes</p>
              </div>
              <Link
                href="/games"
                className="text-xs text-primary hover:text-sky-300 flex items-center gap-1 font-medium transition"
              >
                Ver todos <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {loading ? (
              <div className="py-12 text-center text-xs text-muted-foreground animate-pulse">
                Cargando métricas de juegos...
              </div>
            ) : data?.top_games && data.top_games.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-border/80 text-gray-400 uppercase text-[10px]">
                    <tr>
                      <th className="pb-2.5 font-medium">Juego</th>
                      <th className="pb-2.5 font-medium">AppID</th>
                      <th className="pb-2.5 font-medium text-right">Jugadores (CCU)</th>
                      <th className="pb-2.5 font-medium text-right">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40">
                    {data.top_games.map((game) => (
                      <tr key={game.game_id} className="hover:bg-slate-800/40">
                        <td className="py-2.5 font-medium text-white flex items-center gap-2">
                          {game.cover_image_url ? (
                            <img
                              src={game.cover_image_url}
                              alt=""
                              className="w-7 h-4 object-cover rounded bg-slate-800"
                            />
                          ) : (
                            <div className="w-7 h-4 rounded bg-slate-800" />
                          )}
                          <span>{game.canonical_name}</span>
                        </td>
                        <td className="py-2.5 text-gray-400 font-mono text-[11px]">
                          {game.steam_appid || "—"}
                        </td>
                        <td className="py-2.5 text-right font-mono font-medium text-cyan-300">
                          {game.current_players ? formatNumber(game.current_players) : "Sin datos"}
                        </td>
                        <td className="py-2.5 text-right">
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-400 font-medium">
                            {game.availability_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-gray-400">
                Aún no hay juegos sincronizados. Inicia la sincronización de catálogo desde{" "}
                <Link href="/sources" className="text-primary underline">
                  Data Sources
                </Link>
                .
              </div>
            )}
          </div>

          {/* Right Column: Rising Genres & Connectors */}
          <div className="space-y-6">
            {/* Rising Genres */}
            <div className="bg-card border border-border rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-sm text-white flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  Géneros en Crecimiento
                </h3>
              </div>
              <p className="text-xs text-muted-foreground mb-4">
                Variación mensual de actividad observada
              </p>

              <div className="space-y-3">
                {data?.rising_genres.map((g, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-md bg-slate-900/60 border border-border/80 flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-medium text-gray-200">{g.genre}</div>
                      <div className="text-[10px] text-muted-foreground">{g.active_games} juegos activos</div>
                    </div>
                    <div className="text-right">
                      <span className="text-emerald-400 font-semibold font-mono">+{g.growth_pct}%</span>
                      <div className="text-[9px] text-gray-500 uppercase">MoM</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Status */}
            <div className="bg-card border border-border rounded-lg p-5">
              <h3 className="font-semibold text-sm text-white mb-2 flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                Frescura y Políticas
              </h3>
              <div className="text-xs text-gray-400 space-y-2.5 mt-3">
                <div className="flex justify-between items-center py-1 border-b border-border/50">
                  <span>Conector Principal</span>
                  <span className="font-semibold text-white">Steam Store (Activo)</span>
                </div>
                <div className="flex justify-between items-center py-1 border-b border-border/50">
                  <span>Última Medición</span>
                  <span className="text-emerald-400 font-mono">
                    {data?.latest_observation_at
                      ? new Date(data.latest_observation_at).toLocaleTimeString()
                      : "Al inicio"}
                  </span>
                </div>
                <div className="flex justify-between items-center py-1">
                  <span>Modo de Operación</span>
                  <span className="text-gray-300">Mixto (Manual + Auto)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
