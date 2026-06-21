"use client";

import { useState } from "react";

import { DataTable } from "@/components/data-display/data-table";
import { StatusBadge } from "@/components/data-display/status-badge";
import { Button } from "@/components/ui/button";
import type { Order } from "@/types/domain";

export function OrderManagement({ orders }: { orders: Order[] }) {
  const [selected, setSelected] = useState<Order | null>(orders[0] ?? null);

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_380px]">
      <DataTable
        columns={["Order", "Customer", "Date", "Status", "Fulfillment", "Total", "Action"]}
        rows={orders.map((order) => [
          <span key="id" className="font-medium text-slate-950">{order.id}</span>,
          order.customer,
          order.date,
          <StatusBadge key="status" status={order.status} />,
          <StatusBadge key="fulfillment" status={order.fulfillmentStatus} />,
          `$${order.total}`,
          <Button key="action" variant="outline" size="sm" onClick={() => setSelected(order)}>View</Button>,
        ])}
        emptyMessage="No orders found."
      />
      <aside className="rounded-lg border bg-white p-5 shadow-sm">
        {selected ? (
          <>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-semibold text-slate-950">{selected.id}</h2>
                <p className="mt-1 text-sm text-slate-500">{selected.customer} - {selected.destination}</p>
              </div>
              <StatusBadge status={selected.fulfillmentStatus} />
            </div>
            <div className="mt-5 space-y-3">
              {selected.lines.map((line) => (
                <div key={line.sku} className="rounded-md bg-slate-50 p-3 text-sm">
                  <div className="flex justify-between gap-3">
                    <span className="font-medium text-slate-950">{line.productName}</span>
                    <span>${line.unitPrice * line.quantity}</span>
                  </div>
                  <p className="mt-1 text-slate-500">{line.sku} - Qty {line.quantity}</p>
                </div>
              ))}
            </div>
            <div className="mt-5 border-t pt-4 text-sm">
              <div className="flex justify-between font-semibold text-slate-950"><span>Total</span><span>${selected.total}</span></div>
            </div>
          </>
        ) : null}
      </aside>
    </div>
  );
}
