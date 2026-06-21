"use client";

import Link from "next/link";
import Image from "next/image";
import { Search, Star } from "lucide-react";
import { useMemo, useState } from "react";

import { EmptyState } from "@/components/data-display/empty-state";
import { Button } from "@/components/ui/button";
import type { Product } from "@/types/domain";

export function ProductBrowser({ products }: { products: Product[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const categories = ["All", ...Array.from(new Set(products.map((product) => product.category)))];

  const filtered = useMemo(
    () =>
      products.filter((product) => {
        const matchesQuery = `${product.name} ${product.sku} ${product.category}`
          .toLowerCase()
          .includes(query.toLowerCase());
        const matchesCategory = category === "All" || product.category === category;
        return matchesQuery && matchesCategory;
      }),
    [category, products, query],
  );

  return (
    <div>
      <div className="flex flex-col gap-3 md:flex-row">
        <label className="flex flex-1 items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm text-slate-500">
          <Search className="size-4" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by product, SKU, category"
            className="w-full bg-transparent text-slate-950 outline-none placeholder:text-slate-400"
          />
        </label>
        <select
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          className="h-10 rounded-lg border bg-white px-3 text-sm text-slate-700 outline-none focus:ring-2 focus:ring-teal-600"
        >
          {categories.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>
      {filtered.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="No products match your filters" description="Try another search term or category." />
        </div>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((product) => (
            <article key={product.id} className="overflow-hidden rounded-lg border bg-white shadow-sm">
              <Image
                src={product.image}
                alt={product.name}
                width={640}
                height={420}
                className="h-56 w-full object-cover"
              />
              <div className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-medium text-teal-700">{product.category}</p>
                    <h2 className="mt-1 font-semibold text-slate-950">{product.name}</h2>
                  </div>
                  <p className="font-semibold text-slate-950">${product.price}</p>
                </div>
                <div className="mt-3 flex items-center gap-1 text-sm text-slate-500">
                  <Star className="size-4 fill-amber-400 text-amber-400" />
                  {product.rating} rating
                </div>
                <p className="mt-3 line-clamp-2 text-sm leading-6 text-slate-600">{product.description}</p>
                <Button asChild className="mt-4 w-full bg-teal-700 hover:bg-teal-800">
                  <Link href={`/shop/products/${product.id}`}>View product</Link>
                </Button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
