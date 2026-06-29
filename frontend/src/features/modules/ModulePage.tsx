import { Activity, Construction, Database, ShieldCheck } from "lucide-react";

import { StatusPill } from "../../components/ui/StatusPill";

type ModulePageProps = {
  title: string;
  description: string;
};

export function ModulePage({ title, description }: ModulePageProps) {
  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm text-slate-500">Módulo</p>
          <h2 className="text-2xl font-semibold tracking-normal text-white">{title}</h2>
        </div>
        <StatusPill tone="neutral">Estrutura inicial</StatusPill>
      </div>

      <div className="rounded-lg border border-white/10 bg-panel p-5 shadow-glow">
        <p className="max-w-3xl text-sm leading-6 text-slate-400">{description}</p>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {[
            { label: "API protegida", icon: ShieldCheck },
            { label: "Banco relacional", icon: Database },
            { label: "Eventos operacionais", icon: Activity },
          ].map((item) => (
            <div key={item.label} className="rounded-lg border border-white/10 bg-white/5 p-4">
              <item.icon className="mb-4 h-5 w-5 text-cyan-200" aria-hidden="true" />
              <p className="text-sm font-medium text-slate-100">{item.label}</p>
            </div>
          ))}
        </div>
        <div className="mt-5 flex items-center gap-3 rounded-lg border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100">
          <Construction className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span>Pronto para receber telas CRUD e permissões por perfil.</span>
        </div>
      </div>
    </section>
  );
}
