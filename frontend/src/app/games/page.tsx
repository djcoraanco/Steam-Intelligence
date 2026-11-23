"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api, GameSummaryItem, GameDetailItem } from "@/lib/api";
import { formatPrice } from "@/lib/utils";
import {
  Gamepad2,
  Search,
  ExternalLink,
  RefreshCw,
  Tag,
  Building,
  Calendar,
  X,
  Sparkles,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

export default function GamesPage() {
  const [games, setGames] = useState<GameSummaryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedGameId, setSelectedGameId] = useState<string | null>(null);
  const [detail, setDetail] = useState<GameDetailItem | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [syncingMetadata, setSyncingMetadata] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  useEffect(() => {
    loadGames();
  }, [search]);

  const loadGames = () => {
    setLoading(true);
    api
      .getGames({ limit: 24, search: search.trim() || undefined })
      .then((res) => {
        setGames(res.items);
        setTotal(res.total);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleOpenDetail = (gameId: string) => {
    setSelectedGameId(gameId);
    setDetailLoading(true);
    setSyncMessage(null);
    api
      .getGameDetail(gameId)
      .then((data) => {
        setDetail(data);
        setDetailLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setDetailLoading(false);
      });
  };

  const handleSyncMetadata = async () => {
    if (!selectedGameId) return;
    setSyncingMetadata(true);
    setSyncMessage(null);
    try {
      const res = await api.syncGameMetadata(selectedGameId);
      if (res.success) {
        setSyncMessage("Metadatos y precios sincronizados exitosamente desde Steam Storefront.");
        // Refresh details
        const updated = await api.getGameDetail(selectedGameId);
        setDetail(updated);
        loadGames();
      } else {
        setSyncMessage(res.message || "La tienda reportó datos no disponibles.");
      }
    } catch (err: any) {
      setSyncMessage(err.message || "Error al sincronizar metadatos.");
    } finally {
      setSyncingMetadata(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="Game Explorer · Catálogo y Fichas de Producto" />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Search & Actions Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-96">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por título de videojuego..."
              className="w-full bg-card border border-border rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-primary transition"
            />
          </div>

          <div className="text-xs text-muted-foreground">
            Mostrando <span className="text-white font-semibold">{games.length}</span> de{" "}
            <span className="text-white font-semibold">{total}</span> títulos en catálogo
          </div>
        </div>

        {/* Games Grid */}
        {loading ? (
          <div className="py-20 text-center text-xs text-muted-foreground animate-pulse">
            Consultando catálogo de videojuegos...
          </div>
        ) : games.length === 0 ? (
          <div className="py-20 text-center text-xs text-gray-400 bg-card border border-border rounded-lg p-8">
            <Gamepad2 className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <div className="text-sm font-semibold text-white mb-1">No se encontraron videojuegos</div>
            <p className="max-w-md mx-auto text-muted-foreground mb-4">
              Si acabas de inicializar el sistema, ejecuta una sincronización de catálogo desde el panel de fuentes.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {games.map((g) => (
              <div
                key={g.id}
                onClick={() => handleOpenDetail(g.id)}
                className="bg-card border border-border rounded-lg overflow-hidden hover:border-gray-600 transition flex flex-col justify-between cursor-pointer group"
              >
                <div>
                  <div className="w-full h-32 bg-slate-900 relative overflow-hidden">
                    {g.cover_image_url ? (
                      <img
                        src={g.cover_image_url}
                        alt={g.canonical_name}
                        className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-700">
                        <Gamepad2 className="w-8 h-8" />
                      </div>
                    )}
                    {g.is_early_access && (
                      <span className="absolute top-2 left-2 bg-amber-500/90 text-black text-[9px] font-bold px-1.5 py-0.5 rounded">
                        Early Access
                      </span>
                    )}
                  </div>

                  <div className="p-3.5 space-y-1.5">
                    <h3 className="font-semibold text-xs text-white line-clamp-1 group-hover:text-primary transition">
                      {g.canonical_name}
                    </h3>
                    <div className="text-[11px] text-gray-400 flex items-center justify-between">
                      <span className="font-mono">AppID: {g.steam_appid || "—"}</span>
                      <span className="uppercase text-[9px] px-1 py-0.5 rounded bg-slate-800 text-gray-300">
                        {g.game_type}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-3.5 pt-0 border-t border-border/50 flex items-center justify-between text-xs mt-2">
                  <div className="font-semibold text-cyan-300 font-mono">
                    {g.is_free ? (
                      <span className="text-emerald-400">Gratis</span>
                    ) : g.price_cents !== null && g.price_cents !== undefined ? (
                      formatPrice(g.price_cents, g.currency)
                    ) : (
                      <span className="text-gray-500 font-normal">Precio no verificado</span>
                    )}
                  </div>
                  <span className="text-[10px] text-primary group-hover:underline flex items-center gap-0.5">
                    Ficha técnica →
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Game Detail Modal */}
        {selectedGameId && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-card border border-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-5 shadow-2xl relative">
              <button
                onClick={() => setSelectedGameId(null)}
                className="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-white rounded-md hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>

              {detailLoading || !detail ? (
                <div className="py-20 text-center text-xs text-muted-foreground animate-pulse">
                  Cargando ficha del videojuego...
                </div>
              ) : (
                <div className="space-y-5">
                  <div className="flex gap-4 items-start">
                    {detail.cover_image_url && (
                      <img
                        src={detail.cover_image_url}
                        alt=""
                        className="w-40 h-24 object-cover rounded-lg border border-border shrink-0"
                      />
                    )}
                    <div className="space-y-1">
                      <h2 className="text-base font-bold text-white tracking-tight">{detail.canonical_name}</h2>
                      <div className="flex flex-wrap gap-2 text-xs text-gray-400">
                        <span className="font-mono">AppID: {detail.steam_appid}</span>
                        {detail.release_date && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {detail.release_date}
                          </span>
                        )}
                      </div>
                      <div className="pt-1 flex items-center gap-2">
                        {detail.is_early_access && (
                          <span className="bg-amber-500/20 text-amber-400 border border-amber-800 text-[10px] font-bold px-2 py-0.5 rounded">
                            Early Access
                          </span>
                        )}
                        <span className="bg-slate-800 text-gray-300 text-[10px] font-medium px-2 py-0.5 rounded">
                          {detail.release_status}
                        </span>
                      </div>
                    </div>
                  </div>

                  {syncMessage && (
                    <div className="p-3 rounded-lg bg-sky-950/60 border border-sky-800 text-sky-200 text-xs flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0" />
                      <span>{syncMessage}</span>
                    </div>
                  )}

                  {/* Pricing Overview */}
                  <div className="bg-slate-900/60 border border-border p-4 rounded-lg flex items-center justify-between">
                    <div>
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                        Precio Observado (Storefront)
                      </div>
                      <div className="flex items-baseline gap-2 mt-1">
                        <span className="text-xl font-bold font-mono text-cyan-300">
                          {detail.is_free
                            ? "Free to Play"
                            : detail.final_price_cents !== null && detail.final_price_cents !== undefined
                            ? formatPrice(detail.final_price_cents, detail.currency)
                            : "No disponible"}
                        </span>
                        {detail.discount_percent ? (
                          <span className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.5 rounded font-mono font-semibold">
                            -{detail.discount_percent}%
                          </span>
                        ) : null}
                        {detail.regular_price_cents && detail.regular_price_cents !== detail.final_price_cents ? (
                          <span className="text-xs line-through text-gray-500 font-mono">
                            {formatPrice(detail.regular_price_cents, detail.currency)}
                          </span>
                        ) : null}
                      </div>
                    </div>

                    <button
                      onClick={handleSyncMetadata}
                      disabled={syncingMetadata}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary/20 hover:bg-primary/30 border border-primary/40 text-primary text-xs font-medium transition disabled:opacity-50"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>{syncingMetadata ? "Sincronizando..." : "Actualizar Storefront"}</span>
                    </button>
                  </div>

                  {/* Description */}
                  {detail.short_description && (
                    <div className="space-y-1">
                      <div className="text-xs font-semibold text-gray-300">Descripción Corta</div>
                      <p className="text-xs text-gray-400 leading-relaxed bg-slate-900/40 p-3 rounded-lg border border-border/60">
                        {detail.short_description}
                      </p>
                    </div>
                  )}

                  {/* Developers, Publishers & Genres */}
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div className="bg-slate-900/40 p-3 rounded-lg border border-border/60 space-y-1">
                      <div className="text-gray-500 font-semibold flex items-center gap-1.5 text-[11px]">
                        <Building className="w-3.5 h-3.5" /> Desarrollador / Editor
                      </div>
                      <div className="text-gray-200">
                        {detail.developers.length > 0 ? detail.developers.join(", ") : "No especificado"}
                      </div>
                    </div>

                    <div className="bg-slate-900/40 p-3 rounded-lg border border-border/60 space-y-1">
                      <div className="text-gray-500 font-semibold flex items-center gap-1.5 text-[11px]">
                        <Tag className="w-3.5 h-3.5" /> Géneros Declarados
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {detail.genres.length > 0 ? (
                          detail.genres.map((g) => (
                            <span key={g} className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-gray-300">
                              {g}
                            </span>
                          ))
                        ) : (
                          <span className="text-gray-500">Sin clasificar</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* External Store Link */}
                  {detail.store_url && (
                    <div className="pt-2 flex justify-end">
                      <a
                        href={detail.store_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-primary hover:text-sky-300 flex items-center gap-1 font-medium transition"
                      >
                        <span>Abrir página oficial de Steam</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
