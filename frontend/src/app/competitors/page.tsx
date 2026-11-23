"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api, GameSummaryItem } from "@/lib/api";
import { Users2, ArrowRightLeft, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function CompetitorsPage() {
  const [games, setGames] = useState<GameSummaryItem[]>([]);
  const [selectedGameA, setSelectedGameA] = useState<string>("");
  const [selectedGameB, setSelectedGameB] = useState<string>("");
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [comparison, setComparison] = useState<any | null>(null);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [loadingCompare, setLoadingCompare] = useState(false);
  const [linkMsg, setLinkMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadGames() {
      try {
        const res = await api.getGames({ limit: 100 });
        setGames(res.items || []);
        if (res.items?.length > 0) {
          setSelectedGameA(res.items[0].id);
          if (res.items.length > 1) {
            setSelectedGameB(res.items[1].id);
          }
        }
      } catch (err) {
        console.error(err);
      }
    }
    loadGames();
  }, []);

  useEffect(() => {
    if (!selectedGameA) return;
    async function fetchSuggestions() {
      setLoadingSuggestions(true);
      try {
        const data = await api.getCompetitorSuggestions(selectedGameA);
        setSuggestions(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingSuggestions(false);
      }
    }
    fetchSuggestions();
  }, [selectedGameA]);

  useEffect(() => {
    if (!selectedGameA || !selectedGameB || selectedGameA === selectedGameB) {
      setComparison(null);
      return;
    }
    async function runCompare() {
      setLoadingCompare(true);
      try {
        const data = await api.compareGames(selectedGameA, selectedGameB);
        setComparison(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingCompare(false);
      }
    }
    runCompare();
  }, [selectedGameA, selectedGameB]);

  const handleLink = async (competitorId: string, reason: string, score: number) => {
    try {
      await api.fetchWithAuth("/api/v1/competitors/link", {
        method: "POST",
        body: JSON.stringify({
          game_id: selectedGameA,
          competitor_game_id: competitorId,
          reason_type: reason,
          similarity_score: score,
        }),
      });
      setLinkMsg(`Competidor vinculado con éxito (${reason})`);
      setTimeout(() => setLinkMsg(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Page Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Users2 className="w-6 h-6 text-primary" />
              Competitor Analyzer & Head-to-Head
            </h1>
            <p className="text-sm text-muted-foreground">
              Selección algorítmica de competidores por solapamiento de tags/géneros y comparación métrica directa.
            </p>
          </div>
          {linkMsg && (
            <div className="flex items-center gap-2 text-xs bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1.5 rounded">
              <CheckCircle2 className="w-4 h-4" />
              {linkMsg}
            </div>
          )}
        </div>

        {/* Game Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-card/60 border border-border p-5 rounded-lg">
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Juego Base (Target)
            </label>
            <select
              value={selectedGameA}
              onChange={(e) => setSelectedGameA(e.target.value)}
              className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded px-3 py-2"
            >
              {games.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.canonical_name} ({g.steam_appid || "N/A"})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Juego Competidor a Comparar
            </label>
            <select
              value={selectedGameB}
              onChange={(e) => setSelectedGameB(e.target.value)}
              className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded px-3 py-2"
            >
              {games.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.canonical_name} ({g.steam_appid || "N/A"})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Head-to-Head Matrix */}
        {comparison && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <ArrowRightLeft className="w-5 h-5 text-primary" />
              Matriz Comparativa Directa
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Game A Card */}
              <div className="bg-card/70 border border-border p-5 rounded-lg space-y-4">
                <div className="border-b border-border pb-3">
                  <span className="text-[10px] uppercase font-bold text-primary tracking-wider">Target</span>
                  <h3 className="text-lg font-bold text-white">{comparison.game_a.name}</h3>
                  <p className="text-xs text-gray-400">Lanzamiento: {comparison.game_a.release_date || "N/A"}</p>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Precio USD:</span>
                    <span className="font-semibold text-white">
                      {comparison.game_a.is_free ? "Free to Play" : `$${comparison.game_a.price_usd || "N/A"}`}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Jugadores CCU:</span>
                    <span className="font-semibold text-white">{comparison.game_a.latest_ccu?.toLocaleString() || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Pico CCU Observado:</span>
                    <span className="font-semibold text-white">{comparison.game_a.peak_ccu?.toLocaleString() || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Total Reseñas:</span>
                    <span className="font-semibold text-white">{comparison.game_a.total_reviews?.toLocaleString() || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Ratio Positivo:</span>
                    <span className="font-semibold text-emerald-400">{comparison.game_a.positive_ratio ? `${comparison.game_a.positive_ratio}%` : "N/A"}</span>
                  </div>
                </div>
              </div>

              {/* Overlap & Delta Highlights */}
              <div className="bg-[#0f172a]/90 border border-primary/30 p-5 rounded-lg space-y-4">
                <div className="border-b border-border pb-3 text-center">
                  <span className="text-[10px] uppercase font-bold text-accent tracking-wider">Métricas de Solapamiento</span>
                  <div className="text-2xl font-black text-white mt-1">
                    {(comparison.comparison.tag_similarity_index * 100).toFixed(1)}%
                  </div>
                  <p className="text-[11px] text-gray-400">Índice Jaccard de Tags y Taxonomía</p>
                </div>
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-gray-400 font-medium">Diferencia de Precio:</span>
                    <p className="font-bold text-white text-sm">
                      {comparison.comparison.price_difference_usd > 0
                        ? `+$${comparison.comparison.price_difference_usd} (Más costoso)`
                        : `$${comparison.comparison.price_difference_usd} (Menor o igual)`}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400 font-medium">Diferencia de Ratio Positivo:</span>
                    <p className="font-bold text-white text-sm">
                      {comparison.comparison.positive_ratio_diff > 0
                        ? `+${comparison.comparison.positive_ratio_diff}%`
                        : `${comparison.comparison.positive_ratio_diff}%`}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400 font-medium block mb-1">Tags Compartidos:</span>
                    <div className="flex flex-wrap gap-1">
                      {comparison.comparison.shared_tags.map((t: string) => (
                        <span key={t} className="bg-primary/20 text-primary border border-primary/30 text-[10px] px-2 py-0.5 rounded">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Game B Card */}
              <div className="bg-card/70 border border-border p-5 rounded-lg space-y-4">
                <div className="border-b border-border pb-3">
                  <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Competidor</span>
                  <h3 className="text-lg font-bold text-white">{comparison.game_b.name}</h3>
                  <p className="text-xs text-gray-400">Lanzamiento: {comparison.game_b.release_date || "N/A"}</p>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Precio USD:</span>
                    <span className="font-semibold text-white">
                      {comparison.game_b.is_free ? "Free to Play" : `$${comparison.game_b.price_usd || "N/A"}`}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Jugadores CCU:</span>
                    <span className="font-semibold text-white">{comparison.game_b.latest_ccu?.toLocaleString() || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Pico CCU Observado:</span>
                    <span className="font-semibold text-white">{comparison.game_b.peak_ccu?.toLocaleString() || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Total Reseñas:</span>
                    <span className="font-semibold text-white">{comparison.game_b.total_reviews?.toLocaleString() || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-gray-400">Ratio Positivo:</span>
                    <span className="font-semibold text-emerald-400">{comparison.game_b.positive_ratio ? `${comparison.game_b.positive_ratio}%` : "N/A"}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Algorithmic Suggestions Table */}
        <div className="bg-card/60 border border-border rounded-lg p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              Competidores Sugeridos por Similitud de Contenido
            </h2>
            <span className="text-xs text-gray-400">{suggestions.length} competidores detectados</span>
          </div>

          {loadingSuggestions ? (
            <p className="text-xs text-gray-400 py-6 text-center">Calculando solapamiento de tags y mecánicas...</p>
          ) : suggestions.length === 0 ? (
            <p className="text-xs text-gray-500 py-6 text-center">No se encontraron suficientes juegos con taxonomías registradas.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0b101c] text-gray-400 uppercase tracking-wider border-b border-border">
                  <tr>
                    <th className="py-2.5 px-3">Juego Competidor</th>
                    <th className="py-2.5 px-3">Razón Principal</th>
                    <th className="py-2.5 px-3">Similitud Jaccard</th>
                    <th className="py-2.5 px-3">Tags en Común</th>
                    <th className="py-2.5 px-3 text-right">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {suggestions.map((s) => (
                    <tr key={s.game_id} className="hover:bg-card/80 transition-colors">
                      <td className="py-3 px-3 font-medium text-white">{s.name}</td>
                      <td className="py-3 px-3">
                        <span className="bg-secondary/40 text-gray-300 border border-border px-2 py-0.5 rounded text-[10px]">
                          {s.primary_reason}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-bold text-accent">{(s.similarity_score * 100).toFixed(1)}%</td>
                      <td className="py-3 px-3 text-gray-400">
                        {s.shared_taxonomy?.join(", ") || `${s.shared_tags_count} tags`}
                      </td>
                      <td className="py-3 px-3 text-right space-x-2">
                        <button
                          onClick={() => setSelectedGameB(s.game_id)}
                          className="px-2.5 py-1 bg-secondary hover:bg-secondary/80 text-white rounded text-[11px]"
                        >
                          Comparar
                        </button>
                        <button
                          onClick={() => handleLink(s.game_id, s.primary_reason, s.similarity_score)}
                          className="px-2.5 py-1 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/30 rounded text-[11px]"
                        >
                          Vincular
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
