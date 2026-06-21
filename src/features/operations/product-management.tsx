"use client";

import { Search } from "lucide-react";
import Image from "next/image";
import { useMemo, useState } from "react";

import { DataTable } from "@/components/data-display/data-table";
import { EmptyState } from "@/components/data-display/empty-state";
import { StatusBadge } from "@/components/data-display/status-badge";
import { Button } from "@/components/ui/button";
import type { Product } from "@/types/domain";

export function ProductManagement({ products }: { products: Product[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [selected, setSelected] = useState<Product | null>(products[0] ?? null);
  const categories = ["All", ...Array.from(new Set(products.map((product) => product.category)))];

  const filtered = useMemo(
    () =>
      products.filter((product) => {
        const haystack = `${product.name} ${product.sku} ${product.category}`.toLowerCase();
        return haystack.includes(query.toLowerCase()) && (category === "All" || product.category === category);
      }),
    [category, products, query],
  );

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
      <section>
        <div className="mb-4 flex flex-col gap-3 md:flex-row">
          <label className="flex flex-1 items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm text-slate-500">
            <Search className="size-4" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search products or SKUs"
              className="w-full bg-transparent text-slate-950 outline-none"
            />
          </label>
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="h-10 rounded-lg border bg-white px-3 text-sm"
          >
            {categories.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>
        <DataTable
          columns={["Product", "SKU", "Category", "Price", "Status", "Action"]}
          rows={filtered.map((product) => [
            <span key="name" className="font-medium text-slate-950">{product.name}</span>,
            product.sku,
            product.category,
            `$${product.price}`,
            <StatusBadge key="status" status={product.status} />,
            <Button key="action" variant="outline" size="sm" onClick={() => setSelected(product)}>Details</Button>,
          ])}
          emptyMessage="No products match the current filters."
        />
      </section>
      <aside className="rounded-lg border bg-white p-5 shadow-sm">
        {selected ? (
          <>
            <Image
              src={selected.image}
              alt={selected.name}
              width={640}
              height={360}
              className="aspect-video w-full rounded-md object-cover"
            />
            <div className="mt-4 flex items-center justify-between gap-3">
              <h2 className="font-semibold text-slate-950">{selected.name}</h2>
              <StatusBadge status={selected.status} />
            </div>
            <p className="mt-2 text-sm text-slate-500">{selected.sku}</p>
            <p className="mt-4 text-sm leading-6 text-slate-600">{selected.description}</p>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-md bg-slate-50 p-3"><dt className="text-slate-500">Category</dt><dd className="font-medium">{selected.category}</dd></div>
              <div className="rounded-md bg-slate-50 p-3"><dt className="text-slate-500">Price</dt><dd className="font-medium">${selected.price}</dd></div>
            </dl>
          </>
        ) : (
          <EmptyState title="No product selected" description="Select a product row to inspect its details." />
        )}
      </aside>
    </div>
  );
}
