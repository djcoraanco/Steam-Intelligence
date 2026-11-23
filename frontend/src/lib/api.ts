const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  roles: string[];
  is_active: boolean;
}

export interface DashboardOverview {
  indexed_games_count: number;
  monitored_games_count: number;
  active_sources_count: number;
  latest_observation_at: string | null;
  data_freshness_status: string;
  top_games: Array<{
    game_id: string;
    canonical_name: string;
    steam_appid?: string;
    cover_image_url?: string;
    current_players?: number;
    availability_status: string;
  }>;
  rising_genres: Array<{
    genre: string;
    growth_pct: number;
    active_games: number;
  }>;
  detected_niches_count: number;
  active_research_runs_count: number;
}

export interface DataSourceItem {
  id: string;
  code: string;
  name: string;
  provider_type: string;
  status: string;
  capabilities: string[];
  base_url?: string;
  documentation_url?: string;
  terms_url?: string;
  last_verified_at?: string;
}

export interface GameSummaryItem {
  id: string;
  canonical_name: string;
  slug?: string;
  release_date?: string;
  release_date_precision?: string;
  release_status: string;
  game_type: string;
  is_early_access: boolean;
  cover_image_url?: string;
  steam_appid?: string;
  store_url?: string;
  current_players?: number;
  positive_ratio?: number;
  total_reviews?: number;
  price_cents?: number;
  currency: string;
  is_free: boolean;
  availability_status: string;
  last_seen_at?: string;
}

export interface GameDetailItem extends GameSummaryItem {
  description?: string;
  short_description?: string;
  website_url?: string;
  regular_price_cents?: number;
  final_price_cents?: number;
  discount_percent?: number;
  price_status: string;
  developers: string[];
  publishers: string[];
  genres: string[];
  created_at: string;
  updated_at: string;
}

export interface CatalogStatus {
  provider_code: string;
  last_cursor?: string;
  total_records: number;
  status: string;
  last_synced_at?: string;
  error_message?: string;
}

export const api = {
  getToken: () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("steam_intel_token");
    }
    return null;
  },

  setToken: (token: string) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("steam_intel_token", token);
    }
  },

  clearToken: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("steam_intel_token");
    }
  },

  fetchWithAuth: async (endpoint: string, options: RequestInit = {}) => {
    const token = api.getToken();
    const headers = new Headers(options.headers || {});
    headers.set("Content-Type", "application/json");
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 401 && typeof window !== "undefined") {
      api.clearToken();
    }

    return res;
  },

  getHealth: async () => {
    const res = await fetch(`${API_BASE_URL}/api/v1/health`);
    return res.json();
  },

  getOverview: async (): Promise<DashboardOverview> => {
    const res = await api.fetchWithAuth("/api/v1/dashboard/overview");
    if (!res.ok) throw new Error("Failed to load dashboard overview");
    return res.json();
  },

  getSources: async (): Promise<DataSourceItem[]> => {
    const res = await api.fetchWithAuth("/api/v1/sources");
    if (!res.ok) throw new Error("Failed to load data sources");
    return res.json();
  },

  testSource: async (code: string) => {
    const res = await api.fetchWithAuth(`/api/v1/sources/${code}/test`, {
      method: "POST",
    });
    return res.json();
  },

  getCatalogStatus: async (): Promise<CatalogStatus> => {
    const res = await api.fetchWithAuth("/api/v1/catalog/status");
    if (!res.ok) throw new Error("Failed to get catalog status");
    return res.json();
  },

  triggerCatalogSync: async (maxResults: number = 1000) => {
    const res = await api.fetchWithAuth("/api/v1/catalog/sync", {
      method: "POST",
      body: JSON.stringify({ max_results: maxResults, resume: true }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Catalog sync failed");
    }
    return res.json();
  },

  getGames: async (params: { limit?: number; offset?: number; search?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.limit) query.set("limit", params.limit.toString());
    if (params.offset) query.set("offset", params.offset.toString());
    if (params.search) query.set("search", params.search);

    const res = await api.fetchWithAuth(`/api/v1/games?${query.toString()}`);
    if (!res.ok) throw new Error("Failed to load games list");
    return res.json();
  },

  getGameDetail: async (id: string): Promise<GameDetailItem> => {
    const res = await api.fetchWithAuth(`/api/v1/games/${id}`);
    if (!res.ok) throw new Error("Failed to load game detail");
    return res.json();
  },

  syncGameMetadata: async (id: string) => {
    const res = await api.fetchWithAuth(`/api/v1/games/${id}/sync-metadata`, {
      method: "POST",
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Metadata sync failed");
    }
    return res.json();
  },

  getMe: async (): Promise<UserProfile | null> => {
    try {
      const res = await api.fetchWithAuth("/api/v1/auth/me");
      if (!res.ok) return null;
      return res.json();
    } catch {
      return null;
    }
  },

  getNiches: async (params: { confidence?: string; min_score?: number } = {}) => {
    const query = new URLSearchParams();
    if (params.confidence) query.set("confidence", params.confidence);
    if (params.min_score) query.set("min_score", params.min_score.toString());

    const res = await api.fetchWithAuth(`/api/v1/niches?${query.toString()}`);
    if (!res.ok) throw new Error("Failed to load niches");
    return res.json();
  },

  runNicheAnalysis: async () => {
    const res = await api.fetchWithAuth("/api/v1/niches/analyze", {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to run niche analysis");
    return res.json();
  },

  getSegmentRollups: async (segmentType: string = "genre") => {
    const res = await api.fetchWithAuth(`/api/v1/analytics/segments?segment_type=${segmentType}`);
    if (!res.ok) throw new Error("Failed to load segment rollups");
    return res.json();
  },

  computeRollups: async () => {
    const res = await api.fetchWithAuth("/api/v1/analytics/compute-rollups", {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to compute rollups");
    return res.json();
  },

  snapshotPlayers: async (gameId: string) => {
    const res = await api.fetchWithAuth(`/api/v1/games/${gameId}/snapshot-players`, {
      method: "POST",
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Player snapshot failed");
    }
    return res.json();
  },

  getGameHistory: async (gameId: string) => {
    const res = await api.fetchWithAuth(`/api/v1/games/${gameId}/history`);
    if (!res.ok) throw new Error("Failed to load game history");
    return res.json();
  },

  // Phase 7: Competitors & Review Mining
  getCompetitorSuggestions: async (gameId: string) => {
    const res = await api.fetchWithAuth(`/api/v1/competitors/suggestions/${gameId}`);
    if (!res.ok) throw new Error("Failed to load competitor suggestions");
    return res.json();
  },

  getLinkedCompetitors: async (gameId: string) => {
    const res = await api.fetchWithAuth(`/api/v1/competitors/${gameId}`);
    if (!res.ok) throw new Error("Failed to load linked competitors");
    return res.json();
  },

  compareGames: async (gameIdA: string, gameIdB: string) => {
    const res = await api.fetchWithAuth(`/api/v1/competitors/compare/${gameIdA}/${gameIdB}`);
    if (!res.ok) throw new Error("Failed to compare games");
    return res.json();
  },

  getReviewsMining: async (gameId: string) => {
    const res = await api.fetchWithAuth(`/api/v1/reviews-mining/${gameId}`);
    if (!res.ok) throw new Error("Failed to mine reviews");
    return res.json();
  },

  // Phase 8: PC Expansion
  getStoreRegistry: async () => {
    const res = await api.fetchWithAuth("/api/v1/cross-platform/stores");
    if (!res.ok) throw new Error("Failed to load PC stores registry");
    return res.json();
  },

  getCrossReferences: async (gameId: string) => {
    const res = await api.fetchWithAuth(`/api/v1/cross-platform/${gameId}`);
    if (!res.ok) throw new Error("Failed to load cross-platform references");
    return res.json();
  },

  linkCrossPlatform: async (payload: {
    game_id: string;
    platform_code: string;
    external_id: string;
    external_title: string;
    store_url?: string;
    match_confidence?: string;
  }) => {
    const res = await api.fetchWithAuth("/api/v1/cross-platform/link", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to link cross-platform game");
    return res.json();
  },

  // Phase 9: Seasonality & Release Calendar
  getIndustryEvents: async () => {
    const res = await api.fetchWithAuth("/api/v1/seasonality/events");
    if (!res.ok) throw new Error("Failed to load industry events");
    return res.json();
  },

  getCohorts: async (dimension: string = "release_year") => {
    const res = await api.fetchWithAuth(`/api/v1/seasonality/cohorts?dimension=${dimension}`);
    if (!res.ok) throw new Error("Failed to load cohorts analysis");
    return res.json();
  },

  analyzeLaunchCollision: async (targetDate: string, daysWindow: number = 14) => {
    const res = await api.fetchWithAuth(
      `/api/v1/seasonality/launch-collision?target_date=${targetDate}&days_window=${daysWindow}`
    );
    if (!res.ok) throw new Error("Failed to analyze launch collision");
    return res.json();
  },

  // Phase 10: AI Research Layer & Report Exports
  queryAI: async (question: string, targetGenre: string = "Action", targetGameId?: string) => {
    const res = await api.fetchWithAuth("/api/v1/ai/query", {
      method: "POST",
      body: JSON.stringify({ question, target_genre: targetGenre, target_game_id: targetGameId }),
    });
    if (!res.ok) throw new Error("Failed to query AI analyst");
    return res.json();
  },

  validateConcept: async (conceptDescription: string, genres: string[] = ["Indie"]) => {
    const res = await api.fetchWithAuth("/api/v1/ai/validate-concept", {
      method: "POST",
      body: JSON.stringify({ concept_description: conceptDescription, genres }),
    });
    if (!res.ok) throw new Error("Failed to validate game concept");
    return res.json();
  },

  exportReport: async (format: string, genre: string = "Action", customTitle?: string) => {
    const res = await api.fetchWithAuth("/api/v1/reports/export", {
      method: "POST",
      body: JSON.stringify({ format, genre, custom_title: customTitle }),
    });
    if (!res.ok) throw new Error("Failed to generate export");
    return res.json();
  },
};
