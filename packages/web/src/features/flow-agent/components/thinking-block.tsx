import { useState } from 'react';

import { Brain, ChevronDown, ChevronRight } from 'lucide-react';

import { cn } from '@/lib/utils';

interface ThinkingBlockProps {
  content: string;
  isStreaming?: boolean;
}

export function ThinkingBlock({ content, isStreaming = false }: ThinkingBlockProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="my-2 rounded-lg border border-border bg-muted/40 text-sm">
      <button
        type="button"
        onClick={() => setIsOpen((v) => !v)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-muted-foreground hover:text-foreground transition-colors"
      >
        <Brain className="h-3.5 w-3.5 shrink-0" />
        <span className="font-medium text-xs tracking-wide uppercase">
          Ragionamento
        </span>
        {isStreaming && (
          <span
            className="ml-1 inline-block h-1.5 w-1.5 rounded-full bg-primary animate-pulse"
            data-testid="thinking-streaming-dot"
          />
        )}
        <span className="ml-auto">
          {isOpen ? (
            <ChevronDown className="h-3.5 w-3.5" />
          ) : (
            <ChevronRight className="h-3.5 w-3.5" />
          )}
        </span>
      </button>

      <div
        className={cn(
          'overflow-hidden transition-all duration-200',
          isOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0',
        )}
        data-testid="thinking-content"
      >
        <pre className="overflow-x-auto whitespace-pre-wrap px-3 pb-3 font-mono text-xs text-muted-foreground">
          {content}
        </pre>
      </div>
    </div>
  );
}
