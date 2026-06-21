import { DataTable } from "@/components/data-display/data-table";
import { ErrorState } from "@/components/data-display/error-state";
import { StatusBadge } from "@/components/data-display/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { getFulfillmentData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { FulfillmentRecord } from "@/types/domain";

export default async function FulfillmentPage() {
  let records: FulfillmentRecord[] = [];
  let error: string | null = null;

  try {
    records = await getFulfillmentData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  return (
    <>
      <PageHeader
        title="Fulfillment"
        description="Warehouse queue records for picking, packing, shipping, and exceptions."
      />
      {error ? (
        <ErrorState title="Fulfillment could not be loaded" message={error} />
      ) : (
        <DataTable
          columns={["Record", "Order", "Warehouse", "Status", "Tracking", "Exception", "Updated"]}
          rows={records.map((record) => [
            <span key="id" className="font-medium text-slate-950">{record.id}</span>,
            record.orderId,
            record.warehouse,
            <StatusBadge key="status" status={record.status} />,
            record.trackingReference ?? "Not assigned",
            record.exceptionReason ?? "None",
            record.updatedAt,
          ])}
          emptyMessage="No fulfillment records found."
        />
      )}
    </>
  );
}
