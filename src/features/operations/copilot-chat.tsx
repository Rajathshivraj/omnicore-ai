"use client";

import { Bot, Loader2, Send, User } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import type { ApiAIInsight } from "@/lib/api/contracts";

type ChatMessage = {
  role: "assistant" | "user";
  content: string;
};

const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content:
      "Ask about sales movement, reorder priorities, or stockout risk. " +
      "I will cite the operational sources used.",
  },
];

export function CopilotChat() {
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);

  async function sendMessage() {
    const question = draft.trim();
    if (!question || isSending) return;

    setMessages((current) => [
      ...current,
      { role: "user", content: question },
    ]);
    setDraft("");
    setIsSending(true);

    try {
      const response = await fetch("/api/ai-copilot/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
      const payload = (await response.json()) as ApiAIInsight | { message?: string };

      if (!response.ok) {
        throw new Error("message" in payload ? payload.message : "The copilot request failed.");
      }

      const insight = payload as ApiAIInsight;
      const sourceTitles = insight.source_refs
        .map((source) => source.title)
        .filter((title): title is string => typeof title === "string" && title.length > 0);
      const sources = sourceTitles.length
        ? `\n\nSources: ${sourceTitles.slice(0, 3).join(", ")}`
        : "";
      setMessages((current) => [
        ...current,
        { role: "assistant", content: `${insight.summary}${sources}` },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "The copilot request failed.";
      setMessages((current) => [
        ...current,
        { role: "assistant", content: message },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <section className="flex min-h-[640px] flex-col rounded-lg border bg-white shadow-sm">
      <div className="border-b p-4">
        <h2 className="font-semibold text-slate-950">Operations Copilot</h2>
        <p className="mt-1 text-sm text-slate-500">
          RAG-backed answers persisted as AI insights for operational review.
        </p>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((message, index) => {
          const assistant = message.role === "assistant";
          const Icon = assistant ? Bot : User;
          return (
            <div key={index} className={`flex gap-3 ${assistant ? "" : "justify-end"}`}>
              {assistant ? <Icon className="mt-1 size-5 text-teal-700" /> : null}
              <div
                className={`max-w-2xl whitespace-pre-line rounded-lg px-4 py-3 text-sm leading-6 ${
                  assistant ? "bg-slate-100 text-slate-700" : "bg-teal-700 text-white"
                }`}
              >
                {message.content}
              </div>
              {!assistant ? <Icon className="mt-1 size-5 text-slate-500" /> : null}
            </div>
          );
        })}
      </div>
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") void sendMessage();
            }}
            disabled={isSending}
            placeholder="Ask about stockouts, fulfillment risk, forecasts"
            className="h-10 flex-1 rounded-lg border px-3 text-sm outline-none
              focus:ring-2 focus:ring-teal-600"
          />
          <Button
            onClick={() => void sendMessage()}
            disabled={isSending}
            className="bg-teal-700 hover:bg-teal-800"
          >
            {isSending ? <Loader2 className="animate-spin" /> : <Send />} Send
          </Button>
        </div>
      </div>
    </section>
  );
}
