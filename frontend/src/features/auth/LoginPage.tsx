import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, ShieldCheck, Wifi } from "lucide-react";

import { apiRequest } from "../../lib/api";
import { setToken } from "../../lib/auth";

type LoginResponse = {
  access_token: string;
};

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@ultralink.io");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await apiRequest<LoginResponse>("/auth/login", {
        method: "POST",
        authenticated: false,
        body: JSON.stringify({ email, password }),
      });
      setToken(data.access_token);
      navigate("/", { replace: true });
    } catch {
      setError("Credenciais inválidas ou API indisponível.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 py-8">
      <section className="grid w-full max-w-5xl overflow-hidden rounded-lg border border-white/10 bg-panel shadow-glow lg:grid-cols-[1.05fr_0.95fr]">
        <div className="relative min-h-[28rem] overflow-hidden bg-[#071016] p-8">
          <div className="absolute inset-0 opacity-70">
            <div className="absolute left-8 top-10 h-28 w-28 rounded-full border border-cyan-300/20" />
            <div className="absolute bottom-10 right-10 h-40 w-40 rounded-full border border-emerald-300/15" />
            <div className="absolute inset-x-8 top-1/2 h-px bg-cyan-200/20" />
            <div className="absolute left-1/3 top-16 h-[70%] w-px bg-emerald-200/10" />
          </div>
          <div className="relative flex h-full flex-col justify-between">
            <div>
              <div className="mb-8 inline-flex items-center gap-2 rounded-lg border border-cyan-300/20 bg-cyan-300/10 px-3 py-2 text-sm text-cyan-100">
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
                Ultralink Monitor
              </div>
              <h1 className="max-w-md text-4xl font-semibold tracking-normal text-white sm:text-5xl">Operação IoT corporativa em tempo real</h1>
            </div>

            <div className="grid grid-cols-3 gap-3">
              {["Torres", "Geradores", "Sensores"].map((item) => (
                <div key={item} className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <Wifi className="mb-3 h-4 w-4 text-cyan-200" aria-hidden="true" />
                  <p className="truncate text-sm text-slate-200">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col justify-center p-6 sm:p-10">
          <div className="mb-8">
            <p className="text-sm font-medium text-cyan-200">Acesso seguro</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-normal text-white">Entrar na plataforma</h2>
          </div>

          <label className="mb-4 block">
            <span className="mb-2 block text-sm text-slate-400">E-mail</span>
            <span className="flex items-center gap-3 rounded-lg border border-white/10 bg-black/20 px-3 py-3">
              <Mail className="h-4 w-4 text-slate-500" aria-hidden="true" />
              <input
                className="w-full bg-transparent text-white outline-none"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                autoComplete="email"
                required
              />
            </span>
          </label>

          <label className="mb-3 block">
            <span className="mb-2 block text-sm text-slate-400">Senha</span>
            <span className="flex items-center gap-3 rounded-lg border border-white/10 bg-black/20 px-3 py-3">
              <Lock className="h-4 w-4 text-slate-500" aria-hidden="true" />
              <input
                className="w-full bg-transparent text-white outline-none"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type="password"
                autoComplete="current-password"
                required
              />
            </span>
          </label>

          {error ? <p className="mb-3 rounded-lg border border-rose-400/20 bg-rose-400/10 px-3 py-2 text-sm text-rose-100">{error}</p> : null}

          <button
            type="submit"
            disabled={loading}
            className="mt-3 rounded-lg bg-cyan-300 px-4 py-3 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loading ? "Autenticando..." : "Entrar"}
          </button>
        </form>
      </section>
    </main>
  );
}
