import { NextResponse } from "next/server";

import { api } from "@/lib/api/client";
import { getErrorMessage } from "@/lib/api/errors";

export async function GET() {
  try {
    const user = await api.getCurrentUser();
    return NextResponse.json(user);
  } catch (error) {
    return NextResponse.json({ message: getErrorMessage(error) }, { status: 401 });
  }
}
