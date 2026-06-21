"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Bot,
  Boxes,
  ClipboardList,
  Home,
  LineChart,
  Menu,
  Package,
  Search,
  Settings,
  Shield,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/ops/dashboard", label: "Dashboard", icon: Home },
  { href: "/ops/products", label: "Products", icon: Package },
  { href: "/ops/orders", label: "Orders", icon: ClipboardList },
  { href: "/ops/fulfillment", label: "Fulfillment", icon: ClipboardList },
  { href: "/ops/inventory", label: "Inventory", icon: Boxes },
  { href: "/ops/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/ops/forecasting", label: "Forecasting", icon: LineChart },
  { href: "/ops/ai-copilot", label: "AI Copilot", icon: Bot },
  { href: "/ops/admin", label: "Admin", icon: Shield },
];

const roleSections: Record<string, string[]> = {
  "Inventory Manager": [
    "Dashboard",
    "Products",
    "Inventory",
    "Analytics",
    "Forecasting",
    "AI Copilot",
  ],
  "Warehouse Manager": ["Dashboard", "Orders", "Fulfillment", "Inventory", "Analytics", "AI Copilot"],
  Admin: nav.map((item) => item.label),
};

export function OperationsShell({
  children,
  userName,
  role,
}: {
  children: React.ReactNode;
  userName: string;
  role: string;
}) {
  const pathname = usePathname();
  const allowedSections = roleSections[role] ?? roleSections.Admin;
  const visibleNav = nav.filter((item) => allowedSections.includes(item.label));

  return (
    <div className="min-h-screen bg-slate-100">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r bg-slate-950 text-white lg:block">
        <div className="flex h-16 items-center gap-2 border-b border-white/10 px-5">
          <div className="flex size-9 items-center justify-center rounded-lg bg-teal-500 text-slate-950">
            <Settings className="size-5" />
          </div>
          <div>
            <p className="font-semibold">OmniCore AI</p>
            <p className="text-xs text-slate-400">Operations Portal</p>
          </div>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {visibleNav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/10 hover:text-white",
                  active && "bg-white text-slate-950 hover:bg-white hover:text-slate-950",
                )}
              >
                <Icon className="size-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b bg-white px-4 lg:px-6">
          <Button variant="outline" size="icon" className="lg:hidden" aria-label="Open navigation">
            <Menu />
          </Button>
          <div className="flex min-w-0 flex-1 items-center gap-2 rounded-lg border bg-slate-50 px-3 py-2 text-sm text-slate-500">
            <Search className="size-4" />
            Search products, orders, SKUs, recommendations
          </div>
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-slate-950">{userName}</p>
            <p className="text-xs text-slate-500">{role}</p>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 lg:px-6">{children}</main>
      </div>
    </div>
  );
}
