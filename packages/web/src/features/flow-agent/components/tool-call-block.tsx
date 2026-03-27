import { useState } from 'react';

import { CheckCircle2, ChevronDown, ChevronRight, Loader2, Terminal } from 'lucide-react';

import { cn } from '@/lib/utils';

const TRUNCATE_LENGTH = 300;

interface ToolCallBlockProps {
  name: string;
  input: unknown;
  result?: string;
}

export function ToolCallBlock({ name, input, result }: ToolCallBlockProps) {
  const [isInputOpen, setIsInputOpen] = useState(false);
  const [isOutputExpanded, setIsOutputExpanded] = useState(false);

  const isDone = result !== undefined;
  const prettyInput = JSON.stringify(input, null, 2);
  const isTruncated = result !== undefined && result.length > TRUNCATE_LENGTH;
  const displayedOutput =
    isTruncated && !isOutputExpanded
      ? result.slice(0, TRUNCATE_LENGTH) + '…'
      : result;

  return (
    <div
      className="my-2 rounded-lg border border-border bg-muted/50 border-l-4 border-l-primary text-sm"
      data-testid="tool-call-block"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2">
        <Terminal className="h-3.5 w-3.5 shrink-0 text-primary" />
        <span className="rounded bg-primary/10 px-1.5 py-0.5 font-mono text-xs font-semibold text-primary">
          {name}
        </span>
        <span className="ml-auto">
          {isDone ? (
            <CheckCircle2
              className="h-4 w-4 text-green-500"
              data-testid="tool-done-icon"
            />
          ) : (
            <Loader2
              className="h-4 w-4 animate-spin text-muted-foreground"
              data-testid="tool-spinner"
            />
          )}
        </span>
      </div>

      {/* Input section (collapsible) */}
      <div className="border-t border-border">
        <button
          type="button"
          onClick={() => setIsInputOpen((v) => !v)}
          className="flex w-full items-center gap-1 px-3 py-1.5 text-left text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          {isInputOpen ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
          <span>Input</span>
        </button>

        <div
          className={cn(
            'overflow-hidden transition-all duration-200',
            isInputOpen ? 'max-h-[200px] opacity-100' : 'max-h-0 opacity-0',
          )}
          data-testid="tool-input-content"
        >
          <pre className="overflow-x-auto overflow-y-auto max-h-[180px] px-3 pb-2 font-mono text-xs text-muted-foreground">
            {prettyInput}
          </pre>
        </div>
      </div>

      {/* Output section (only when done) */}
      {isDone && (
        <div className="border-t border-border px-3 py-2">
          <p className="mb-1 text-xs font-medium text-muted-foreground">Output</p>
          <pre
            className="whitespace-pre-wrap break-words font-mono text-xs text-foreground"
            data-testid="tool-output-content"
          >
            {displayedOutput}
          </pre>
          {isTruncated && (
            <button
              type="button"
              onClick={() => setIsOutputExpanded((v) => !v)}
              className="mt-1 text-xs text-primary hover:underline"
              data-testid="tool-output-expand"
            >
              {isOutputExpanded ? 'mostra meno' : 'mostra tutto'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
