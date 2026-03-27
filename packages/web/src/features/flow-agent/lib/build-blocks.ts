/**
 * Pure logic for converting a flat AgentEvent[] into renderable Block[].
 * Framework-free, fully testable.
 */

import { type AgentEvent } from '../hooks/use-flow-agent-chat';

export type TextBlock = { kind: 'text'; content: string };
export type ThinkingBlockData = { kind: 'thinking'; content: string };
export type ToolBlock = {
  kind: 'tool';
  name: string;
  input: unknown;
  result?: string;
};

export type Block = TextBlock | ThinkingBlockData | ToolBlock;

export function buildBlocks(events: AgentEvent[]): Block[] {
  const blocks: Block[] = [];

  for (const event of events) {
    switch (event.type) {
      case 'text_delta': {
        const last = blocks[blocks.length - 1];
        if (last?.kind === 'text') {
          last.content += event.delta;
        } else {
          blocks.push({ kind: 'text', content: event.delta });
        }
        break;
      }
      case 'thinking': {
        const last = blocks[blocks.length - 1];
        if (last?.kind === 'thinking') {
          last.content += event.delta;
        } else {
          blocks.push({ kind: 'thinking', content: event.delta });
        }
        break;
      }
      case 'tool_call': {
        blocks.push({ kind: 'tool', name: event.name, input: event.input });
        break;
      }
      case 'tool_result': {
        for (let i = blocks.length - 1; i >= 0; i--) {
          const b = blocks[i];
          if (
            b.kind === 'tool' &&
            b.name === event.name &&
            b.result === undefined
          ) {
            b.result = event.output;
            break;
          }
        }
        break;
      }
    }
  }

  return blocks;
}
