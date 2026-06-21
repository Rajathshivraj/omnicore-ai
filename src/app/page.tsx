import Link from "next/link";
import { ArrowRight, BarChart3, ShoppingBag } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-12">
        <div className="max-w-3xl">
          <p className="text-sm font-medium uppercase tracking-wider text-teal-700">
            OmniCore AI
          </p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-950 md:text-6xl">
            Commerce and operations intelligence for modern retailers.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
            Explore the frontend MVP through the customer shopping experience
            or the internal operations portal backed by the OmniCore API.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg" className="bg-teal-700 hover:bg-teal-800">
              <Link href="/shop">
                <ShoppingBag /> Customer Portal <ArrowRight />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/ops/dashboard">
                <BarChart3 /> Operations Portal <ArrowRight />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </main>
  );
}
