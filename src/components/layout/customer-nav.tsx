"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, ShoppingCart, User } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const links = [
  { href: "/shop", label: "Home" },
  { href: "/shop/products", label: "Products" },
  { href: "/shop/cart", label: "Cart" },
  { href: "/shop/orders", label: "Orders" },
  { href: "/shop/profile", label: "Profile" },
];

export function CustomerNav({ userName }: { userName: string }) {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
        <Link href="/shop" className="mr-2 text-lg font-semibold text-slate-950">
          OmniCore
        </Link>
        <nav className="hidden items-center gap-1 md:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 hover:text-slate-950",
                pathname === link.href && "bg-slate-100 text-slate-950",
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto hidden w-full max-w-sm items-center gap-2 rounded-lg border bg-slate-50 px-3 py-2 text-sm text-slate-500 md:flex">
          <Search className="size-4" />
          Search products, orders, categories
        </div>
        <Button asChild variant="outline" size="icon" aria-label="Cart">
          <Link href="/shop/cart">
            <ShoppingCart />
          </Link>
        </Button>
        <Button asChild variant="outline" size="icon" aria-label="Profile">
          <Link href="/shop/profile">
            <User />
          </Link>
        </Button>
        <span className="hidden text-sm font-medium text-slate-700 sm:inline">{userName}</span>
      </div>
    </header>
  );
}
