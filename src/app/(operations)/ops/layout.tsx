import { redirect } from "next/navigation";

import { OperationsShell } from "@/components/layout/operations-shell";
import { getCurrentUserData } from "@/lib/api/data";

export default async function OpsLayout({ children }: { children: React.ReactNode }) {
  let user;
  try {
    user = await getCurrentUserData();
  } catch {
    redirect("/login");
  }
  if (user.role === "Customer") {
    redirect("/shop");
  }
  return (
    <OperationsShell userName={user.name} role={user.role}>
      {children}
    </OperationsShell>
  );
}
