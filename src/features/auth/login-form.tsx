"use client";

import { Loader2, LogIn } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

const demoUsers = [
  "admin@omnicore.local",
  "inventory@omnicore.local",
  "warehouse@omnicore.local",
  "customer@omnicore.local",
];

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("admin@omnicore.local");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const payload = (await response.json()) as { message?: string };
      if (!response.ok) {
        throw new Error(payload.message ?? "Login failed.");
      }
      router.replace(searchParams.get("next") ?? "/ops/dashboard");
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Login failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={submit} className="rounded-lg border bg-white p-6 shadow-sm">
      <div>
        <label className="text-sm font-medium text-slate-700" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="mt-2 h-10 w-full rounded-lg border px-3 text-sm outline-none focus:ring-2 focus:ring-teal-600"
        />
      </div>
      <div className="mt-4">
        <label className="text-sm font-medium text-slate-700" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="mt-2 h-10 w-full rounded-lg border px-3 text-sm outline-none focus:ring-2 focus:ring-teal-600"
        />
      </div>
      {error ? <p className="mt-4 text-sm text-red-700">{error}</p> : null}
      <Button disabled={isSubmitting} className="mt-5 w-full bg-teal-700 hover:bg-teal-800">
        {isSubmitting ? <Loader2 className="animate-spin" /> : <LogIn />} Sign in
      </Button>
      <div className="mt-5 rounded-md bg-slate-50 p-3 text-xs leading-5 text-slate-600">
        <p className="font-medium text-slate-700">Demo users</p>
        {demoUsers.map((user) => (
          <button
            key={user}
            type="button"
            onClick={() => setEmail(user)}
            className="mt-1 block text-left text-teal-700 hover:underline"
          >
            {user}
          </button>
        ))}
        <p className="mt-2">Password: Password123!</p>
      </div>
    </form>
  );
}
