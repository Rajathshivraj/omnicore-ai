import { Suspense } from "react";

import { LoginForm } from "@/features/auth/login-form";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <section className="w-full max-w-md">
        <div className="mb-6">
          <p className="text-sm font-medium uppercase tracking-wider text-teal-700">OmniCore AI</p>
          <h1 className="mt-3 text-3xl font-semibold text-slate-950">Sign in</h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Use a seeded demo account to access the role-specific portal.
          </p>
        </div>
        <Suspense fallback={<div className="rounded-lg border bg-white p-6 shadow-sm" />}>
          <LoginForm />
        </Suspense>
      </section>
    </main>
  );
}
