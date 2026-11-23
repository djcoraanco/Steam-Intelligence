"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api, DataSourceItem, CatalogStatus } from "@/lib/api";
import {
  Database,
  Play,
  CheckCircle2,
  XCircle,
  ExternalLink,
  RefreshCw,
  Layers,
  ArrowRight,
  Clock,
  Check
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function SourcesPage() {
  const [sources, setSources] = useState<DataSourceItem[]>([]);
  const [catalogStatus, setCatalogStatus] = useState<CatalogStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [testingCode, setTestingCode] = useState<string | null>(null);
  const [syncingCatalog, setSyncingCatalog] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, any>>({});

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = () => {
    setLoading(true);
    Promise.all([api.getSources(), api.getCatalogStatus()])
      .then(([srcs, catStat]) => {
        setSources(srcs);
        setCatalogStatus(catStat);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleTestConnection = async (code: string) => {
    setTestingCode(code);
    try {
      const res = await api.testSource(code);
      setTestResults((prev) => ({ ...prev, [code]: res }));
    } catch (err: any) {
      setTestResults((prev) => ({
        ...prev,
        [code]: { success: false, message: err.message || "Error al conectar" },
      }));
    } finally {
      setTestingCode(null);
    }
  };

  const handleSyncCatalog = async () => {
    setSyncingCatalog(true);
    setSyncResult(null);
    try {
      const res = await api.triggerCatalogSync(1000);
      setSyncResult(`Sincronizados ${res.imported} nuevos juegos. Último AppID: ${res.last_appid}.`);
      loadSources();
    } catch (err: any) {
      setSyncResult(`Fallo en sincronización: ${err.message}`);
    } finally {
      setSyncingCatalog(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="Data Sources · Conectores y Estado de Proveedores" />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Catalog Ingestion Card (Phase 2 & 3) */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-sky-950/80 border border-sky-800 text-sky-400 flex items-center justify-center">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold text-sm text-white">Sincronización de Catálogo Steam</h3>
                <p className="text-xs text-muted-foreground">
                  Ingesta masiva incremental mediante <span className="font-mono text-gray-300">IStoreService/GetAppList/v1/</span> con cursor y checkpoint.
                </p>
              </div>
            </div>

            <button
              onClick={handleSyncCatalog}
              disabled={syncingCatalog}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-xs font-medium transition disabled:opacity-50 shrink-0"
            >
              <RefreshCw className={cn("w-3.5 h-3.5", syncingCatalog && "animate-spin")} />
              <span>{syncingCatalog ? "Sincronizando lote..." : "Sincronizar Lote"}</span>
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-slate-900/60 p-3.5 rounded-lg border border-border/80">
            <div>
              <span className="text-gray-500 block text-[10px] uppercase font-semibold">Títulos Registrados</span>
              <span className="text-base font-bold font-mono text-white">
                {catalogStatus ? catalogStatus.total_records.toLocaleString() : "0"}
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px] uppercase font-semibold">Cursor (Last AppID)</span>
              <span className="text-base font-mono text-cyan-300">
                {catalogStatus?.last_cursor || "Inicio"}
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px] uppercase font-semibold">Estado del Proceso</span>
              <span className="text-xs uppercase font-semibold text-emerald-400 font-mono">
                {catalogStatus?.status || "Idle"}
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px] uppercase font-semibold">Última Ejecución</span>
              <span className="text-xs text-gray-300 font-mono">
                {catalogStatus?.last_synced_at
                  ? new Date(catalogStatus.last_synced_at).toLocaleTimeString()
                  : "Nunca"}
              </span>
            </div>
          </div>

          {syncResult && (
            <div className="text-xs p-2.5 rounded bg-sky-950/60 border border-sky-800 text-sky-200">
              {syncResult}
            </div>
          )}
        </div>

        {/* Sources Section Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight uppercase text-gray-400">
              Inventario de Conectores Registrados
            </h2>
          </div>
          <button
            onClick={loadSources}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-card border border-border hover:border-gray-600 text-xs text-gray-300 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Actualizar</span>
          </button>
        </div>

        {loading ? (
          <div className="py-16 text-center text-xs text-muted-foreground animate-pulse">
            Consultando estado de fuentes...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sources.map((src) => {
              const testResult = testResults[src.code];
              const isTesting = testingCode === src.code;

              return (
                <div
                  key={src.id}
                  className="bg-card border border-border rounded-lg p-5 flex flex-col justify-between space-y-4 hover:border-gray-700 transition"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="w-9 h-9 rounded bg-primary/10 border border-primary/30 flex items-center justify-center text-primary">
                          <Database className="w-4 h-4" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sm text-white">{src.name}</h3>
                          <span className="text-[11px] font-mono text-gray-500">{src.code}</span>
                        </div>
                      </div>

                      <span
                        className={cn(
                          "text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded border",
                          src.status === "active"
                            ? "bg-emerald-950/80 text-emerald-400 border-emerald-800"
                            : src.status === "planned"
                            ? "bg-blue-950/80 text-blue-400 border-blue-800"
                            : "bg-slate-800 text-gray-400 border-slate-700"
                        )}
                      >
                        {src.status}
                      </span>
                    </div>

                    <div className="text-xs text-gray-400 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-500">Tipo de proveedor:</span>
                        <span className="font-mono text-gray-300">{src.provider_type}</span>
                      </div>
                      {src.base_url && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-500">Endpoint Base:</span>
                          <span className="font-mono text-gray-400 text-[11px] truncate max-w-[200px]">
                            {src.base_url}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Capabilities Tags */}
                    <div>
                      <div className="text-[10px] text-gray-500 uppercase font-semibold mb-1.5">Capacidades:</div>
                      <div className="flex flex-wrap gap-1.5">
                        {src.capabilities.map((cap) => (
                          <span
                            key={cap}
                            className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-border/80 text-gray-300"
                          >
                            {cap}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Test result status badge */}
                    {testResult && (
                      <div
                        className={cn(
                          "p-2.5 rounded text-xs flex items-start gap-2 border",
                          testResult.success
                            ? "bg-emerald-950/60 border-emerald-800 text-emerald-300"
                            : "bg-red-950/60 border-red-800 text-red-300"
                        )}
                      >
                        {testResult.success ? (
                          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-400" />
                        ) : (
                          <XCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
                        )}
                        <div>
                          <div className="font-semibold">
                            {testResult.success
                              ? `Conexión Exitosa (${testResult.response_time_ms} ms)`
                              : "Prueba fallida"}
                          </div>
                          <div className="text-[11px] opacity-90">{testResult.message}</div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions & Documentation */}
                  <div className="pt-3 border-t border-border/70 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3 text-primary">
                      {src.documentation_url && (
                        <a
                          href={src.documentation_url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-1 hover:underline text-[11px]"
                        >
                          <span>Docs</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {src.terms_url && (
                        <a
                          href={src.terms_url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-1 hover:underline text-[11px] text-gray-400"
                        >
                          <span>Términos</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>

                    <button
                      onClick={() => handleTestConnection(src.code)}
                      disabled={isTesting}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-primary/20 hover:bg-primary/30 border border-primary/40 text-primary text-xs font-medium transition disabled:opacity-50"
                    >
                      <Play className="w-3 h-3" />
                      <span>{isTesting ? "Probando..." : "Probar Conexión"}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
