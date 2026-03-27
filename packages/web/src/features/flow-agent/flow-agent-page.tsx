import { useEffect, useRef } from 'react';

import { BotIcon, X } from 'lucide-react';

import { ChatInput } from '@/features/chat/chat-input';
import {
  ChatBubble,
  ChatBubbleMessage,
} from '@/features/chat/chat-bubble';

import { AgentMessageBubble } from './components/agent-message-bubble';
import { useFlowAgentChat } from './hooks/use-flow-agent-chat';

const WELCOME_MESSAGE = 'Ciao! Dimmi quale flusso vuoi creare e lo costruirò per te passo dopo passo.';

export function FlowAgentPage() {
  const { messages, isStreaming, error, sendMessage, clearError } =
    useFlowAgentChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new events
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 border-b px-6 py-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
          <BotIcon className="h-4 w-4 text-primary" />
        </div>
        <div>
          <h1 className="text-sm font-semibold">Flow Agent</h1>
          <p className="text-xs text-muted-foreground">
            Crea flussi Activepieces in linguaggio naturale
          </p>
        </div>
        {isStreaming && (
          <span className="ml-auto flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
            In elaborazione…
          </span>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 bg-destructive/10 px-6 py-2 text-sm text-destructive">
          <span className="flex-1">{error}</span>
          <button
            type="button"
            onClick={clearError}
            className="rounded p-0.5 hover:bg-destructive/20"
            aria-label="Chiudi errore"
            data-testid="error-dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {/* Welcome message */}
        <ChatBubble variant="received" layout="ai">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
            <BotIcon className="h-4 w-4 text-primary" />
          </div>
          <ChatBubbleMessage variant="received" layout="ai">
            {WELCOME_MESSAGE}
          </ChatBubbleMessage>
        </ChatBubble>

        {messages.map((msg, i) => {
          if (msg.role === 'user') {
            return (
              <ChatBubble key={i} variant="sent">
                <ChatBubbleMessage variant="sent">
                  {msg.text}
                </ChatBubbleMessage>
              </ChatBubble>
            );
          }
          return (
            <AgentMessageBubble
              key={i}
              events={msg.events}
              isStreaming={msg.isStreaming}
            />
          );
        })}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t px-4 py-4">
        <ChatInput
          onSendMessage={({ textContent }) => {
            if (textContent.trim()) sendMessage(textContent.trim());
          }}
          disabled={isStreaming}
          placeholder="Descrivi il flusso che vuoi creare…"
        />
      </div>
    </div>
  );
}
