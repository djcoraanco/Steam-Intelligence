"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { ShieldCheck, Lock, Mail, User, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        // Register user
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            password,
            display_name: displayName || undefined,
            role: "owner"
          }),
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || "Error en el registro");
        }
      }

      // Login
      const loginRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!loginRes.ok) {
        const errData = await loginRes.json();
        throw new Error(errData.detail || "Credenciales incorrectas");
      }

      const tokenData = await loginRes.json();
      api.setToken(tokenData.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Error al procesar la solicitud");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md bg-card border border-border rounded-xl p-8 shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-lg bg-primary/20 border border-primary/40 text-primary font-bold text-xl flex items-center justify-center mx-auto">
            SI
          </div>
          <h1 className="text-lg font-bold text-white tracking-wide">STEAM INTELLIGENCE</h1>
          <p className="text-xs text-muted-foreground">
            {isRegister
              ? "Registrar cuenta de propietario (Owner Bootstrap)"
              : "Ingreso seguro a la plataforma de inteligencia de mercado"}
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {isRegister && (
            <div className="space-y-1.5">
              <label className="text-gray-300 font-medium">Nombre Completo</label>
              <div className="relative">
                <User className="w-4 h-4 text-gray-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="Ej. Andrés Analyst"
                  className="w-full bg-[#0b0f19] border border-border rounded-lg pl-9 pr-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:border-primary transition"
                />
              </div>
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-gray-300 font-medium">Correo Electrónico</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-500 absolute left-3 top-2.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@steamintel.internal"
                className="w-full bg-[#0b0f19] border border-border rounded-lg pl-9 pr-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:border-primary transition"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-gray-300 font-medium">Contraseña</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-500 absolute left-3 top-2.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-[#0b0f19] border border-border rounded-lg pl-9 pr-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:border-primary transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-primary-dark text-white font-medium py-2.5 rounded-lg transition disabled:opacity-50 mt-2 flex items-center justify-center gap-2"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{loading ? "Procesando..." : isRegister ? "Crear Propietario" : "Iniciar Sesión"}</span>
          </button>
        </form>

        <div className="pt-4 border-t border-border/80 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-xs text-primary hover:text-sky-300 transition"
          >
            {isRegister
              ? "¿Ya tienes cuenta? Iniciar Sesión"
              : "¿Primera instalación? Registrar cuenta de Propietario"}
          </button>
        </div>
      </div>
    </div>
  );
}
