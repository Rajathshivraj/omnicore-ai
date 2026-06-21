import { AlertTriangle, Boxes, DollarSign, ShoppingCart } from "lucide-react";

import { ChartCard } from "@/components/data-display/chart-card";
import { DataTable } from "@/components/data-display/data-table";
import { EmptyState } from "@/components/data-display/empty-state";
import { ErrorState } from "@/components/data-display/error-state";
import { KpiCard } from "@/components/data-display/kpi-card";
import { StatusBadge } from "@/components/data-display/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { getOperationsSnapshot } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";

export default async function DashboardPage() {
  let snapshot;
  let error: string | null = null;

  try {
    snapshot = await getOperationsSnapshot();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  if (!snapshot) {
    return (
      <>
        <PageHeader title="Dashboard" description="Operational summary for revenue, orders, inventory health, and fulfillment attention." />
        <ErrorState title="Dashboard data could not be loaded" message={error ?? "Backend data is unavailable."} />
      </>
    );
  }

  const { inventory, orders, trendData } = snapshot;
  const lowStock = inventory.filter((item) => item.status !== "Healthy");
  const revenue = orders.reduce((sum, order) => sum + order.total, 0);
  const inventoryValue = inventory.reduce((sum, item) => sum + item.onHand * item.unitCost, 0);

  return (
    <>
      <PageHeader title="Dashboard" description="Operational summary for revenue, orders, inventory health, and fulfillment attention." />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Revenue" value={`$${Math.round(revenue).toLocaleString()}`} change="From loaded orders" icon={DollarSign} tone="emerald" />
        <KpiCard label="Orders" value={`${orders.length}`} change="Backend order records" icon={ShoppingCart} tone="blue" />
        <KpiCard label="Inventory Value" value={`$${Math.round(inventoryValue).toLocaleString()}`} change="Estimated from loaded stock" icon={Boxes} tone="teal" />
        <KpiCard label="Low Stock Alerts" value={`${lowStock.length}`} change="Requires replenishment review" icon={AlertTriangle} tone="amber" />
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <ChartCard title="Revenue Trend" data={trendData} dataKey="revenue" type="area" color="#0f766e" />
        <ChartCard title="Orders Trend" data={trendData} dataKey="orders" type="bar" color="#2563eb" />
        <ChartCard title="Inventory Trend" data={trendData} dataKey="inventory" color="#ca8a04" />
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-[1fr_360px]">
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-950">Recent Orders</h2>
          <DataTable
            columns={["Order", "Customer", "Status", "Fulfillment", "Total"]}
            rows={orders.map((order) => [
              <span key="id" className="font-medium text-slate-950">{order.id}</span>,
              order.customer,
              <StatusBadge key="status" status={order.status} />,
              <StatusBadge key="fulfillment" status={order.fulfillmentStatus} />,
              `$${order.total}`,
            ])}
            emptyMessage="No recent orders found."
          />
        </section>
        <section className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="font-semibold text-slate-950">Low Stock Alerts</h2>
          {lowStock.length === 0 ? (
            <div className="mt-4">
              <EmptyState title="No low-stock alerts" description="All loaded inventory records are above their reorder threshold." />
            </div>
          ) : (
            <div className="mt-4 space-y-3">
              {lowStock.map((item) => (
                <div key={item.id} className="rounded-md border p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-slate-950">{item.name}</p>
                      <p className="mt-1 text-xs text-slate-500">{item.sku} - {item.location}</p>
                    </div>
                    <StatusBadge status={item.status} />
                  </div>
                  <p className="mt-3 text-sm text-slate-600">{item.available} available, reorder point {item.reorderPoint}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </>
  );
}
