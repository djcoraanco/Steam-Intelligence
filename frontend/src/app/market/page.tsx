"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api, GameSummaryItem } from "@/lib/api";
import { cn, formatNumber, formatPrice } from "@/lib/utils";
import {
  Compass,
  Search,
  Filter,
  DollarSign,
  Layers,
  PieChart,
  BarChart3,
  ExternalLink,
  Sparkles,
  TrendingUp,
  Percent,
  Gamepad2,
  AlertCircle
} from "lucide-react";

const PRICE_TIERS = [
  { id: "all", label: "All Prices" },
  { id: "free", label: "Free-to-Play ($0)" },
  { id: "tier1", label: "$0.99 - $9.99" },
  { id: "tier2", label: "$10.00 - $19.99" },
  { id: "tier3", label: "$20.00 - $29.99" },
  { id: "tier4", label: "$30.00+" },
];

const GENRES = ["All", "Action", "RPG", "Strategy", "Indie", "Simulation", "Adventure", "Casual"];

export default function MarketExplorerPage() {
  const [games, setGames] = useState<GameSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("All");
  const [selectedPriceTier, setSelectedPriceTier] = useState("all");
  const [onlyEarlyAccess, setOnlyEarlyAccess] = useState(false);

  useEffect(() => {
    loadGames();
  }, [search]);

  const loadGames = async () => {
    setLoading(true);
    try {
      const data = await api.getGames({ limit: 50, search: search || undefined });
      setGames(data);
    } catch (err) {
      console.error("Failed to load games for market explorer", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredGames = games.filter((g) => {
    if (onlyEarlyAccess && !g.is_early_access) return false;
    if (selectedPriceTier === "free" && !g.is_free && (g.price_cents || 0) > 0) return false;
    if (selectedPriceTier === "tier1" && ((g.price_cents || 0) < 99 || (g.price_cents || 0) > 999)) return false;
    if (selectedPriceTier === "tier2" && ((g.price_cents || 0) < 1000 || (g.price_cents || 0) > 1999)) return false;
    if (selectedPriceTier === "tier3" && ((g.price_cents || 0) < 2000 || (g.price_cents || 0) > 2999)) return false;
    if (selectedPriceTier === "tier4" && (g.price_cents || 0) < 3000) return false;
    return true;
  });

  const totalReviews = filteredGames.reduce((acc, g) => acc + (g.total_reviews || 0), 0);
  const avgPositiveRatio = filteredGames.length > 0
    ? Math.round(filteredGames.reduce((acc, g) => acc + (g.positive_ratio || 0), 0) / filteredGames.length)
    : 0;
  const earlyAccessCount = filteredGames.filter(g => g.is_early_access).length;
  const eaPercentage = filteredGames.length > 0 ? Math.round((earlyAccessCount / filteredGames.length) * 100) : 0;

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
          <div>
            <div className="flex items-center gap-2">
              <Compass className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold tracking-tight text-white">Market Explorer</h1>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Macro market analysis, price tiers, distribution, and revenue percentiles based on Steamworks data.
            </p>
          </div>
        </div>

        {/* Macro KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>GAMES IN VIEW</span>
              <Gamepad2 className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-bold text-white">{filteredGames.length}</div>
            <div className="text-[11px] text-muted-foreground mt-1">Active sample size</div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>TOTAL REVIEWS IN SAMPLE</span>
              <TrendingUp className="w-4 h-4 text-chart-2" />
            </div>
            <div className="text-2xl font-bold text-white">{formatNumber(totalReviews)}</div>
            <div className="text-[11px] text-muted-foreground mt-1">Boxleiter base proxy</div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>AVG POSITIVE SENTIMENT</span>
              <Percent className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400">{avgPositiveRatio}%</div>
            <div className="text-[11px] text-muted-foreground mt-1">Customer satisfaction</div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between text-muted-foreground text-xs font-medium mb-1">
              <span>EARLY ACCESS SHARE</span>
              <Layers className="w-4 h-4 text-chart-4" />
            </div>
            <div className="text-2xl font-bold text-white">{eaPercentage}%</div>
            <div className="text-[11px] text-muted-foreground mt-1">{earlyAccessCount} games in EA</div>
          </div>
        </div>

        {/* Filters bar */}
        <div className="bg-card border border-border rounded-lg p-4 space-y-4">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search games by title or appid..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-md text-sm text-white placeholder-muted-foreground focus:outline-none focus:border-primary"
              />
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setOnlyEarlyAccess(!onlyEarlyAccess)}
                className={cn(
                  "px-3 py-2 text-xs font-medium rounded-md border transition-colors flex items-center gap-1.5",
                  onlyEarlyAccess
                    ? "bg-primary/20 text-primary border-primary/40"
                    : "bg-background text-muted-foreground border-border hover:text-white"
                )}
              >
                <Layers className="w-3.5 h-3.5" />
                Only Early Access
              </button>
            </div>
          </div>

          {/* Price Tier Buttons */}
          <div className="flex items-center gap-2 flex-wrap border-t border-border pt-3">
            <span className="text-xs text-muted-foreground mr-1 flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5" /> Price Tier:
            </span>
            {PRICE_TIERS.map((tier) => (
              <button
                key={tier.id}
                onClick={() => setSelectedPriceTier(tier.id)}
                className={cn(
                  "px-2.5 py-1 text-xs rounded-full border transition-colors",
                  selectedPriceTier === tier.id
                    ? "bg-primary text-black font-semibold border-primary"
                    : "bg-background text-muted-foreground border-border hover:border-gray-500 hover:text-white"
                )}
              >
                {tier.label}
              </button>
            ))}
          </div>
        </div>

        {/* Games Table */}
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-primary" />
              Market Titles & Estimates ({filteredGames.length})
            </h2>
            <span className="text-xs text-muted-foreground">Boxleiter multiplier standard: 30x</span>
          </div>

          {loading ? (
            <div className="p-12 text-center text-sm text-muted-foreground">
              Loading market data...
            </div>
          ) : filteredGames.length === 0 ? (
            <div className="p-12 text-center text-sm text-muted-foreground">
              No titles match the selected filters. Try searching for a different keyword or resetting price tier.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0e1422] text-muted-foreground border-b border-border font-medium">
                  <tr>
                    <th className="py-3 px-4">Title</th>
                    <th className="py-3 px-3">Price</th>
                    <th className="py-3 px-3">Reviews</th>
                    <th className="py-3 px-3">Positive %</th>
                    <th className="py-3 px-3">Est. Owners (30x)</th>
                    <th className="py-3 px-3">Est. Gross Revenue</th>
                    <th className="py-3 px-3">Type / Status</th>
                    <th className="py-3 px-3 text-right">Store Link</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredGames.map((game) => {
                    const price = (game.price_cents || 0) / 100;
                    const reviews = game.total_reviews || 0;
                    const estimatedOwners = reviews * 30;
                    const estimatedRevenue = estimatedOwners * price;

                    return (
                      <tr key={game.id} className="hover:bg-accent/40 transition-colors">
                        <td className="py-3 px-4 font-medium text-white flex items-center gap-2">
                          {game.cover_image_url && (
                            <img
                              src={game.cover_image_url}
                              alt={game.canonical_name}
                              className="w-8 h-4 object-cover rounded"
                            />
                          )}
                          <span>{game.canonical_name}</span>
                          {game.is_early_access && (
                            <span className="px-1.5 py-0.5 text-[10px] bg-amber-500/20 text-amber-300 rounded border border-amber-500/30">
                              EA
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-white">
                          {game.is_free ? "Free" : formatPrice(game.price_cents || 0, game.currency)}
                        </td>
                        <td className="py-3 px-3 text-muted-foreground">{formatNumber(reviews)}</td>
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
                        <td className="py-3 px-3 text-gray-300">~{formatNumber(estimatedOwners)}</td>
                        <td className="py-3 px-3 text-emerald-400 font-medium">
                          {game.is_free ? "$0" : `$${formatNumber(Math.round(estimatedRevenue))}`}
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
                              className="inline-flex items-center gap-1 text-primary hover:underline"
                            >
                              Steam <ExternalLink className="w-3 h-3" />
                            </a>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
