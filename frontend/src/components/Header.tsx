"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, UserProfile } from "@/lib/api";
import { ShieldCheck, LogOut, User, Radio } from "lucide-react";

export function Header({ title = "Market Overview" }: { title?: string }) {
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    api.getMe().then((data) => setUser(data));
  }, []);

  const handleLogout = () => {
    api.clearToken();
    window.location.href = "/login";
  };

  return (
    <header className="h-14 border-b border-border bg-[#0b0f19]/80 backdrop-blur px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-semibold text-white tracking-wide">{title}</h2>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] bg-emerald-950/60 border border-emerald-800 text-emerald-400">
          <Radio className="w-3 h-3 animate-pulse text-emerald-400" />
          <span>System Healthy</span>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-card border border-border">
              <ShieldCheck className="w-3.5 h-3.5 text-primary" />
              <span className="text-gray-300 font-medium">{user.display_name}</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground ml-1">
                ({user.roles[0] || "viewer"})
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="p-1.5 text-gray-400 hover:text-red-400 rounded hover:bg-card transition"
              title="Cerrar sesión"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary hover:bg-primary-dark text-white font-medium transition"
          >
            <User className="w-3.5 h-3.5" />
            <span>Iniciar Sesión</span>
          </Link>
        )}
      </div>
    </header>
  );
}
