"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { CalendarDays, AlertTriangle, ShieldCheck, CheckCircle2, Flame, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

export default function SeasonalityPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [targetDate, setTargetDate] = useState<string>("2026-10-15");
  const [daysWindow, setDaysWindow] = useState<number>(14);
  const [collisionResult, setCollisionResult] = useState<any | null>(null);
  const [cohorts, setCohorts] = useState<any | null>(null);
  const [loadingCollision, setLoadingCollision] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [evData, cohortData] = await Promise.all([
          api.getIndustryEvents(),
          api.getCohorts("release_year"),
        ]);
        setEvents(evData);
        setCohorts(cohortData);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    if (!targetDate) return;
    async function runCollision() {
      setLoadingCollision(true);
      try {
        const data = await api.analyzeLaunchCollision(targetDate, daysWindow);
        setCollisionResult(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingCollision(false);
      }
    }
    runCollision();
  }, [targetDate, daysWindow]);

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <CalendarDays className="w-6 h-6 text-primary" />
              Seasonality & Launch Collision Intelligence
            </h1>
            <p className="text-sm text-muted-foreground">
              Evaluación empírica de fechas de lanzamiento, detección de conflicto con rebajas masivas y alternativas óptimas.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-primary/10 border border-primary/30 text-primary px-3 py-1.5 rounded text-xs">
            <ShieldCheck className="w-4 h-4" />
            <span>Asociación Temporal ≠ Causalidad</span>
          </div>
        </div>

        {/* Launch Collision Simulator */}
        <div className="bg-card/70 border border-border p-6 rounded-lg space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Flame className="w-5 h-5 text-amber-400" />
                Simulador de Colisión de Lanzamiento
              </h2>
              <p className="text-xs text-gray-400">
                Selecciona una fecha tentativa para evaluar solapamientos con festivales de demos, sales y densidad competitiva.
              </p>
            </div>
            {collisionResult && (
              <span
                className={cn(
                  "px-3 py-1 rounded text-xs font-bold uppercase border",
                  collisionResult.collision_level === "extreme"
                    ? "bg-rose-500/20 text-rose-400 border-rose-500/40"
                    : collisionResult.collision_level === "high"
                    ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                    : collisionResult.collision_level === "moderate"
                    ? "bg-blue-500/20 text-blue-400 border-blue-500/40"
                    : "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                )}
              >
                Riesgo: {collisionResult.collision_level} ({collisionResult.collision_score}/100)
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Fecha Objetivo de Lanzamiento:
              </label>
              <input
                type="date"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
                className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Radio de Ventana ({daysWindow} días):
              </label>
              <input
                type="range"
                min={7}
                max={30}
                value={daysWindow}
                onChange={(e) => setDaysWindow(parseInt(e.target.value))}
                className="w-full mt-2"
              />
            </div>
          </div>

          {collisionResult && (
            <div className="space-y-4 pt-2">
              <div className="bg-[#0b101c] border border-border p-4 rounded text-xs space-y-2">
                <span className="font-bold text-white uppercase tracking-wider">Diagnóstico:</span>
                <p className="text-gray-300">{collisionResult.recommendation}</p>
              </div>

              {/* Overlapping Events */}
              {collisionResult.overlapping_events?.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    Eventos Masivos en Conflicto ({collisionResult.overlapping_events.length}):
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {collisionResult.overlapping_events.map((ev: any, i: number) => (
                      <div key={i} className="bg-rose-950/20 border border-rose-500/30 p-3 rounded text-xs space-y-1">
                        <div className="flex justify-between font-semibold text-rose-300">
                          <span>{ev.name}</span>
                          <span className="text-[10px] uppercase text-rose-400">{ev.event_type}</span>
                        </div>
                        <p className="text-gray-400 text-[11px]">{ev.start_date} al {ev.end_date}</p>
                        <p className="text-gray-300 italic text-[11px] mt-1">{ev.impact_note}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Clean Alternative Windows */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Ventanas Alternativas Despejadas Sugeridas:
                </span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {collisionResult.alternative_windows?.map((w: any, idx: number) => (
                    <div key={idx} className="bg-emerald-950/20 border border-emerald-500/30 p-3 rounded text-xs space-y-1">
                      <span className="font-bold text-emerald-300">
                        {w.start} al {w.end}
                      </span>
                      <p className="text-gray-300 text-[11px]">{w.reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Industry Events Schedule */}
        <div className="bg-card/70 border border-border p-6 rounded-lg space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <CalendarDays className="w-4 h-4 text-primary" />
              Calendario Oficial de Eventos de la Industria & Steam
            </h2>
            <span className="text-xs text-gray-400">Fuentes documentadas oficiales</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0b101c] text-gray-400 uppercase tracking-wider border-b border-border">
                <tr>
                  <th className="py-2.5 px-3">Evento</th>
                  <th className="py-2.5 px-3">Tipo</th>
                  <th className="py-2.5 px-3">Inicio</th>
                  <th className="py-2.5 px-3">Fin</th>
                  <th className="py-2.5 px-3">Impacto Típico</th>
                  <th className="py-2.5 px-3">Fuente</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {events.map((e) => (
                  <tr key={e.id} className="hover:bg-card/80 transition-colors">
                    <td className="py-3 px-3 font-medium text-white">{e.name}</td>
                    <td className="py-3 px-3">
                      <span className="bg-secondary/40 text-gray-300 border border-border px-2 py-0.5 rounded text-[10px] uppercase">
                        {e.event_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-gray-300">{e.start_date}</td>
                    <td className="py-3 px-3 text-gray-300">{e.end_date}</td>
                    <td className="py-3 px-3 text-gray-400 max-w-xs truncate">{e.description}</td>
                    <td className="py-3 px-3 text-gray-500 text-[10px]">{e.source_ref}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Cohorts Analysis Preview */}
        {cohorts && (
          <div className="bg-card/70 border border-border p-6 rounded-lg space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-primary" />
                Análisis por Cohortes de Lanzamiento
              </h2>
              <span className="text-xs text-gray-400">Muestra: {cohorts.total_sample_size} juegos</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {cohorts.cohorts?.map((c: any) => (
                <div key={c.cohort} className="bg-[#0b101c] border border-border p-4 rounded text-xs space-y-1">
                  <span className="text-gray-400 uppercase text-[10px]">Año {c.cohort}</span>
                  <div className="text-xl font-bold text-white">{c.sample_size} juegos</div>
                  <p className="text-[11px] text-gray-400">Early Access: {c.early_access_ratio}%</p>
                </div>
              ))}
            </div>
            <p className="text-[11px] text-gray-500 italic">{cohorts.disclaimer}</p>
          </div>
        )}
      </main>
    </div>
  );
}
