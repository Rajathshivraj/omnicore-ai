import { PageHeader } from "@/components/layout/page-header";
import { OrderManagement } from "@/features/operations/order-management";
import { EmptyState } from "@/components/data-display/empty-state";
import { ErrorState } from "@/components/data-display/error-state";
import { getOrderData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { Order } from "@/types/domain";

export default async function OpsOrdersPage() {
  let orders: Order[] = [];
  let error: string | null = null;

  try {
    orders = await getOrderData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  return (
    <>
      <PageHeader title="Orders" description="Review order status, fulfillment stage, line items, and operational exceptions." />
      {error ? (
        <ErrorState title="Orders could not be loaded" message={error} />
      ) : orders.length === 0 ? (
        <EmptyState title="No orders found" description="Orders created through the backend will appear here." />
      ) : (
        <OrderManagement orders={orders} />
      )}
    </>
  );
}
