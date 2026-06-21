import { NextResponse, type NextRequest } from "next/server";

const protectedPrefixes = ["/ops", "/shop"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasToken = Boolean(request.cookies.get("omnicore_access_token")?.value);
  const isProtected = protectedPrefixes.some((prefix) => pathname.startsWith(prefix));

  if (isProtected && !hasToken) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  if (pathname === "/login" && hasToken) {
    return NextResponse.redirect(new URL("/ops/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/ops/:path*", "/shop/:path*", "/login"],
};
