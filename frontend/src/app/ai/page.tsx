"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Bot, Sparkles, Send, ShieldAlert, CheckCircle2, AlertTriangle, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AIAnalystPage() {
  const [tab, setTab] = useState<"market" | "concept">("market");
  const [question, setQuestion] = useState("¿Qué oportunidad de mercado existe en el género Roguelike y qué quejas comunes debemos evitar?");
  const [targetGenre, setTargetGenre] = useState("Action");
  const [concept, setConcept] = useState("Un juego de cartas táctico y supervivencia ambientado en una estación espacial desierta");
  const [conceptGenres, setConceptGenres] = useState("Strategy, Card Game, Sci-Fi");
  const [analysis, setAnalysis] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      if (tab === "market") {
        const res = await api.queryAI(question, targetGenre);
        setAnalysis(res);
      } else {
        const genresList = conceptGenres.split(",").map((g) => g.trim());
        const res = await api.validateConcept(concept, genresList);
        setAnalysis(res);
      }
    } catch (err: any) {
      setError(err.message || "Error al procesar consulta con la capa de IA");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Bot className="w-6 h-6 text-primary" />
              AI Market Analyst & Concept Validator
            </h1>
            <p className="text-sm text-muted-foreground">
              Investigación asistida con IA respaldada en telemetría determinista, sin inventar ventas privadas ni sufrir inyecciones.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-primary/10 border border-primary/30 text-primary px-3 py-1.5 rounded text-xs">
            <Sparkles className="w-4 h-4" />
            <span>Herramientas Tipadas · Cero Acceso SQL Arbitrario</span>
          </div>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex items-center gap-3 border-b border-border pb-3">
          <button
            onClick={() => { setTab("market"); setAnalysis(null); }}
            className={cn(
              "px-4 py-2 rounded text-xs font-bold transition-colors",
              tab === "market"
                ? "bg-primary text-primary-foreground shadow"
                : "text-gray-400 hover:text-white bg-card/60"
            )}
          >
            Análisis de Mercado y Competencia
          </button>
          <button
            onClick={() => { setTab("concept"); setAnalysis(null); }}
            className={cn(
              "px-4 py-2 rounded text-xs font-bold transition-colors",
              tab === "concept"
                ? "bg-primary text-primary-foreground shadow"
                : "text-gray-400 hover:text-white bg-card/60"
            )}
          >
            Validador de Concepto y Pitch
          </button>
        </div>

        {/* Input Form */}
        <div className="bg-card/70 border border-border p-6 rounded-lg space-y-4">
          {tab === "market" ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                    Pregunta de Investigación de Mercado:
                  </label>
                  <textarea
                    rows={3}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded p-3"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                    Segmento de Género:
                  </label>
                  <input
                    type="text"
                    value={targetGenre}
                    onChange={(e) => setTargetGenre(e.target.value)}
                    className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded p-3 mb-2"
                  />
                  <p className="text-[11px] text-gray-500">
                    Se consultarán rollups históricos y competidores de este género.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  Descripción o Pitch del Videojuego:
                </label>
                <textarea
                  rows={3}
                  value={concept}
                  onChange={(e) => setConcept(e.target.value)}
                  className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded p-3"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  Géneros y Mecánicas Previstas (separadas por coma):
                </label>
                <input
                  type="text"
                  value={conceptGenres}
                  onChange={(e) => setConceptGenres(e.target.value)}
                  className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded p-3"
                />
              </div>
            </div>
          )}

          <div className="flex justify-end pt-2">
            <button
              onClick={handleRunAnalysis}
              disabled={loading}
              className="px-5 py-2.5 bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-xs rounded flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              {loading ? "Sintetizando Evidencias..." : "Ejecutar Análisis"}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Structured Output Section */}
        {analysis && (
          <div className="space-y-6">
            {/* Header info */}
            <div className="bg-card/70 border border-border p-6 rounded-lg space-y-3">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-border pb-3">
                <h2 className="text-xl font-bold text-white">{analysis.title}</h2>
                <div className="flex items-center gap-2 text-[11px] text-gray-400">
                  <span className="font-mono bg-secondary/50 px-2 py-0.5 rounded text-gray-300">
                    {analysis.prompt_version}
                  </span>
                  <span>Corte: {analysis.data_cutoff?.slice(0, 10)}</span>
                </div>
              </div>
              <p className="text-sm text-gray-300">{analysis.summary}</p>
            </div>

            {/* Findings */}
            {analysis.findings?.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Layers className="w-4 h-4 text-primary" />
                  Hallazgos y Evidencias Observadas
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.findings.map((f: any, i: number) => (
                    <div key={i} className="bg-[#0b101c] border border-border p-4 rounded-lg space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-semibold text-primary uppercase text-[10px] tracking-wider">
                          {f.metric}
                        </span>
                        <span
                          className={cn(
                            "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                            f.confidence === "high"
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                              : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                          )}
                        >
                          Confianza: {f.confidence}
                        </span>
                      </div>
                      <p className="text-xs text-white leading-relaxed">{f.claim}</p>
                      <div className="text-[10px] text-gray-500 flex items-center gap-1">
                        <span>Fuente/Ref:</span>
                        <code className="text-gray-400">{f.evidence_refs?.join(", ")}</code>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations & Limitations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Recommendations */}
              <div className="bg-card/70 border border-border p-5 rounded-lg space-y-3">
                <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  Recomendaciones Tácticas
                </h3>
                <ul className="space-y-2 text-xs text-gray-300 list-disc list-inside">
                  {analysis.recommendations?.map((r: string, idx: number) => (
                    <li key={idx} className="leading-relaxed">{r}</li>
                  ))}
                </ul>
              </div>

              {/* Limitations */}
              <div className="bg-card/70 border border-border p-5 rounded-lg space-y-3">
                <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4" />
                  Limitaciones Metodológicas
                </h3>
                <ul className="space-y-2 text-xs text-gray-400 list-disc list-inside">
                  {analysis.limitations?.map((lim: string, idx: number) => (
                    <li key={idx} className="leading-relaxed">{lim}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
