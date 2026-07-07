"use client";

import { useEffect, useRef, useState } from "react";
import { useStream } from "@langchain/react";
import {
  FileText,
  Loader2,
  PawPrint,
  Search,
  Send,
  Sparkles,
  Wrench,
} from "lucide-react";

import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { getMessageText, toolLabel } from "@/lib/messages";

const CONFIGURED_API_URL = process.env.NEXT_PUBLIC_API_URL;

function getApiUrl() {
  if (CONFIGURED_API_URL?.startsWith("http")) return CONFIGURED_API_URL;
  if (typeof window !== "undefined") {
    return new URL(CONFIGURED_API_URL ?? "/api", window.location.origin).toString();
  }
  return new URL(CONFIGURED_API_URL ?? "/api", "http://localhost:3000").toString();
}

type StreamMessage = ReturnType<typeof useStream>["messages"][number];

const SUGGESTIONS = [
  "How often should I deworm my cat?",
  "What vaccinations do kittens need?",
  "What are signs of feline dehydration?",
];

function toolIcon(name?: string) {
  if (name === "retrieve_information") return <FileText className="size-3" />;
  if (name?.startsWith("tavily")) return <Search className="size-3" />;
  return <Wrench className="size-3" />;
}

export function Chat({ assistantId }: { assistantId: string }) {
  const stream = useStream({ apiUrl: getApiUrl(), assistantId });
  const { messages, isLoading, error } = stream;

  const [input, setInput] = useState("");
  const messageViewportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const viewport = messageViewportRef.current;
    if (!viewport) return;
    viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  const send = (text: string) => {
    const content = text.trim();
    if (!content || isLoading) return;
    stream.submit({ messages: [{ type: "human", content }] });
    setInput("");
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(input);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col bg-[radial-gradient(circle_at_top,_var(--color-accent),_transparent_38%)]">
      <div
        ref={messageViewportRef}
        className="min-h-0 flex-1 overflow-y-auto overscroll-contain"
      >
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-7 px-4 py-8 sm:px-6">
          {messages.length === 0 && (
            <div className="mx-auto mt-[8vh] flex max-w-2xl flex-col items-center gap-7 text-center">
              <div className="relative flex size-16 items-center justify-center rounded-2xl border bg-background shadow-sm">
                <PawPrint className="size-8 text-primary" />
                <Sparkles className="absolute -right-2 -top-2 size-5 text-amber-500" />
              </div>
              <div className="space-y-2">
                <h1 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
                  How can I help your cat today?
                </h1>
                <p className="mx-auto max-w-lg text-pretty text-sm leading-6 text-muted-foreground sm:text-base">
                  Ask about everyday care, nutrition, vaccinations, or symptoms.
                  I’ll search the available veterinary resources when useful.
                </p>
              </div>
              <div className="grid w-full gap-2 sm:grid-cols-3">
                {SUGGESTIONS.map((s) => (
                  <Button
                    key={s}
                    variant="outline"
                    className="h-auto justify-start whitespace-normal rounded-xl bg-background/80 px-4 py-3 text-left text-sm shadow-xs"
                    onClick={() => send(s)}
                  >
                    {s}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, i) => (
            <MessageRow key={message.id ?? i} message={message} />
          ))}

          {isLoading && <ThinkingRow />}

          {error != null && (
            <Card className="border-destructive/40">
              <CardContent className="text-sm text-destructive">
                {error instanceof Error ? error.message : "Something went wrong."}
              </CardContent>
            </Card>
          )}
          <div aria-hidden="true" className="h-px" />
        </div>
      </div>

      <div className="z-10 shrink-0 border-t bg-background/90 backdrop-blur-xl">
        <form
          onSubmit={onSubmit}
          className="mx-auto w-full max-w-3xl px-4 pb-3 pt-3 sm:px-6"
        >
          <div className="flex items-center gap-2 rounded-2xl border bg-background p-2 shadow-lg shadow-black/5 ring-1 ring-black/[0.02] transition-shadow focus-within:shadow-xl">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your cat..."
              className="h-11 border-0 bg-transparent shadow-none focus-visible:ring-0"
              autoFocus
            />
            <Button
              type="submit"
              size="icon"
              disabled={isLoading || input.trim().length === 0}
              className="size-10 shrink-0 rounded-xl"
              aria-label="Send message"
            >
              {isLoading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
            </Button>
          </div>
          <p className="pt-2 text-center text-[11px] text-muted-foreground">
            General information only — contact a veterinarian for medical advice.
          </p>
        </form>
      </div>
    </div>
  );
}

function MessageRow({ message }: { message: StreamMessage }) {
  const isHuman = message.type === "human";
  const isTool = message.type === "tool";
  const text = getMessageText(message.content);
  const toolCalls =
    message.type === "ai"
      ? (message as unknown as {
          tool_calls?: Array<{ name?: string; id?: string }>;
        }).tool_calls ?? []
      : [];

  if (isTool) {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <details className="group rounded-lg border bg-muted/40 text-sm">
          <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2 text-muted-foreground">
            {toolIcon(message.name)}
            <span className="font-medium text-foreground">
              {toolLabel(message.name)}
            </span>
            <span className="text-xs">tool result</span>
          </summary>
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap px-3 pb-3 text-xs text-muted-foreground">
            {text}
          </pre>
        </details>
      </div>
    );
  }

  return (
    <Message from={isHuman ? "user" : "assistant"}>
      <div className="flex flex-col gap-2">
        {toolCalls.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {toolCalls.map((tc, idx) => (
              <Badge key={tc.id ?? idx} variant="secondary">
                {toolIcon(tc.name)}
                {toolLabel(tc.name)}
              </Badge>
            ))}
          </div>
        )}

        {text && (
          <MessageContent>
            {isHuman ? (
              <p className="whitespace-pre-wrap">{text}</p>
            ) : (
              <MessageResponse isAnimating={false}>{text}</MessageResponse>
            )}
          </MessageContent>
        )}
      </div>
    </Message>
  );
}

function ThinkingRow() {
  return (
    <Message from="assistant">
      <MessageContent className="flex-row items-center text-muted-foreground">
        <Loader2 className="size-4 animate-spin" />
        <span>Thinking…</span>
      </MessageContent>
    </Message>
  );
}
