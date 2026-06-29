import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BatteryCharging, Container, RadioTower, SatelliteDish, ServerCrash, Signal, TowerControl } from "lucide-react";

import { StatCard } from "../../components/ui/StatCard";
import { StatusPill } from "../../components/ui/StatusPill";
import { apiRequest } from "../../lib/api";

type DashboardSummary = {
  online: number;
  offline: number;
  alerts: number;
  towers: number;
  generators: number;
  tanks: number;
  sensors: number;
};

const fallbackSummary: DashboardSummary = {
  online: 128,
  offline: 9,
  alerts: 17,
  towers: 24,
  generators: 18,
  tanks: 31,
  sensors: 64,
};

const statConfig = [
  { key: "online", title: "Equipamentos Online", icon: Signal, accent: "bg-emerald-400/10 text-emerald-200", detail: "Última sincronização há 2 min" },
  { key: "offline", title: "Equipamentos Offline", icon: ServerCrash, accent: "bg-rose-400/10 text-rose-200", detail: "Aguardando reconexão" },
  { key: "alerts", title: "Alertas", icon: AlertTriangle, accent: "bg-amber-400/10 text-amber-200", detail: "Eventos abertos" },
  { key: "towers", title: "Torres", icon: TowerControl, accent: "bg-cyan-400/10 text-cyan-200", detail: "Sites monitorados" },
  { key: "generators", title: "Geradores", icon: BatteryCharging, accent: "bg-lime-400/10 text-lime-200", detail: "Energia crítica" },
  { key: "tanks", title: "Tanques", icon: Container, accent: "bg-sky-400/10 text-sky-200", detail: "Nível e volume" },
  { key: "sensors", title: "Sensores", icon: SatelliteDish, accent: "bg-violet-400/10 text-violet-200", detail: "Telemetria ativa" },
] as const;

export function DashboardPage() {
  const { data = fallbackSummary, isError } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => apiRequest<DashboardSummary>("/dashboards/summary"),
  });

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm text-slate-500">Visão geral</p>
          <h2 className="text-2xl font-semibold tracking-normal text-white">Monitoramento corporativo</h2>
        </div>
        <StatusPill tone={isError ? "warning" : "success"}>{isError ? "Dados demonstrativos" : "Dados ao vivo"}</StatusPill>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statConfig.map((item) => (
          <StatCard
            key={item.key}
            title={item.title}
            value={data[item.key]}
            icon={item.icon}
            accent={item.accent}
            detail={item.detail}
          />
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-lg border border-white/10 bg-panel p-4 shadow-glow">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold tracking-normal text-white">Mapa operacional</h3>
              <p className="text-sm text-slate-500">Placeholder geográfico</p>
            </div>
            <StatusPill tone="neutral">Mapa</StatusPill>
          </div>

          <div className="relative h-80 overflow-hidden rounded-lg border border-white/10 bg-[#071016]">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(125,211,252,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(125,211,252,0.08)_1px,transparent_1px)] bg-[size:36px_36px]" />
            {[
              ["left-[18%] top-[28%]", "bg-emerald-300"],
              ["left-[42%] top-[46%]", "bg-cyan-300"],
              ["left-[66%] top-[35%]", "bg-amber-300"],
              ["left-[76%] top-[62%]", "bg-rose-300"],
            ].map(([position, color]) => (
              <span key={position} className={`absolute ${position} h-4 w-4 rounded-full ${color} shadow-[0_0_22px_currentColor] ring-4 ring-white/10`} />
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-panel p-4 shadow-glow">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold tracking-normal text-white">Telemetria</h3>
              <p className="text-sm text-slate-500">Placeholder de série temporal</p>
            </div>
            <StatusPill tone="success">MQTT/API</StatusPill>
          </div>

          <div className="relative h-80 overflow-hidden rounded-lg border border-white/10 bg-[#08111b] p-5">
            <div className="absolute inset-x-5 bottom-5 top-5 border-l border-b border-white/10" />
            <div className="telemetry-line absolute inset-x-5 bottom-5 top-8 bg-cyan-300/25" />
            <div className="absolute inset-x-5 bottom-5 top-8 border-t border-cyan-200/60" />
            <div className="relative grid h-full grid-cols-4 items-end gap-3">
              {[42, 68, 51, 76].map((height, index) => (
                <div key={height} className="flex h-full items-end">
                  <span className="w-full rounded-t bg-emerald-300/25" style={{ height: `${height}%` }} />
                  <span className="sr-only">Amostra {index + 1}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
