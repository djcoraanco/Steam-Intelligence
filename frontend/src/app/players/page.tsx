"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api, GameSummaryItem } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";
import {
  Activity,
  RefreshCw,
  Clock,
  Radio,
  Gamepad2,
  TrendingUp,
  AlertCircle,
  Eye,
  CheckCircle2
} from "lucide-react";

export default function PlayersPage() {
  const [games, setGames] = useState<GameSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGameId, setSelectedGameId] = useState<string | null>(null);
  const [history, setHistory] = useState<any | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [snapshottingId, setSnapshottingId] = useState<string | null>(null);
  const [snapMessage, setSnapMessage] = useState<string | null>(null);

  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = () => {
    setLoading(true);
    api
      .getGames({ limit: 30 })
      .then((res) => {
        setGames(res.items);
        setLoading(false);
        if (res.items.length > 0 && !selectedGameId) {
          selectGame(res.items[0].id);
        }
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const selectGame = (gameId: string) => {
    setSelectedGameId(gameId);
    setHistoryLoading(true);
    setSnapMessage(null);
    api
      .getGameHistory(gameId)
      .then((data) => {
        setHistory(data);
        setHistoryLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setHistoryLoading(false);
      });
  };

  const handleTakeSnapshot = async (gameId: string) => {
    setSnapshottingId(gameId);
    setSnapMessage(null);
    try {
      const res = await api.snapshotPlayers(gameId);
      if (res.success) {
        setSnapMessage(`Snapshot capturado: ${formatNumber(res.player_count)} jugadores concurrentes.`);
        selectGame(gameId);
        loadGames();
      } else {
        setSnapMessage(`Proveedor reportó estado: ${res.availability_status}`);
      }
    } catch (err: any) {
      setSnapMessage(err.message || "Error al tomar snapshot");
    } finally {
      setSnapshottingId(null);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="Player Analytics · Concurrencia y Series Temporales CCU" />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Provenance note */}
        <div className="bg-slate-900/60 border border-border rounded-xl p-4 flex items-center justify-between text-xs">
          <div className="flex items-center gap-3">
            <Radio className="w-4 h-4 text-emerald-400 animate-pulse shrink-0" />
            <div className="text-gray-300">
              <span className="font-semibold text-white">Métrica Instantánea (CCU): </span>
              El endpoint oficial de Steam sólo devuelve el número del instante presente. Steam Intelligence construye la serie histórica guardando snapshots propios inmutables cada 15-30 min.
            </div>
          </div>
        </div>

        {snapMessage && (
          <div className="p-3 rounded-lg bg-sky-950/60 border border-sky-800 text-sky-200 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0" />
            <span>{snapMessage}</span>
          </div>
        )}

        {/* Two-column layout: Games List & Selected Game History */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Games list for selection */}
          <div className="bg-card border border-border rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <h3 className="font-semibold text-xs text-white uppercase tracking-wider">Títulos Monitorizados</h3>
              <button onClick={loadGames} className="text-gray-400 hover:text-white p-1">
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            {loading ? (
              <div className="py-12 text-center text-xs text-muted-foreground animate-pulse">
                Cargando lista de juegos...
              </div>
            ) : games.length === 0 ? (
              <div className="py-12 text-center text-xs text-gray-500">
                No hay juegos registrados en el catálogo.
              </div>
            ) : (
              <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-1">
                {games.map((g) => {
                  const isSelected = selectedGameId === g.id;
                  return (
                    <div
                      key={g.id}
                      onClick={() => selectGame(g.id)}
                      className={cn(
                        "p-3 rounded-lg border cursor-pointer transition flex items-center justify-between text-xs",
                        isSelected
                          ? "bg-primary/15 border-primary/40 text-white"
                          : "bg-slate-900/40 border-border/60 hover:bg-slate-800/60 text-gray-300"
                      )}
                    >
                      <div className="flex items-center gap-2.5">
                        <Gamepad2 className={cn("w-4 h-4", isSelected ? "text-primary" : "text-gray-500")} />
                        <div>
                          <div className="font-medium line-clamp-1">{g.canonical_name}</div>
                          <div className="text-[10px] text-gray-500 font-mono">AppID: {g.steam_appid || "—"}</div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="font-mono font-semibold text-cyan-300 text-xs">
                          {g.current_players ? formatNumber(g.current_players) : "—"}
                        </div>
                        <span className="text-[9px] uppercase tracking-wider text-gray-500">CCU</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* History details & timeline */}
          <div className="lg:col-span-2 bg-card border border-border rounded-xl p-5 space-y-5">
            {historyLoading || !history ? (
              <div className="py-24 text-center text-xs text-muted-foreground animate-pulse">
                Consultando historial de snapshots para el juego seleccionado...
              </div>
            ) : (
              <div className="space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/80 pb-4">
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">{history.canonical_name}</h3>
                    <div className="text-xs text-muted-foreground font-mono">
                      Steam AppID: {history.steam_appid} · {history.player_history.length} snapshots registrados
                    </div>
                  </div>

                  <button
                    onClick={() => handleTakeSnapshot(history.game_id)}
                    disabled={snapshottingId === history.game_id}
                    className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-xs font-medium transition disabled:opacity-50 shrink-0"
                  >
                    <Activity className="w-3.5 h-3.5" />
                    <span>
                      {snapshottingId === history.game_id ? "Tomando snapshot..." : "Capturar CCU Ahora"}
                    </span>
                  </button>
                </div>

                {/* Timeline table */}
                <div>
                  <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-cyan-400" />
                    Historial Cronológico de Observaciones
                  </h4>

                  {history.player_history.length === 0 ? (
                    <div className="py-12 text-center text-xs text-gray-500 bg-slate-900/40 rounded-lg border border-border/60">
                      Aún no hay mediciones de jugadores guardadas para este juego. Presiona "Capturar CCU Ahora".
                    </div>
                  ) : (
                    <div className="overflow-x-auto border border-border/80 rounded-lg">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900/80 border-b border-border text-gray-400 text-[10px] uppercase">
                          <tr>
                            <th className="py-2.5 px-3 font-medium">Timestamp (UTC)</th>
                            <th className="py-2.5 px-3 font-medium text-right">Jugadores (CCU)</th>
                            <th className="py-2.5 px-3 font-medium text-right">Disponibilidad</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border/40">
                          {history.player_history.map((snap: any, i: number) => (
                            <tr key={i} className="hover:bg-slate-800/30">
                              <td className="py-2.5 px-3 font-mono text-gray-300 text-[11px]">
                                {new Date(snap.observed_at).toLocaleString()}
                              </td>
                              <td className="py-2.5 px-3 text-right font-mono font-bold text-cyan-300">
                                {snap.player_count !== null ? formatNumber(snap.player_count) : "—"}
                              </td>
                              <td className="py-2.5 px-3 text-right">
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-400 font-medium">
                                  {snap.availability_status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
