import { cn } from "@/lib/utils";

const statusStyles: Record<string, string> = {
  Active: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Healthy: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Fulfilled: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Shipped: "border-emerald-200 bg-emerald-50 text-emerald-700",
  New: "border-teal-200 bg-teal-50 text-teal-700",
  Reviewed: "border-sky-200 bg-sky-50 text-sky-700",
  Accepted: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Processing: "border-sky-200 bg-sky-50 text-sky-700",
  Picking: "border-sky-200 bg-sky-50 text-sky-700",
  Packed: "border-blue-200 bg-blue-50 text-blue-700",
  Confirmed: "border-blue-200 bg-blue-50 text-blue-700",
  Pending: "border-amber-200 bg-amber-50 text-amber-700",
  "Ready to Pick": "border-amber-200 bg-amber-50 text-amber-700",
  "Low Stock": "border-amber-200 bg-amber-50 text-amber-700",
  "Stockout Risk": "border-red-200 bg-red-50 text-red-700",
  "Out of Stock": "border-red-200 bg-red-50 text-red-700",
  Exception: "border-red-200 bg-red-50 text-red-700",
  Cancelled: "border-zinc-200 bg-zinc-100 text-zinc-600",
  Inactive: "border-zinc-200 bg-zinc-100 text-zinc-600",
  Archived: "border-zinc-200 bg-zinc-100 text-zinc-600",
  Invited: "border-amber-200 bg-amber-50 text-amber-700",
  Suspended: "border-red-200 bg-red-50 text-red-700",
  Dismissed: "border-zinc-200 bg-zinc-100 text-zinc-600",
};

export function StatusBadge({ status, className }: { status: string; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex h-6 items-center rounded-md border px-2 text-xs font-medium",
        statusStyles[status] ?? "border-slate-200 bg-slate-50 text-slate-700",
        className,
      )}
    >
      {status}
    </span>
  );
}
