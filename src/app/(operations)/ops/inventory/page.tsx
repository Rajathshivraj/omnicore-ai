import { AlertTriangle, Boxes, CircleCheck, PackageX } from "lucide-react";

import { DataTable } from "@/components/data-display/data-table";
import { EmptyState } from "@/components/data-display/empty-state";
import { ErrorState } from "@/components/data-display/error-state";
import { KpiCard } from "@/components/data-display/kpi-card";
import { StatusBadge } from "@/components/data-display/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { getInventoryData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { InventoryItem } from "@/types/domain";

export default async function InventoryPage() {
  let inventory: InventoryItem[] = [];
  let error: string | null = null;

  try {
    inventory = await getInventoryData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  if (error) {
    return (
      <>
        <PageHeader title="Inventory" description="Inventory health, low-stock alerts, stock levels, reservations, and reorder thresholds." />
        <ErrorState title="Inventory could not be loaded" message={error} />
      </>
    );
  }

  const lowStock = inventory.filter((item) => item.status === "Low Stock").length;
  const risk = inventory.filter((item) => item.status === "Stockout Risk" || item.status === "Out of Stock").length;
  const alerts = inventory.filter((item) => item.status !== "Healthy");

  return (
    <>
      <PageHeader title="Inventory" description="Inventory health, low-stock alerts, stock levels, reservations, and reorder thresholds." />
      <div className="grid gap-4 md:grid-cols-3">
        <KpiCard label="Healthy SKUs" value={`${inventory.length - lowStock - risk}`} change="Above reorder point" icon={CircleCheck} tone="emerald" />
        <KpiCard label="Low Stock" value={`${lowStock}`} change="Below preferred threshold" icon={AlertTriangle} tone="amber" />
        <KpiCard label="Critical Risk" value={`${risk}`} change="Stockout or near stockout" icon={PackageX} tone="red" />
      </div>
      <section className="mt-6">
        <DataTable
          columns={["SKU", "Product", "Location", "On Hand", "Reserved", "Available", "Reorder Point", "Status"]}
          rows={inventory.map((item) => [
            <span key="sku" className="font-medium text-slate-950">{item.sku}</span>,
            item.name,
            item.location,
            item.onHand,
            item.reserved,
            item.available,
            item.reorderPoint,
            <StatusBadge key="status" status={item.status} />,
          ])}
          emptyMessage="No inventory records found."
        />
      </section>
      <section className="mt-6 rounded-lg border bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <Boxes className="size-5 text-teal-700" />
          <h2 className="font-semibold text-slate-950">Low Stock Alerts</h2>
        </div>
        {alerts.length === 0 ? (
          <div className="mt-4">
            <EmptyState title="No low-stock alerts" description="Loaded inventory records are currently healthy." />
          </div>
        ) : (
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {alerts.map((item) => (
              <div key={item.id} className="rounded-md border p-3">
                <StatusBadge status={item.status} />
                <p className="mt-3 font-medium text-slate-950">{item.name}</p>
                <p className="mt-1 text-sm text-slate-500">{item.available} available at {item.location}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
