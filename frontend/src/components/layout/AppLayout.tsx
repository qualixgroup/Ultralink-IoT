import { Outlet } from "react-router-dom";
import { useState } from "react";
import { Menu, Search, X } from "lucide-react";

import { Sidebar } from "./Sidebar";
import { StatusPill } from "../ui/StatusPill";

export function AppLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[18rem_1fr]">
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {mobileMenuOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/60"
            aria-label="Fechar menu"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative h-full w-[min(20rem,86vw)]">
            <Sidebar />
            <button
              type="button"
              className="absolute right-3 top-3 grid h-9 w-9 place-items-center rounded-lg border border-white/10 bg-black/40 text-slate-200"
              aria-label="Fechar menu"
              onClick={() => setMobileMenuOpen(false)}
            >
              <X className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </div>
      ) : null}

      <main className="min-w-0">
        <header className="sticky top-0 z-20 border-b border-white/10 bg-[#070a0f]/80 px-4 py-3 backdrop-blur-xl sm:px-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <button
                type="button"
                className="grid h-10 w-10 place-items-center rounded-lg border border-white/10 text-slate-300 lg:hidden"
                aria-label="Abrir menu"
                onClick={() => setMobileMenuOpen(true)}
              >
                <Menu className="h-5 w-5" aria-hidden="true" />
              </button>
              <div className="min-w-0">
                <p className="truncate text-sm text-slate-500">Ultralink Monitor</p>
                <h1 className="truncate text-xl font-semibold tracking-normal text-white sm:text-2xl">Operação IoT</h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <label className="hidden items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-400 md:flex">
                <Search className="h-4 w-4" aria-hidden="true" />
                <input
                  className="w-48 bg-transparent text-slate-200 outline-none placeholder:text-slate-600"
                  placeholder="Buscar ativo"
                  type="search"
                />
              </label>
              <StatusPill tone="success">API online</StatusPill>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
