"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { FileSpreadsheet, Download, FileText, Presentation, FileCode, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ReportsPage() {
  const [genre, setGenre] = useState("Action");
  const [customTitle, setCustomTitle] = useState("Informe Ejecutivo de Mercado — Steam Intelligence");
  const [exportHistory, setExportHistory] = useState<any[]>([]);
  const [generatingFormat, setGeneratingFormat] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async (format: string) => {
    setGeneratingFormat(format);
    setError(null);
    try {
      const res = await api.exportReport(format, genre, customTitle);
      setExportHistory((prev) => [res, ...prev]);

      // Direct trigger of download
      const downloadUrl = `${process.env.NEXT_PUBLIC_API_URL || ""}${res.download_url}`;
      window.open(downloadUrl, "_blank");
    } catch (err: any) {
      setError(err.message || "Error al generar informe");
    } finally {
      setGeneratingFormat(null);
    }
  };

  const FORMATS = [
    {
      format: "pdf",
      title: "Informe Ejecutivo PDF",
      engine: "ReportLab",
      desc: "Documento vectorial listo para imprimir con texto seleccionable, cabeceras, pie con 'Página X de Y' y notas de evidencia.",
      icon: FileText,
      badge: "Recomendado para Dirección"
    },
    {
      format: "pptx",
      title: "Presentación PPTX",
      engine: "python-pptx",
      desc: "Presentación en formato 16:9 widescreen con diseño oscuro profesional, diapositivas ejecutivas y notas al pie.",
      icon: Presentation,
      badge: "Editable en PowerPoint"
    },
    {
      format: "xlsx",
      title: "Libro de Cálculo XLSX",
      engine: "openpyxl",
      desc: "Libro multisede con hojas separadas para Resumen, Hallazgos, Recomendaciones y Limitaciones con formato y anchos automáticos.",
      icon: FileSpreadsheet,
      badge: "Para Analistas Financieros"
    },
    {
      format: "csv",
      title: "Datos Tabulares CSV",
      engine: "csv / pandas",
      desc: "Exportación plana delimitada por comas para integración con herramientas externas de BI y pipelines de datos.",
      icon: FileSpreadsheet,
      badge: "Para Pipelines Externos"
    },
    {
      format: "json",
      title: "Datos Estructurados JSON",
      engine: "JSON nativo",
      desc: "Copia fiel de los datos estructurados con trazabilidad de fecha de corte, versión de algoritmos y reproducibilidad.",
      icon: FileCode,
      badge: "Reproducibilidad Total"
    }
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <FileSpreadsheet className="w-6 h-6 text-primary" />
              Centro de Exportaciones & Informes Profesionales
            </h1>
            <p className="text-sm text-muted-foreground">
              Generación multiformato de documentos reproducibles (PDF, PPTX, XLSX, CSV, JSON) cumpliendo el estándar de la Sección 15.
            </p>
          </div>
        </div>

        {/* Configuration Bar */}
        <div className="bg-card/70 border border-border p-6 rounded-lg space-y-4">
          <h2 className="text-base font-bold text-white">Configuración del Informe a Exportar</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Título Personalizado del Documento:
              </label>
              <input
                type="text"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Segmento de Mercado / Género:
              </label>
              <input
                type="text"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                className="w-full bg-[#0a0f1d] border border-border text-white text-sm rounded px-3 py-2"
              />
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Format Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FORMATS.map((item) => {
            const Icon = item.icon;
            const isGenerating = generatingFormat === item.format;
            return (
              <div
                key={item.format}
                className="bg-card/70 border border-border rounded-lg p-5 space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="bg-primary/20 text-primary border border-primary/30 text-[10px] font-bold px-2 py-0.5 rounded uppercase">
                      {item.badge}
                    </span>
                    <span className="text-[10px] text-gray-500 font-mono">{item.engine}</span>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-base">{item.title}</h3>
                      <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">
                        Formato: .{item.format}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-gray-400 leading-relaxed">{item.desc}</p>
                </div>

                <button
                  onClick={() => handleExport(item.format)}
                  disabled={isGenerating}
                  className="w-full mt-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-xs rounded flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                  {isGenerating ? `Generando .${item.format.toUpperCase()}...` : `Descargar .${item.format.toUpperCase()}`}
                </button>
              </div>
            );
          })}
        </div>

        {/* Recent Generated Exports */}
        {exportHistory.length > 0 && (
          <div className="bg-card/70 border border-border rounded-lg p-6 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Archivos Generados en esta Sesión
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0b101c] text-gray-400 uppercase tracking-wider border-b border-border">
                  <tr>
                    <th className="py-2.5 px-3">Archivo</th>
                    <th className="py-2.5 px-3">Formato</th>
                    <th className="py-2.5 px-3">Hora de Generación</th>
                    <th className="py-2.5 px-3 text-right">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {exportHistory.map((h, i) => (
                    <tr key={i} className="hover:bg-card/80 transition-colors">
                      <td className="py-3 px-3 font-medium text-white">{h.filename}</td>
                      <td className="py-3 px-3 uppercase text-primary font-bold">{h.format}</td>
                      <td className="py-3 px-3 text-gray-400">{h.generated_at}</td>
                      <td className="py-3 px-3 text-right">
                        <a
                          href={`${process.env.NEXT_PUBLIC_API_URL || ""}${h.download_url}`}
                          target="_blank"
                          rel="noreferrer"
                          className="px-3 py-1 bg-secondary text-white rounded text-[11px] hover:bg-secondary/80 inline-flex items-center gap-1"
                        >
                          <Download className="w-3.5 h-3.5" /> Descargar
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
