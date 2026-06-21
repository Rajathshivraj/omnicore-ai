import Link from "next/link";
import Image from "next/image";
import { ArrowRight, PackageCheck, ShieldCheck, Truck } from "lucide-react";

import { EmptyState } from "@/components/data-display/empty-state";
import { ErrorState } from "@/components/data-display/error-state";
import { Button } from "@/components/ui/button";
import { getProductData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { Product } from "@/types/domain";

export default async function ShopHomePage() {
  let products: Product[] = [];
  let error: string | null = null;

  try {
    products = await getProductData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  const featured = products.slice(0, 3);
  const benefits = [
    {
      title: "Inventory aware",
      copy: "Live-style availability states are reflected in product and cart views.",
      icon: PackageCheck,
    },
    {
      title: "Fast fulfillment",
      copy: "Order status and shipment progress stay visible after purchase.",
      icon: Truck,
    },
    {
      title: "Account clarity",
      copy: "Profile, addresses, and order history are grouped in one customer view.",
      icon: ShieldCheck,
    },
  ];

  return (
    <main>
      <section className="bg-white">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 lg:grid-cols-[1fr_420px] lg:items-center">
          <div>
            <p className="text-sm font-medium uppercase tracking-wider text-teal-700">Retail ready</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight text-slate-950 md:text-5xl">
              Shop operationally curated products with clear delivery visibility.
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
              This customer portal demonstrates product discovery, cart review,
              order tracking, and profile management using backend API data.
            </p>
            <Button asChild size="lg" className="mt-7 bg-teal-700 hover:bg-teal-800">
              <Link href="/shop/products">
                Browse products <ArrowRight />
              </Link>
            </Button>
          </div>
          {error ? (
            <ErrorState title="Featured products could not be loaded" message={error} />
          ) : featured.length === 0 ? (
            <EmptyState title="No featured products" description="Products returned by the backend will appear here." />
          ) : (
            <div className="grid gap-3">
              {featured.map((product) => (
                <Link
                  href={`/shop/products/${product.id}`}
                  key={product.id}
                  className="flex gap-4 rounded-lg border bg-slate-50 p-3 hover:bg-white"
                >
                  <Image
                    src={product.image}
                    alt={product.name}
                    width={96}
                    height={96}
                    className="size-24 rounded-md object-cover"
                  />
                  <div>
                    <p className="text-xs text-teal-700">{product.category}</p>
                    <h2 className="mt-1 font-medium text-slate-950">{product.name}</h2>
                    <p className="mt-1 text-sm text-slate-500">{product.sku}</p>
                    <p className="mt-2 font-semibold text-slate-950">${product.price}</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
      <section className="mx-auto grid max-w-7xl gap-4 px-4 py-8 md:grid-cols-3">
        {benefits.map(({ title, copy, icon: Icon }) => (
          <div key={title} className="rounded-lg border bg-white p-5 shadow-sm">
            <Icon className="size-5 text-teal-700" />
            <h2 className="mt-4 font-semibold text-slate-950">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{copy}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
