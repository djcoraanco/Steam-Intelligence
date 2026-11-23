"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api, GameSummaryItem } from "@/lib/api";
import { MessageSquareText, ThumbsUp, ThumbsDown, ShieldCheck, Quote, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ReviewMiningPage() {
  const [games, setGames] = useState<GameSummaryItem[]>([]);
  const [selectedGame, setSelectedGame] = useState<string>("");
  const [miningResult, setMiningResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadGames() {
      try {
        const res = await api.getGames({ limit: 100 });
        setGames(res.items || []);
        if (res.items?.length > 0) {
          setSelectedGame(res.items[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    }
    loadGames();
  }, []);

  useEffect(() => {
    if (!selectedGame) return;
    async function fetchMining() {
      setLoading(true);
      try {
        const data = await api.getReviewsMining(selectedGame);
        setMiningResult(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchMining();
  }, [selectedGame]);

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Title & Methodology Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <MessageSquareText className="w-6 h-6 text-primary" />
              Review Mining & Sentiment Taxonomy
            </h1>
            <p className="text-sm text-muted-foreground">
              Extracción cuantitativa de quejas y elogios en 15 tópicos canónicos, con trazabilidad de citas y denominador riguroso.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-blue-500/10 border border-blue-500/30 text-blue-400 px-3 py-1.5 rounded text-xs">
            <ShieldCheck className="w-4 h-4" />
            <span>Anti-Prompt Injection & Denominador Explícito</span>
          </div>
        </div>

        {/* Game Selector */}
        <div className="bg-card/60 border border-border p-5 rounded-lg flex flex-col md:flex-row items-center gap-4">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider min-w-[120px]">
            Seleccionar Juego:
          </label>
          <select
            value={selectedGame}
            onChange={(e) => setSelectedGame(e.target.value)}
            className="flex-1 bg-[#0a0f1d] border border-border text-white text-sm rounded px-3 py-2"
          >
            {games.map((g) => (
              <option key={g.id} value={g.id}>
                {g.canonical_name} ({g.total_reviews?.toLocaleString() || 0} reseñas observadas)
              </option>
            ))}
          </select>
        </div>

        {/* Mining Content */}
        {loading ? (
          <div className="p-12 text-center text-sm text-gray-400 bg-card/40 border border-border rounded-lg">
            Procesando y clasificando reseñas públicas observadas...
          </div>
        ) : !miningResult || miningResult.topics_breakdown?.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400 bg-card/40 border border-border rounded-lg">
            <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto mb-2" />
            No hay suficientes reseñas registradas en la base de datos para este juego.
            <p className="text-xs text-gray-500 mt-1">
              Ejecuta una sincronización de reseñas desde el catálogo o agrega snapshots.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Overview Stats Bar */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-card/70 border border-border p-4 rounded-lg">
                <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Muestra de Reseñas</span>
                <span className="text-2xl font-bold text-white">{miningResult.sample_size}</span>
                <span className="text-xs text-gray-500 block">Denominador total</span>
              </div>
              <div className="bg-card/70 border border-border p-4 rounded-lg">
                <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Tópicos Detectados</span>
                <span className="text-2xl font-bold text-primary">{miningResult.topics_count}</span>
                <span className="text-xs text-gray-500 block">De 15 categorías canónicas</span>
              </div>
              <div className="bg-card/70 border border-border p-4 rounded-lg">
                <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Garantía Metodológica</span>
                <p className="text-[11px] text-emerald-400 font-medium mt-1">
                  Sin afirmaciones de prevalencia sin denominador.
                </p>
              </div>
            </div>

            {/* Disclaimer box */}
            <div className="bg-primary/5 border border-primary/20 p-3 rounded text-xs text-gray-300">
              <span className="font-semibold text-primary">Nota de Evidencia: </span>
              {miningResult.disclaimer}
            </div>

            {/* Topics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {miningResult.topics_breakdown.map((t: any) => (
                <div key={t.topic} className="bg-card/70 border border-border rounded-lg p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-border pb-3">
                    <div>
                      <h3 className="font-bold text-white text-base capitalize">{t.topic.replace("/", " & ")}</h3>
                      <span className="text-xs text-gray-400">
                        {t.mentions_count} de {t.sample_denominator} reseñas ({t.prevalence_percent}%)
                      </span>
                    </div>
                    <span className="bg-primary/20 text-primary border border-primary/30 text-xs px-2.5 py-1 rounded font-bold">
                      {t.prevalence_percent}%
                    </span>
                  </div>

                  {/* Praise vs Complaint Bar */}
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="flex items-center gap-1 text-emerald-400">
                        <ThumbsUp className="w-3.5 h-3.5" /> Elogios: {t.praises_count} ({t.praise_ratio}%)
                      </span>
                      <span className="flex items-center gap-1 text-rose-400">
                        <ThumbsDown className="w-3.5 h-3.5" /> Quejas: {t.complaints_count} ({t.complaint_ratio}%)
                      </span>
                    </div>
                    <div className="h-2 w-full bg-rose-950/60 rounded-full overflow-hidden flex">
                      <div
                        className="bg-emerald-500 h-full transition-all"
                        style={{ width: `${t.praise_ratio}%` }}
                      />
                      <div
                        className="bg-rose-500 h-full transition-all"
                        style={{ width: `${t.complaint_ratio}%` }}
                      />
                    </div>
                  </div>

                  {/* Evidence Citations */}
                  <div className="space-y-2">
                    <span className="text-[11px] uppercase font-semibold text-gray-400 tracking-wider flex items-center gap-1">
                      <Quote className="w-3 h-3 text-primary" /> Evidencia Citada:
                    </span>
                    {t.citations.map((c: any, i: number) => (
                      <div key={i} className="bg-[#0b101c] border border-border/70 p-3 rounded text-xs space-y-1">
                        <div className="flex justify-between text-[10px] text-gray-500">
                          <span>Review ID: {c.source_review_id}</span>
                          <span
                            className={cn(
                              "font-bold uppercase",
                              c.sentiment === "positive" ? "text-emerald-400" : "text-rose-400"
                            )}
                          >
                            {c.sentiment}
                          </span>
                        </div>
                        <p className="text-gray-300 italic">&ldquo;{c.excerpt}&rdquo;</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
