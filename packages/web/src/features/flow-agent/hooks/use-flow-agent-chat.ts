import { useState, useRef, useCallback } from 'react';

import { parseSseBuffer } from '../lib/sse-parser';

const BACKEND_URL =
  (import.meta as { env?: Record<string, string> }).env
    ?.VITE_FLOW_AGENT_URL ?? 'http://localhost:8181';

// ── Event types emitted by the backend SSE stream ──────────────────────────

export type AgentEvent =
  | { type: 'text_delta'; delta: string }
  | { type: 'thinking'; delta: string }
  | { type: 'tool_call'; name: string; input: unknown }
  | { type: 'tool_result'; name: string; output: string };

// ── Message types ───────────────────────────────────────────────────────────

export type UserMessage = { role: 'user'; text: string };
export type AssistantMessage = {
  role: 'assistant';
  events: AgentEvent[];
  isStreaming: boolean;
};
export type FlowAgentMessage = UserMessage | AssistantMessage;

// ── Hook ────────────────────────────────────────────────────────────────────

export interface UseFlowAgentChatResult {
  messages: FlowAgentMessage[];
  isStreaming: boolean;
  error: string | null;
  sendMessage: (text: string) => void;
  clearError: () => void;
}

export function useFlowAgentChat(): UseFlowAgentChatResult {
  const [messages, setMessages] = useState<FlowAgentMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  const sendMessage = useCallback((text: string) => {
    if (isStreaming) return;

    setError(null);

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', text }]);

    // Add empty assistant message that we'll fill in as events arrive
    setMessages((prev) => [
      ...prev,
      { role: 'assistant', events: [], isStreaming: true },
    ]);

    setIsStreaming(true);

    const body = JSON.stringify({
      message: text,
      session_id: sessionIdRef.current ?? undefined,
    });

    (async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body,
        });

        if (!response.ok || !response.body) {
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const { frames, remaining } = parseSseBuffer(buffer);
          buffer = remaining;

          for (const frame of frames) {
            handleSseEvent(frame.event, frame.data);
          }
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        setError(message);
        setIsStreaming(false);
        // Mark last assistant message as done
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1 && m.role === 'assistant'
              ? { ...m, isStreaming: false }
              : m,
          ),
        );
      }
    })();

    function handleSseEvent(
      eventType: string,
      payload: Record<string, unknown>,
    ) {
      switch (eventType) {
        case 'session':
          if (typeof payload.session_id === 'string') {
            sessionIdRef.current = payload.session_id;
          }
          break;

        case 'text_delta':
          appendEvent({ type: 'text_delta', delta: String(payload.delta ?? '') });
          break;

        case 'thinking':
          appendEvent({ type: 'thinking', delta: String(payload.delta ?? '') });
          break;

        case 'tool_call':
          appendEvent({
            type: 'tool_call',
            name: String(payload.name ?? ''),
            input: payload.input ?? {},
          });
          break;

        case 'tool_result':
          appendEvent({
            type: 'tool_result',
            name: String(payload.name ?? ''),
            output: String(payload.output ?? ''),
          });
          break;

        case 'done':
          setIsStreaming(false);
          setMessages((prev) =>
            prev.map((m, i) =>
              i === prev.length - 1 && m.role === 'assistant'
                ? { ...m, isStreaming: false }
                : m,
            ),
          );
          break;

        case 'error':
          setError(String(payload.message ?? 'Unknown error'));
          setIsStreaming(false);
          setMessages((prev) =>
            prev.map((m, i) =>
              i === prev.length - 1 && m.role === 'assistant'
                ? { ...m, isStreaming: false }
                : m,
            ),
          );
          break;
      }
    }

    function appendEvent(event: AgentEvent) {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (!last || last.role !== 'assistant') return prev;
        const updated: AssistantMessage = {
          ...last,
          events: [...last.events, event],
        };
        return [...prev.slice(0, -1), updated];
      });
    }
  }, [isStreaming]);

  const clearError = useCallback(() => setError(null), []);

  return { messages, isStreaming, error, sendMessage, clearError };
}
