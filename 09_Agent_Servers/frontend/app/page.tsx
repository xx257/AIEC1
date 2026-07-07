import { Cat } from "lucide-react";

import { Chat } from "@/components/chat";

const ASSISTANT_ID = "simple_agent";

export default function Page() {
  return (
    <main className="flex h-dvh flex-col overflow-hidden">
      <header className="z-10 border-b bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 w-full max-w-3xl items-center gap-3 px-4 sm:px-6">
          <div className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <Cat className="size-5" />
          </div>
          <div className="leading-tight">
            <p className="text-sm font-semibold">WhiskerWise</p>
            <div className="mt-0.5 flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="size-1.5 rounded-full bg-emerald-500" />
              Cat health assistant
            </div>
          </div>
        </div>
      </header>

      <Chat assistantId={ASSISTANT_ID} />
    </main>
  );
}
