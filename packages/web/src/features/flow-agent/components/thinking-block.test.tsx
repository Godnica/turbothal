import { describe, it, expect } from 'vitest';

import { buildBlocks } from '../lib/build-blocks';
import { type AgentEvent } from '../hooks/use-flow-agent-chat';

// Tests for buildBlocks logic (the pure function behind ThinkingBlock rendering)

describe('buildBlocks — thinking events', () => {
  it('groups consecutive thinking deltas into a single thinking block', () => {
    const events: AgentEvent[] = [
      { type: 'thinking', delta: 'I think ' },
      { type: 'thinking', delta: 'therefore I am' },
    ];
    const blocks = buildBlocks(events);
    expect(blocks).toHaveLength(1);
    expect(blocks[0]).toEqual({
      kind: 'thinking',
      content: 'I think therefore I am',
    });
  });

  it('creates separate thinking blocks when interrupted by another event', () => {
    const events: AgentEvent[] = [
      { type: 'thinking', delta: 'first' },
      { type: 'text_delta', delta: 'response' },
      { type: 'thinking', delta: 'second' },
    ];
    const blocks = buildBlocks(events);
    expect(blocks.filter((b) => b.kind === 'thinking')).toHaveLength(2);
  });

  it('returns empty array for empty events', () => {
    expect(buildBlocks([])).toHaveLength(0);
  });
});
