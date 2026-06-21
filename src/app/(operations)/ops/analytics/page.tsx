import { ChartCard } from "@/components/data-display/chart-card";
import { DataTable } from "@/components/data-display/data-table";
import { ErrorState } from "@/components/data-display/error-state";
import { PageHeader } from "@/components/layout/page-header";
import { getOperationsSnapshot } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";

export default async function AnalyticsPage() {
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
        <PageHeader title="Analytics" description="Executive dashboard style analytics across revenue, product performance, and inventory health." />
        <ErrorState title="Analytics could not be loaded" message={error ?? "Backend data is unavailable."} />
      </>
    );
  }

  const { inventory, products, trendData } = snapshot;

  return (
    <>
      <PageHeader title="Analytics" description="Executive dashboard style analytics across revenue, product performance, and inventory health." />
      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Revenue Analytics" data={trendData} dataKey="revenue" type="area" color="#0f766e" />
        <ChartCard title="Product Demand Analytics" data={trendData} dataKey="demand" type="bar" color="#2563eb" />
        <ChartCard title="Inventory Value Analytics" data={trendData} dataKey="inventory" color="#ca8a04" />
        <ChartCard title="Forecast vs Demand Signal" data={trendData} dataKey="forecast" type="area" color="#7c3aed" />
      </div>
      <section className="mt-6">
        <h2 className="mb-3 text-sm font-semibold text-slate-950">Product Analytics</h2>
        <DataTable
          columns={["Product", "Category", "Rating", "Inventory Value", "Operational Note"]}
          rows={products.slice(0, 5).map((product) => {
            const stock = inventory.find((item) => item.productId === product.id);
            return [
              <span key="name" className="font-medium text-slate-950">{product.name}</span>,
              product.category,
              product.rating,
              stock ? `$${stock.onHand * stock.unitCost}` : "$0",
              stock ? `${stock.available} available at ${stock.location}` : "No stock record",
            ];
          })}
          emptyMessage="No product analytics data found."
        />
      </section>
    </>
  );
}
