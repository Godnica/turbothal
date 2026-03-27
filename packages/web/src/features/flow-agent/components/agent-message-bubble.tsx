import React, { useMemo } from 'react';

import { BotIcon } from 'lucide-react';
import Markdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';

import {
  ChatBubble,
  ChatBubbleAvatar,
  ChatBubbleMessage,
} from '@/features/chat/chat-bubble';

import { buildBlocks, type Block } from '../lib/build-blocks';
import { type AgentEvent } from '../hooks/use-flow-agent-chat';
import { ThinkingBlock } from './thinking-block';
import { ToolCallBlock } from './tool-call-block';

import MessageLoading from '@/features/chat/chat-bubble/message-loading';

interface AgentMessageBubbleProps {
  events: AgentEvent[];
  isStreaming: boolean;
}

/**
 * Renders an assistant message as a sequence of visual blocks:
 *  - ThinkingBlock  — for consecutive thinking deltas
 *  - ToolCallBlock  — for tool_call events, paired with their tool_result
 *  - Markdown text  — for accumulated text_delta events
 *
 * Events are processed in order so interleaved tool calls appear correctly.
 */
export const AgentMessageBubble = React.memo(function AgentMessageBubble({
  events,
  isStreaming,
}: AgentMessageBubbleProps) {
  const blocks = useMemo<Block[]>(() => buildBlocks(events), [events]);

  const isEmpty = blocks.length === 0;

  return (
    <ChatBubble variant="received" layout="ai">
      <ChatBubbleAvatar fallback={<BotIcon className="h-4 w-4" />} />
      <ChatBubbleMessage variant="received" layout="ai">
        {isEmpty && isStreaming ? (
          <MessageLoading />
        ) : (
          blocks.map((block, i) => <BlockRenderer key={i} block={block} isStreaming={isStreaming} />)
        )}
      </ChatBubbleMessage>
    </ChatBubble>
  );
});

// ── Renderer ─────────────────────────────────────────────────────────────────

function BlockRenderer({ block, isStreaming }: { block: Block; isStreaming: boolean }) {
  switch (block.kind) {
    case 'thinking':
      return <ThinkingBlock content={block.content} isStreaming={isStreaming} />;
    case 'tool':
      return (
        <ToolCallBlock name={block.name} input={block.input} result={block.result} />
      );
    case 'text':
      return (
        <Markdown
          className="prose prose-sm dark:prose-invert max-w-none"
          remarkPlugins={[remarkGfm, remarkBreaks]}
        >
          {block.content}
        </Markdown>
      );
  }
}
