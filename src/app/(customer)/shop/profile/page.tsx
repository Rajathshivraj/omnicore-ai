import { CreditCard, MapPin, User } from "lucide-react";

import { ErrorState } from "@/components/data-display/error-state";
import { PageHeader } from "@/components/layout/page-header";
import { getCurrentUserData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";

export default async function ProfilePage() {
  let user = null;
  let error: string | null = null;

  try {
    user = await getCurrentUserData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <PageHeader title="Profile" description="Customer account information from the authenticated backend user." />
      {error ? <ErrorState title="Profile could not be loaded" message={error} /> : null}
      <div className="grid gap-4 lg:grid-cols-3">
        <section className="rounded-lg border bg-white p-5 shadow-sm">
          <User className="size-5 text-teal-700" />
          <h2 className="mt-4 font-semibold text-slate-950">{user?.name ?? "Unavailable"}</h2>
          <p className="mt-1 text-sm text-slate-500">{user?.email ?? "No authenticated user loaded"}</p>
          <p className="mt-4 text-sm leading-6 text-slate-600">{user ? `${user.role} account with ${user.status.toLowerCase()} status.` : "Provide a frontend API token to load current user details."}</p>
        </section>
        <section className="rounded-lg border bg-white p-5 shadow-sm">
          <MapPin className="size-5 text-teal-700" />
          <h2 className="mt-4 font-semibold text-slate-950">Default address</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">814 Congress Ave, Austin, TX 78701</p>
        </section>
        <section className="rounded-lg border bg-white p-5 shadow-sm">
          <CreditCard className="size-5 text-teal-700" />
          <h2 className="mt-4 font-semibold text-slate-950">Payment</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">Visa ending in 4242. Payment processing is intentionally not implemented.</p>
        </section>
      </div>
    </main>
  );
}
