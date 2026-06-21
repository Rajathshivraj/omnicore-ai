import Link from "next/link";
import { ShoppingCart } from "lucide-react";

import { EmptyState } from "@/components/data-display/empty-state";
import { Button } from "@/components/ui/button";

export default function CartPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <h1 className="text-2xl font-semibold text-slate-950">Cart</h1>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_360px]">
        <section>
          <EmptyState
            title="Cart API is not available yet"
            description="Cart persistence is not implemented in the backend API. Product browsing and order history are connected to backend data."
            icon={ShoppingCart}
          />
        </section>
        <aside className="h-fit rounded-lg border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <ShoppingCart className="size-5 text-teal-700" />
            <h2 className="font-semibold text-slate-950">Order summary</h2>
          </div>
          <div className="mt-5 space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">Subtotal</span><span>$0</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Estimated shipping</span><span>$0</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Estimated tax</span><span>$0</span></div>
            <div className="border-t pt-3 flex justify-between font-semibold text-slate-950"><span>Total</span><span>$0</span></div>
          </div>
          <Button className="mt-5 w-full bg-teal-700 hover:bg-teal-800" disabled>Checkout</Button>
          <Button asChild variant="outline" className="mt-3 w-full">
            <Link href="/shop/products">Continue shopping</Link>
          </Button>
        </aside>
      </div>
    </main>
  );
}
