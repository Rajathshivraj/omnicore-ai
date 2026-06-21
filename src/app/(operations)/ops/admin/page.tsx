import { UserPlus } from "lucide-react";

import { DataTable } from "@/components/data-display/data-table";
import { ErrorState } from "@/components/data-display/error-state";
import { StatusBadge } from "@/components/data-display/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { getAdminRoleData, getAdminUserData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { ApiRole } from "@/lib/api/contracts";
import type { User } from "@/types/domain";

export default async function AdminPage() {
  let users: User[] = [];
  let roles: ApiRole[] = [];
  let error: string | null = null;

  try {
    [users, roles] = await Promise.all([getAdminUserData(), getAdminRoleData()]);
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  return (
    <>
      <PageHeader
        title="Admin"
        description="User management and role visibility for the MVP operations portal."
        actions={<Button className="bg-teal-700 hover:bg-teal-800"><UserPlus /> Invite user</Button>}
      />
      {error ? <ErrorState title="Admin data could not be loaded" message={error} /> : null}
      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-950">Users</h2>
          <DataTable
            columns={["User", "Email", "Role", "Status", "Last Active"]}
            rows={users.map((user) => [
              <span key="name" className="font-medium text-slate-950">{user.name}</span>,
              user.email,
              user.role,
              <StatusBadge key="status" status={user.status} />,
              user.lastActive,
            ])}
            emptyMessage="No users found."
          />
        </section>
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-950">Roles</h2>
          <div className="space-y-3">
            {roles.map((role) => (
              <div key={role.id} className="rounded-lg border bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-slate-950">{role.name}</p>
                  <StatusBadge status="Active" />
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {role.description ?? `${role.name} access to role-specific operational work surfaces.`}
                </p>
              </div>
            ))}
            {roles.length === 0 ? (
              <div className="rounded-lg border border-dashed bg-white p-4 text-sm text-slate-500">
                No roles found.
              </div>
            ) : null}
          </div>
        </section>
      </div>
    </>
  );
}
