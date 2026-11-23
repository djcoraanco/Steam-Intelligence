"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Store, CheckCircle2, AlertCircle, Info, ExternalLink, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

export default function PCExpansionPage() {
  const [registry, setRegistry] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStores() {
      try {
        const data = await api.getStoreRegistry();
        setRegistry(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadStores();
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Store className="w-6 h-6 text-primary" />
              PC Storefront Expansion & Capabilities
            </h1>
            <p className="text-sm text-muted-foreground">
              Cobertura multiplataforma de PC (Steam, IGDB, itch.io, GOG, Epic Games Store) respetando licencias y términos de servicio.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1.5 rounded text-xs">
            <ShieldCheck className="w-4 h-4" />
            <span>Términos Verificados & Sin Scraping No Autorizado</span>
          </div>
        </div>

        {/* IGDB Mandatory Attribution Card */}
        {registry.igdb?.attribution_required && (
          <div className="bg-purple-950/20 border border-purple-500/40 p-4 rounded-lg flex items-start gap-3">
            <Info className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs">
              <span className="font-semibold text-purple-300 uppercase tracking-wider block">
                Aviso Obligatorio de Atribución Editorial
              </span>
              <p className="text-purple-200">
                {registry.igdb.attribution_notice}
              </p>
            </div>
          </div>
        )}

        {/* Store Registry Cards */}
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Cargando matriz de tiendas...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(registry).map(([code, store]) => {
              const isActive = store.status === "active";
              const isMetaOnly = store.status === "metadata_only";
              return (
                <div key={code} className="bg-card/70 border border-border rounded-lg p-5 space-y-4 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase font-mono text-gray-500">{code}</span>
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                          isActive
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            : isMetaOnly
                            ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                            : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        )}
                      >
                        {store.status}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-bold text-white text-base">{store.name}</h3>
                      <p className="text-xs text-gray-400 mt-1">{store.notes}</p>
                    </div>

                    <div>
                      <span className="text-[11px] uppercase font-semibold text-gray-400 tracking-wider block mb-1.5">
                        Capacidades Autorizadas:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {store.capabilities?.map((cap: string) => (
                          <span
                            key={cap}
                            className="bg-secondary/40 border border-border text-gray-300 text-[10px] px-2 py-0.5 rounded"
                          >
                            {cap}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-border/60 text-[11px] text-gray-500 flex items-center justify-between">
                    <span>Tipo: {store.type}</span>
                    {store.attribution_required && <span className="text-purple-400">Atribución Activa</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
