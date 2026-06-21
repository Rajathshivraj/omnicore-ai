import { NextResponse } from "next/server";

import { api } from "@/lib/api/client";
import { getErrorMessage } from "@/lib/api/errors";

export async function POST(request: Request) {
  const payload = (await request.json().catch(() => null)) as { question?: unknown } | null;
  const question = typeof payload?.question === "string" ? payload.question.trim() : "";

  if (question.length < 3) {
    return NextResponse.json(
      { message: "Question must be at least 3 characters." },
      { status: 400 },
    );
  }

  try {
    const insight = await api.askCopilot(question);
    return NextResponse.json(insight, { status: 201 });
  } catch (error) {
    return NextResponse.json({ message: getErrorMessage(error) }, { status: 502 });
  }
}
