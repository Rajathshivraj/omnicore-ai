import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete("omnicore_access_token");
  response.cookies.delete("omnicore_refresh_token");
  return response;
}
