import Link from "next/link";
import Image from "next/image";
import { notFound } from "next/navigation";
import { Check, ShoppingCart, Star } from "lucide-react";

import { StatusBadge } from "@/components/data-display/status-badge";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/data-display/error-state";
import { getInventoryData, getProductData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { InventoryItem, Product } from "@/types/domain";

export default async function ProductDetailsPage({
  params,
}: {
  params: Promise<{ productId: string }>;
}) {
  const { productId } = await params;
  let products: Product[] = [];
  let inventory: InventoryItem[] = [];
  let error: string | null = null;

  try {
    [products, inventory] = await Promise.all([getProductData(), getInventoryData()]);
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  if (error) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-8">
        <ErrorState title="Product could not be loaded" message={error} />
      </main>
    );
  }

  const product = products.find((item) => item.id === productId);
  if (!product) notFound();

  const stock = inventory.find((item) => item.productId === product.id);

  return (
    <main className="mx-auto grid max-w-7xl gap-8 px-4 py-8 lg:grid-cols-2">
      <Image
        src={product.image}
        alt={product.name}
        width={900}
        height={675}
        className="aspect-[4/3] w-full rounded-lg object-cover"
      />
      <section>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={product.status} />
          {stock ? <StatusBadge status={stock.status} /> : null}
        </div>
        <p className="mt-5 text-sm font-medium text-teal-700">{product.category}</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">{product.name}</h1>
        <p className="mt-2 text-sm text-slate-500">{product.sku}</p>
        <div className="mt-4 flex items-center gap-2 text-sm text-slate-600">
          <Star className="size-4 fill-amber-400 text-amber-400" />
          {product.rating} customer rating
        </div>
        <p className="mt-5 text-3xl font-semibold text-slate-950">${product.price}</p>
        <p className="mt-5 max-w-xl leading-7 text-slate-600">{product.description}</p>
        <ul className="mt-6 grid gap-2">
          {product.attributes.map((attribute) => (
            <li key={attribute} className="flex items-center gap-2 text-sm text-slate-700">
              <Check className="size-4 text-emerald-600" />
              {attribute}
            </li>
          ))}
        </ul>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Button className="bg-teal-700 hover:bg-teal-800">
            <ShoppingCart /> Add to cart
          </Button>
          <Button asChild variant="outline">
            <Link href="/shop/products">Back to products</Link>
          </Button>
        </div>
      </section>
    </main>
  );
}
