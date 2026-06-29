import { clsx } from "clsx";

type StatusPillProps = {
  tone: "success" | "danger" | "warning" | "neutral";
  children: React.ReactNode;
};

const toneClass = {
  success: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  danger: "border-rose-400/30 bg-rose-400/10 text-rose-200",
  warning: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  neutral: "border-slate-400/25 bg-slate-400/10 text-slate-200",
};

export function StatusPill({ tone, children }: StatusPillProps) {
  return (
    <span className={clsx("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium", toneClass[tone])}>
      {children}
    </span>
  );
}
