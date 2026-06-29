import { Link, NavLink, useNavigate } from "react-router-dom";
import { Bell, Bot, Building2, Gauge, GitBranch, LayoutDashboard, LogOut, RadioTower, Settings, Shield } from "lucide-react";
import { clsx } from "clsx";

import { clearToken } from "../../lib/auth";

const navItems = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Dispositivos", href: "/devices", icon: RadioTower },
  { label: "Alertas", href: "/alerts", icon: Bell },
  { label: "Empresas", href: "/companies", icon: Building2 },
  { label: "Automações", href: "/workflows", icon: GitBranch },
  { label: "IA", href: "/ai", icon: Bot },
  { label: "Integrações", href: "/integrations", icon: Settings },
];

export function Sidebar() {
  const navigate = useNavigate();

  function handleLogout() {
    clearToken();
    navigate("/login", { replace: true });
  }

  return (
    <aside className="flex h-full w-full flex-col border-r border-white/10 bg-black/25 px-3 py-4 backdrop-blur-xl lg:w-72">
      <Link to="/" className="mb-6 flex items-center gap-3 px-2">
        <div className="grid h-11 w-11 place-items-center rounded-lg bg-cyan-400/15 text-cyan-200 ring-1 ring-cyan-300/25">
          <Shield className="h-5 w-5" aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold uppercase text-cyan-100">Ultralink IoT</p>
          <p className="truncate text-xs text-slate-500">Monitor corporativo</p>
        </div>
      </Link>

      <nav className="flex-1 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={`${item.label}-${item.href}`}
            to={item.href}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-400 transition hover:bg-white/10 hover:text-white",
                isActive ? "bg-cyan-400/10 text-cyan-100" : "",
              )
            }
          >
            <item.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
            <span className="truncate">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="rounded-lg border border-white/10 bg-panelMuted p-3">
        <div className="mb-3 flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-lg bg-emerald-400/10 text-emerald-200">
            <Gauge className="h-4 w-4" aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-slate-100">ThingsBoard interno</p>
            <p className="truncate text-xs text-slate-500">Oculto do cliente final</p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-300 transition hover:border-rose-300/30 hover:bg-rose-400/10 hover:text-rose-100"
        >
          <LogOut className="h-4 w-4" aria-hidden="true" />
          Sair
        </button>
      </div>
    </aside>
  );
}
