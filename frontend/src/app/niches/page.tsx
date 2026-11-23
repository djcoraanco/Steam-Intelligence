"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import {
  Crosshair,
  RefreshCw,
  TrendingUp,
  ShieldAlert,
  Flame,
  Award,
  BarChart3,
  Layers,
  ArrowRight,
  Info
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NicheItem {
  id: string;
  name: string;
  description: string;
  demand_score: number;
  growth_score: number;
  competitive_space_score: number;
  commercial_feasibility_score: number;
  evidence_quality_score: number;
  opportunity_score: number;
  score_version: string;
  confidence_band: "low" | "medium" | "high";
  limitations: string[];
}

export default function NichesPage() {
  const [niches, setNiches] = useState<NicheItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedConfidence, setSelectedConfidence] = useState<string>("");

  useEffect(() => {
    loadNiches();
  }, [selectedConfidence]);

  const loadNiches = () => {
    setLoading(true);
    api
      .getNiches({ confidence: selectedConfidence || undefined })
      .then((data) => {
        setNiches(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    try {
      await api.runNicheAnalysis();
      loadNiches();
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const getConfidenceBadge = (band: string) => {
    switch (band) {
      case "high":
        return "bg-emerald-950/80 text-emerald-400 border-emerald-800";
      case "medium":
        return "bg-amber-950/80 text-amber-400 border-amber-800";
      default:
        return "bg-slate-800 text-gray-400 border-slate-700";
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="Niche Finder · Detección y Scoring de Oportunidades" />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Method / Formula Banner (Section 8) */}
        <div className="bg-card border border-border rounded-xl p-5 space-y-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center">
                <Crosshair className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-semibold text-sm text-white">Algoritmo Niche Opportunity Score (v1.0)</h2>
                <p className="text-xs text-muted-foreground">
                  Fórmula determinista basada en evidencia y trazabilidad observable (Sección 8.2).
                </p>
              </div>
            </div>

            <button
              onClick={handleRunAnalysis}
              disabled={analyzing}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-xs font-medium transition disabled:opacity-50 shrink-0"
            >
              <RefreshCw className={cn("w-3.5 h-3.5", analyzing && "animate-spin")} />
              <span>{analyzing ? "Evaluando nichos..." : "Recalcular Nichos"}</span>
            </button>
          </div>

          <div className="p-3 bg-slate-900/60 rounded-lg border border-border/80 font-mono text-[11px] text-cyan-300 flex flex-wrap gap-x-4 gap-y-1">
            <span>Opportunity =</span>
            <span>0.30 × Demand</span>
            <span>+ 0.25 × Growth</span>
            <span>+ 0.20 × CompetitiveSpace</span>
            <span>+ 0.15 × CommercialFeasibility</span>
            <span>+ 0.10 × EvidenceQuality</span>
          </div>
        </div>

        {/* Filter bar */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="text-gray-400">Filtrar por confianza:</span>
            <select
              value={selectedConfidence}
              onChange={(e) => setSelectedConfidence(e.target.value)}
              className="bg-card border border-border rounded-md px-2.5 py-1 text-white focus:outline-none focus:border-primary text-xs"
            >
              <option value="">Todas las bandas</option>
              <option value="high">Alta (High Confidence)</option>
              <option value="medium">Media (Medium Confidence)</option>
              <option value="low">Baja (Low Confidence)</option>
            </select>
          </div>

          <div className="text-gray-400">
            Total oportunidades detectadas: <span className="text-white font-semibold">{niches.length}</span>
          </div>
        </div>

        {/* Niches List */}
        {loading ? (
          <div className="py-20 text-center text-xs text-muted-foreground animate-pulse">
            Calculando y ordenando ranking de nichos...
          </div>
        ) : niches.length === 0 ? (
          <div className="py-20 text-center text-xs text-gray-400 bg-card border border-border rounded-lg p-8">
            <Crosshair className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <div className="text-sm font-semibold text-white mb-1">No hay nichos analizados aún</div>
            <p className="max-w-md mx-auto text-muted-foreground mb-4">
              Presiona el botón superior "Recalcular Nichos" para ejecutar el algoritmo sobre los datos observados.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {niches.map((niche, idx) => (
              <div
                key={niche.id}
                className="bg-card border border-border rounded-xl p-5 space-y-4 hover:border-gray-600 transition"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="w-7 h-7 rounded-full bg-slate-800 text-gray-300 font-bold text-xs flex items-center justify-center font-mono">
                      #{idx + 1}
                    </span>
                    <div>
                      <h3 className="font-semibold text-sm text-white flex items-center gap-2">
                        {niche.name}
                        <span
                          className={cn(
                            "text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded border",
                            getConfidenceBadge(niche.confidence_band)
                          )}
                        >
                          Confianza {niche.confidence_band}
                        </span>
                      </h3>
                      <p className="text-xs text-muted-foreground">{niche.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    <div className="text-right">
                      <div className="text-[10px] text-gray-500 uppercase font-semibold">Opportunity Score</div>
                      <div className="text-2xl font-black font-mono text-cyan-300">
                        {niche.opportunity_score} <span className="text-xs font-normal text-gray-500">/ 100</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Score Breakdown Bars (Section 8.2) */}
                <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 pt-3 border-t border-border/60 text-xs">
                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-gray-400">Demanda (30%)</span>
                      <span className="font-mono text-white font-semibold">{niche.demand_score}</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-sky-500 rounded-full" style={{ width: `${niche.demand_score}%` }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-gray-400">Crecimiento (25%)</span>
                      <span className="font-mono text-white font-semibold">{niche.growth_score}</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${niche.growth_score}%` }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-gray-400">Espacio Comp. (20%)</span>
                      <span className="font-mono text-white font-semibold">{niche.competitive_space_score}</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${niche.competitive_space_score}%` }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-gray-400">Viabilidad Com. (15%)</span>
                      <span className="font-mono text-white font-semibold">{niche.commercial_feasibility_score}</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500 rounded-full" style={{ width: `${niche.commercial_feasibility_score}%` }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-gray-400">Evidencia (10%)</span>
                      <span className="font-mono text-white font-semibold">{niche.evidence_quality_score}</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-amber-500 rounded-full" style={{ width: `${niche.evidence_quality_score}%` }} />
                    </div>
                  </div>
                </div>

                {/* Limitations and caveats */}
                {niche.limitations && niche.limitations.length > 0 && (
                  <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300 flex items-start gap-2">
                    <ShieldAlert className="w-3.5 h-3.5 shrink-0 mt-0.5 text-amber-400" />
                    <div>
                      <span className="font-semibold">Limitaciones de Muestra: </span>
                      {niche.limitations.join(" ")}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
