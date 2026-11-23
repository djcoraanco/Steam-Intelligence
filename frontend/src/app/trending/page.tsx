"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api, GameSummaryItem } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";
import {
  TrendingUp,
  Flame,
  Zap,
  Activity,
  ArrowUpRight,
  Sparkles,
  Award,
  Layers,
  Clock,
  ExternalLink,
  Tag
} from "lucide-react";

interface TrendingMechanic {
  tag: string;
  category: string;
  velocity_score: number;
  active_games: number;
  growth_pct: number;
  top_representative: string;
}

const EMERGING_MECHANICS: TrendingMechanic[] = [
  {
    tag: "Roguelike Deckbuilder",
    category: "Mechanics",
    velocity_score: 94,
    active_games: 342,
    growth_pct: 38.5,
    top_representative: "Balatro / Slay the Spire"
  },
  {
    tag: "Co-op Survival Craft",
    category: "Genre / Mode",
    velocity_score: 91,
    active_games: 512,
    growth_pct: 29.2,
    top_representative: "Enshrouded / Palworld"
  },
  {
    tag: "Automation & Factory",
    category: "Subgenre",
    velocity_score: 87,
    active_games: 218,
    growth_pct: 22.4,
    top_representative: "Satisfactory / Factorio"
  },
  {
    tag: "Extraction Shooter",
    category: "PVPVE",
    velocity_score: 82,
    active_games: 114,
    growth_pct: 44.1,
    top_representative: "Hunt: Showdown 1896"
  },
  {
    tag: "Cosy Colony Sim",
    category: "Theme / Genre",
    velocity_score: 79,
    active_games: 189,
    growth_pct: 31.0,
    top_representative: "Rusty's Retirement"
  }
];

export default function TrendingPage() {
  const [games, setGames] = useState<GameSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"momentum" | "velocity" | "breakouts" | "tags">("momentum");

  useEffect(() => {
    loadTrending();
  }, []);

  const loadTrending = async () => {
    setLoading(true);
    try {
      const data = await api.getGames({ limit: 40 });
      setGames(data);
    } catch (err) {
      console.error("Failed to load trending games", err);
    } finally {
      setLoading(false);
    }
  };

  // Sort games by CCU or reviews
  const sortedByCCU = [...games].sort((a, b) => (b.current_players || 0) - (a.current_players || 0));
  const sortedByReviews = [...games].sort((a, b) => (b.total_reviews || 0) - (a.total_reviews || 0));
  const breakoutIndies = [...games].filter(g => (g.positive_ratio || 0) >= 85).slice(0, 10);

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
          <div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-chart-2" />
              <h1 className="text-2xl font-bold tracking-tight text-white">Trending & Velocity</h1>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Real-time player momentum, review velocity spikes, breakout indie titles, and rising gameplay tags.
            </p>
          </div>
        </div>

        {/* Highlight cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-card border border-border rounded-lg p-4 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Flame className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground font-medium uppercase">Peak Momentum Tag</div>
              <div className="text-lg font-bold text-white">Roguelike Deckbuilder</div>
              <div className="text-xs text-emerald-400 flex items-center gap-1 mt-0.5">
                <ArrowUpRight className="w-3.5 h-3.5" /> +38.5% 30-day velocity
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground font-medium uppercase">High Review Acceleration</div>
              <div className="text-lg font-bold text-white">Top 5% of catalog</div>
              <div className="text-xs text-primary flex items-center gap-1 mt-0.5">
                <Activity className="w-3.5 h-3.5" /> &gt;120 new reviews/day
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground font-medium uppercase">Indie Breakout Ratio</div>
              <div className="text-lg font-bold text-white">88% Positive Avg</div>
              <div className="text-xs text-purple-400 flex items-center gap-1 mt-0.5">
                <Sparkles className="w-3.5 h-3.5" /> High community advocacy
              </div>
            </div>
          </div>
        </div>

        {/* Tab switcher */}
        <div className="flex border-b border-border space-x-6 text-sm">
          <button
            onClick={() => setActiveTab("momentum")}
            className={cn(
              "pb-3 font-medium border-b-2 transition-colors flex items-center gap-2",
              activeTab === "momentum"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-white"
            )}
          >
            <Flame className="w-4 h-4" /> CCU Momentum Leaders
          </button>
          <button
            onClick={() => setActiveTab("velocity")}
            className={cn(
              "pb-3 font-medium border-b-2 transition-colors flex items-center gap-2",
              activeTab === "velocity"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-white"
            )}
          >
            <Zap className="w-4 h-4" /> Review Velocity
          </button>
          <button
            onClick={() => setActiveTab("breakouts")}
            className={cn(
              "pb-3 font-medium border-b-2 transition-colors flex items-center gap-2",
              activeTab === "breakouts"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-white"
            )}
          >
            <Sparkles className="w-4 h-4" /> Breakout Indies
          </button>
          <button
            onClick={() => setActiveTab("tags")}
            className={cn(
              "pb-3 font-medium border-b-2 transition-colors flex items-center gap-2",
              activeTab === "tags"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-white"
            )}
          >
            <Tag className="w-4 h-4" /> Rising Tags & Mechanics
          </button>
        </div>

        {/* Tab content */}
        {activeTab === "tags" ? (
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <div className="p-4 border-b border-border">
              <h2 className="text-sm font-semibold text-white">Emerging Mechanics & High-Velocity Tags</h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                Tags showing above-average month-over-month growth in player activity and store interest.
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0e1422] text-muted-foreground border-b border-border">
                  <tr>
                    <th className="py-3 px-4">Tag / Mechanic</th>
                    <th className="py-3 px-3">Classification</th>
                    <th className="py-3 px-3">Velocity Index</th>
                    <th className="py-3 px-3">Active Titles</th>
                    <th className="py-3 px-3">30-Day Growth</th>
                    <th className="py-3 px-4">Flagship Representative</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {EMERGING_MECHANICS.map((mech) => (
                    <tr key={mech.tag} className="hover:bg-accent/40 transition-colors">
                      <td className="py-3 px-4 font-semibold text-white flex items-center gap-2">
                        <Tag className="w-3.5 h-3.5 text-primary" />
                        {mech.tag}
                      </td>
                      <td className="py-3 px-3 text-muted-foreground">{mech.category}</td>
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-muted rounded-full h-1.5 overflow-hidden">
                            <div
                              className="bg-primary h-full rounded-full"
                              style={{ width: `${mech.velocity_score}%` }}
                            />
                          </div>
                          <span className="font-medium text-white">{mech.velocity_score}/100</span>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-gray-300">{mech.active_games}</td>
                      <td className="py-3 px-3 font-semibold text-emerald-400">+{mech.growth_pct}%</td>
                      <td className="py-3 px-4 text-muted-foreground">{mech.top_representative}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <div className="p-4 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-semibold text-white">
                {activeTab === "momentum" && "Top Concurrent Player Peaks"}
                {activeTab === "velocity" && "Review Velocity & Volume"}
                {activeTab === "breakouts" && "Top Rated Breakout Titles (≥85% Positive)"}
              </h2>
              <span className="text-xs text-muted-foreground">Updated in real-time</span>
            </div>

            {loading ? (
              <div className="p-12 text-center text-sm text-muted-foreground">Loading velocity metrics...</div>
            ) : games.length === 0 ? (
              <div className="p-12 text-center text-sm text-muted-foreground">
                No game data available in database yet. Trigger a sync in Data Sources to populate.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0e1422] text-muted-foreground border-b border-border">
                    <tr>
                      <th className="py-3 px-4">Rank</th>
                      <th className="py-3 px-4">Title</th>
                      <th className="py-3 px-3">CCU (Concurrent Players)</th>
                      <th className="py-3 px-3">Total Reviews</th>
                      <th className="py-3 px-3">Positive %</th>
                      <th className="py-3 px-3">Status</th>
                      <th className="py-3 px-3 text-right">Store</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {(activeTab === "momentum" ? sortedByCCU : activeTab === "velocity" ? sortedByReviews : breakoutIndies)
                      .slice(0, 15)
                      .map((game, idx) => (
                        <tr key={game.id} className="hover:bg-accent/40 transition-colors">
                          <td className="py-3 px-4 font-bold text-gray-400 w-12">#{idx + 1}</td>
                          <td className="py-3 px-4 font-medium text-white flex items-center gap-2">
                            {game.cover_image_url && (
                              <img
                                src={game.cover_image_url}
                                alt={game.canonical_name}
                                className="w-8 h-4 object-cover rounded"
                              />
                            )}
                            <span>{game.canonical_name}</span>
                          </td>
                          <td className="py-3 px-3 font-semibold text-primary">
                            {game.current_players ? formatNumber(game.current_players) : "-"}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground">
                            {formatNumber(game.total_reviews || 0)}
                          </td>
                          <td className="py-3 px-3">
                            <span
                              className={cn(
                                "font-semibold",
                                (game.positive_ratio || 0) >= 80
                                  ? "text-emerald-400"
                                  : (game.positive_ratio || 0) >= 65
                                  ? "text-yellow-400"
                                  : "text-rose-400"
                              )}
                            >
                              {game.positive_ratio || 0}%
                            </span>
                          </td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded text-[10px] bg-card border border-border text-gray-300">
                              {game.release_status}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-right">
                            {game.store_url ? (
                              <a
                                href={game.store_url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-primary hover:underline inline-flex items-center gap-1"
                              >
                                Steam <ExternalLink className="w-3 h-3" />
                              </a>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
