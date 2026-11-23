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
      // Token invalid or expired
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

  getMe: async (): Promise<UserProfile | null> => {
    try {
      const res = await api.fetchWithAuth("/api/v1/auth/me");
      if (!res.ok) return null;
      return res.json();
    } catch {
      return null;
    }
  },
};
