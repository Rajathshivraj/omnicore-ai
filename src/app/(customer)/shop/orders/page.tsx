import { DataTable } from "@/components/data-display/data-table";
import { ErrorState } from "@/components/data-display/error-state";
import { StatusBadge } from "@/components/data-display/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { getMyOrderData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { Order } from "@/types/domain";

export default async function CustomerOrdersPage() {
  let orders: Order[] = [];
  let error: string | null = null;

  try {
    orders = await getMyOrderData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <PageHeader
        title="Orders"
        description="Customer-facing order history with current order and fulfillment status."
      />
      {error ? (
        <ErrorState title="Orders could not be loaded" message={error} />
      ) : (
        <DataTable
          columns={["Order", "Date", "Items", "Status", "Fulfillment", "Total"]}
          rows={orders.slice(0, 4).map((order) => [
            <span key="id" className="font-medium text-slate-950">{order.id}</span>,
            order.date,
            `${order.lines.length} items`,
            <StatusBadge key="status" status={order.status} />,
            <StatusBadge key="fulfillment" status={order.fulfillmentStatus} />,
            `$${order.total}`,
          ])}
          emptyMessage="No customer orders found."
        />
      )}
    </main>
  );
}
