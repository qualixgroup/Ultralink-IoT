import type { LucideIcon } from "lucide-react";

type StatCardProps = {
  title: string;
  value: number | string;
  icon: LucideIcon;
  accent: string;
  detail: string;
};

export function StatCard({ title, value, icon: Icon, accent, detail }: StatCardProps) {
  return (
    <article className="rounded-lg border border-white/10 bg-panel p-4 shadow-glow">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm text-slate-400">{title}</p>
          <strong className="mt-2 block text-3xl font-semibold tracking-normal text-white">{value}</strong>
        </div>
        <div className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${accent}`}>
          <Icon className="h-5 w-5" aria-hidden="true" />
        </div>
      </div>
      <p className="mt-4 text-xs text-slate-500">{detail}</p>
    </article>
  );
}
