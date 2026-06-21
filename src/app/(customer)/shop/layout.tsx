import { redirect } from "next/navigation";

import { CustomerNav } from "@/components/layout/customer-nav";
import { getCurrentUserData } from "@/lib/api/data";

export default async function ShopLayout({ children }: { children: React.ReactNode }) {
  let user;
  try {
    user = await getCurrentUserData();
  } catch {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <CustomerNav userName={user.name} />
      {children}
    </div>
  );
}
