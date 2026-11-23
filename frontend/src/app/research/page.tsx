"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";
import {
  FlaskConical,
  Play,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileText,
  Search,
  Sparkles,
  ArrowRight,
  Database,
  BarChart3,
  Bot
} from "lucide-react";
import Link from "next/link";

interface ResearchProject {
  id: string;
  title: string;
  genre: string;
  target_price: number;
  status: "completed" | "running" | "draft";
  created_at: string;
  sample_size: number;
  market_viability_score: number;
  summary: string;
}

const SAMPLE_PROJECTS: ResearchProject[] = [
  {
    id: "res-001",
    title: "Roguelike Deckbuilder with Auto-Battler Mechanics",
    genre: "Strategy / Roguelike",
    target_price: 19.99,
    status: "completed",
    created_at: "2026-11-20T14:30:00Z",
    sample_size: 142,
    market_viability_score: 86,
    summary: "High demand, low supply in modern sci-fi themes. Median revenue exceeds $240K for titles with >500 reviews."
  },
  {
    id: "res-002",
    title: "Post-Apocalyptic Cozy Farming Simulator",
    genre: "Simulation / RPG",
    target_price: 14.99,
    status: "completed",
    created_at: "2026-11-18T10:15:00Z",
    sample_size: 89,
    market_viability_score: 72,
    summary: "Niche resonance strong among cozy gamers looking for subversion of typical pastoral tropes."
  },
  {
    id: "res-003",
    title: "Extraction PVPVE in Fantasy Medieval Setting",
    genre: "Action / Survival",
    target_price: 29.99,
    status: "running",
    created_at: "2026-11-23T18:00:00Z",
    sample_size: 64,
    market_viability_score: 68,
    summary: "Analyzing player churn and server stability complaints in competitor review corpora."
  }
];

export default function ResearchCenterPage() {
  const [projects, setProjects] = useState<ResearchProject[]>(SAMPLE_PROJECTS);
  const [isCreating, setIsCreating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newGenre, setNewGenre] = useState("Roguelike");
  const [newPrice, setNewPrice] = useState("19.99");
  const [newConcept, setNewConcept] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const handleRunResearch = async () => {
    if (!newConcept.trim()) return;
    setIsAnalyzing(true);
    try {
      const res = await api.validateConcept(newConcept, [newGenre]);
      setAnalysisResult(res);

      const created: ResearchProject = {
        id: `res-${Date.now().toString().slice(-4)}`,
        title: newTitle || newConcept.slice(0, 45) + "...",
        genre: newGenre,
        target_price: parseFloat(newPrice) || 19.99,
        status: "completed",
        created_at: new Date().toISOString(),
        sample_size: res.sample_size || 50,
        market_viability_score: res.viability_score || 80,
        summary: res.verdict || "Deep research complete with automated sample verification."
      };
      setProjects([created, ...projects]);
      setIsCreating(false);
      setNewConcept("");
      setNewTitle("");
    } catch (err) {
      console.error("Failed to run autonomous research", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
          <div>
            <div className="flex items-center gap-2">
              <FlaskConical className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold tracking-tight text-white">Research Center</h1>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Autonomous market research engine: concept viability testing, competitor cohort synthesis, and thesis validation.
            </p>
          </div>

          <button
            onClick={() => setIsCreating(!isCreating)}
            className="px-4 py-2 bg-primary text-black font-semibold rounded-md text-sm hover:bg-primary/90 transition-colors flex items-center gap-2 self-start md:self-auto"
          >
            <Play className="w-4 h-4" />
            {isCreating ? "Close Wizard" : "New Research Dossier"}
          </button>
        </div>

        {/* Wizard Form */}
        {isCreating && (
          <div className="bg-card border border-primary/40 rounded-lg p-5 space-y-4 animate-in fade-in duration-200">
            <div className="flex items-center gap-2 text-white font-semibold text-base border-b border-border pb-3">
              <Sparkles className="w-5 h-5 text-primary" />
              Launch Deep Market Intelligence Project
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1.5 md:col-span-2">
                <label className="text-xs font-medium text-gray-300">Project / Working Game Title</label>
                <input
                  type="text"
                  placeholder="e.g. Project Starforge: Deckbuilding In Space"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm text-white placeholder-muted-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-gray-300">Target Price (USD)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newPrice}
                  onChange={(e) => setNewPrice(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm text-white placeholder-muted-foreground focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-300">
                Core Concept &amp; Gameplay Thesis (for Autonomous Verification)
              </label>
              <textarea
                rows={3}
                placeholder="Describe your game's unique hook, target audience, core loop, and comparable reference titles..."
                value={newConcept}
                onChange={(e) => setNewConcept(e.target.value)}
                className="w-full p-3 bg-background border border-border rounded-md text-sm text-white placeholder-muted-foreground focus:outline-none focus:border-primary"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setIsCreating(false)}
                className="px-4 py-2 bg-background border border-border rounded-md text-sm text-gray-300 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleRunResearch}
                disabled={isAnalyzing || !newConcept.trim()}
                className="px-4 py-2 bg-primary text-black font-semibold rounded-md text-sm hover:bg-primary/90 transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                    Synthesizing Cohorts...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-black" />
                    Execute Autonomous Analysis
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Research Projects List */}
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              <h2 className="text-sm font-semibold text-white">Active &amp; Completed Research Dossiers</h2>
            </div>
            <span className="text-xs text-muted-foreground">{projects.length} research projects</span>
          </div>

          <div className="divide-y divide-border">
            {projects.map((proj) => (
              <div key={proj.id} className="p-5 hover:bg-accent/40 transition-colors space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span
                      className={cn(
                        "w-2.5 h-2.5 rounded-full",
                        proj.status === "completed"
                          ? "bg-emerald-400"
                          : proj.status === "running"
                          ? "bg-amber-400 animate-pulse"
                          : "bg-gray-400"
                      )}
                    />
                    <h3 className="text-base font-semibold text-white">{proj.title}</h3>
                    <span className="text-xs px-2 py-0.5 rounded bg-muted text-gray-300 border border-border">
                      {proj.genre}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-muted-foreground">
                      Target: <span className="text-white font-medium">${proj.target_price}</span>
                    </span>
                    <span className="text-muted-foreground">
                      Sample: <span className="text-white font-medium">{proj.sample_size} titles</span>
                    </span>
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary font-semibold">
                      Viability: {proj.market_viability_score}/100
                    </div>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground pl-5">{proj.summary}</p>

                <div className="flex items-center justify-between pl-5 pt-2 text-[11px] text-gray-400">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Run on {new Date(proj.created_at).toLocaleDateString()}</span>
                  </div>

                  <div className="flex items-center gap-3">
                    <Link
                      href="/ai"
                      className="text-primary hover:underline flex items-center gap-1"
                    >
                      <Bot className="w-3.5 h-3.5" /> Consult AI Analyst
                    </Link>
                    <Link
                      href="/reports"
                      className="text-gray-300 hover:text-white flex items-center gap-1"
                    >
                      <FileText className="w-3.5 h-3.5" /> Export Report
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
