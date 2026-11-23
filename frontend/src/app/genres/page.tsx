"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { cn, formatNumber, formatPrice } from "@/lib/utils";
import {
  Shapes,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Layers,
  PieChart,
  ShieldCheck,
  CheckCircle2
} from "lucide-react";

interface SegmentRollupItem {
  segment_type: string;
  segment_key: { genre_id?: string; canonical_name?: string };
  period_start: string;
  game_count: number;
  active_game_count: number;
  player_sum: number | null;
  median_price_minor: number | null;
  new_release_count: number;
  top_game_concentration: number | null;
  data_coverage: number;
  calculation_version: string;
}

export default function GenresPage() {
  const [rollups, setRollups] = useState<SegmentRollupItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [computing, setComputing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadRollups();
  }, []);

  const loadRollups = () => {
    setLoading(true);
    api
      .getSegmentRollups("genre")
      .then((data) => {
        setRollups(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleComputeRollups = async () => {
    setComputing(true);
    setMessage(null);
    try {
      const res = await api.computeRollups();
      setMessage(`Cálculo de rollups completado: ${res.segments_computed} segmentos analizados.`);
      loadRollups();
    } catch (err: any) {
      setMessage(`Error en el cálculo: ${err.message}`);
    } finally {
      setComputing(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="Genre Analytics · Agregados y Rollups de Segmentos de Mercado" />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Metric Rules / Explainability Banner (Section 7.2) */}
        <div className="bg-card border border-border rounded-xl p-5 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-sky-950/80 border border-sky-800 text-sky-400 flex items-center justify-center">
                <Shapes className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-semibold text-sm text-white">Analítica por Segmento (Rollups Deterministas)</h2>
                <p className="text-xs text-muted-foreground">
                  Cálculo de medianas de precio, títulos activos y concentración de actividad (Sección 7.2).
                </p>
              </div>
            </div>

            <button
              onClick={handleComputeRollups}
              disabled={computing}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-xs font-medium transition disabled:opacity-50 shrink-0"
            >
              <RefreshCw className={cn("w-3.5 h-3.5", computing && "animate-spin")} />
              <span>{computing ? "Calculando rollups..." : "Recalcular Rollups"}</span>
            </button>
          </div>

          <div className="text-xs text-gray-400 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-border/80">
            <span className="font-semibold text-cyan-300">Regla de no-suma global: </span>
            No se suman jugadores entre diferentes juegos como si fueran usuarios únicos (una misma persona puede jugar varios títulos). Se evalúa la mediana de jugadores y la concentración en el título dominante (% Top 1).
          </div>

          {message && (
            <div className="p-2.5 rounded-lg bg-sky-950/60 border border-sky-800 text-sky-200 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0" />
              <span>{message}</span>
            </div>
          )}
        </div>

        {/* Segments Table */}
        <div className="bg-card border border-border rounded-xl p-5 space-y-4">
          <h3 className="font-semibold text-xs text-white uppercase tracking-wider">
            Segmentos de Mercado Observados ({rollups.length})
          </h3>

          {loading ? (
            <div className="py-20 text-center text-xs text-muted-foreground animate-pulse">
              Cargando rollups de mercado...
            </div>
          ) : rollups.length === 0 ? (
            <div className="py-16 text-center text-xs text-gray-500">
              No hay rollups calculados todavía. Presiona "Recalcular Rollups".
            </div>
          ) : (
            <div className="overflow-x-auto border border-border/80 rounded-lg">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 border-b border-border text-gray-400 text-[10px] uppercase">
                  <tr>
                    <th className="py-3 px-3.5 font-medium">Género / Segmento</th>
                    <th className="py-3 px-3.5 font-medium text-right">Catálogo</th>
                    <th className="py-3 px-3.5 font-medium text-right">Activos</th>
                    <th className="py-3 px-3.5 font-medium text-right">Mediana Precio</th>
                    <th className="py-3 px-3.5 font-medium text-right">Concentración (Top 1)</th>
                    <th className="py-3 px-3.5 font-medium text-right">Nuevos (60d)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40">
                  {rollups.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="py-3 px-3.5 font-medium text-white flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-primary" />
                        <span>{r.segment_key.canonical_name || "Sin Nombre"}</span>
                      </td>
                      <td className="py-3 px-3.5 text-right font-mono text-gray-300">
                        {formatNumber(r.game_count)}
                      </td>
                      <td className="py-3 px-3.5 text-right font-mono text-emerald-400 font-semibold">
                        {formatNumber(r.active_game_count)}
                      </td>
                      <td className="py-3 px-3.5 text-right font-mono text-cyan-300 font-medium">
                        {r.median_price_minor !== null ? formatPrice(r.median_price_minor) : "—"}
                      </td>
                      <td className="py-3 px-3.5 text-right font-mono">
                        {r.top_game_concentration !== null ? (
                          <span className={cn(
                            "px-1.5 py-0.5 rounded text-[10px] font-semibold",
                            r.top_game_concentration > 0.8
                              ? "bg-amber-950 text-amber-400 border border-amber-800"
                              : "bg-slate-800 text-gray-300"
                          )}>
                            {(r.top_game_concentration * 100).toFixed(1)}%
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="py-3 px-3.5 text-right font-mono text-gray-400">
                        +{r.new_release_count}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
