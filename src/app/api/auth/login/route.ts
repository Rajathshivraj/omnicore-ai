import { NextResponse } from "next/server";

import { api } from "@/lib/api/client";
import { getErrorMessage } from "@/lib/api/errors";

const cookieOptions = {
  httpOnly: true,
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production",
  path: "/",
};

export async function POST(request: Request) {
  const payload = (await request.json().catch(() => null)) as {
    email?: unknown;
    password?: unknown;
  } | null;
  const email = typeof payload?.email === "string" ? payload.email : "";
  const password = typeof payload?.password === "string" ? payload.password : "";

  try {
    const tokenPair = await api.login(email, password);
    const response = NextResponse.json({ ok: true });
    response.cookies.set("omnicore_access_token", tokenPair.access_token, {
      ...cookieOptions,
      maxAge: 15 * 60,
    });
    response.cookies.set("omnicore_refresh_token", tokenPair.refresh_token, {
      ...cookieOptions,
      maxAge: 14 * 24 * 60 * 60,
    });
    return response;
  } catch (error) {
    return NextResponse.json({ message: getErrorMessage(error) }, { status: 401 });
  }
}
