import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

export function KpiCard({
  label,
  value,
  change,
  icon: Icon,
  tone = "teal",
}: {
  label: string;
  value: string;
  change: string;
  icon: LucideIcon;
  tone?: "teal" | "blue" | "amber" | "emerald" | "red";
}) {
  const tones = {
    teal: "bg-teal-50 text-teal-700",
    blue: "bg-blue-50 text-blue-700",
    amber: "bg-amber-50 text-amber-700",
    emerald: "bg-emerald-50 text-emerald-700",
    red: "bg-red-50 text-red-700",
  };

  return (
    <section className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
          <p className="mt-2 text-xs text-slate-500">{change}</p>
        </div>
        <span className={cn("rounded-md p-2", tones[tone])}>
          <Icon className="size-5" aria-hidden="true" />
        </span>
      </div>
    </section>
  );
}
