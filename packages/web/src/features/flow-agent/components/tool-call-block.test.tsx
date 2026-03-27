import { describe, it, expect } from 'vitest';

import { buildBlocks } from '../lib/build-blocks';
import { type AgentEvent } from '../hooks/use-flow-agent-chat';

// Tests for buildBlocks logic (the pure function behind ToolCallBlock rendering)

describe('buildBlocks — tool events', () => {
  it('creates a tool block for tool_call event', () => {
    const events: AgentEvent[] = [
      { type: 'tool_call', name: 'bash', input: { command: 'ls' } },
    ];
    const blocks = buildBlocks(events);
    expect(blocks).toHaveLength(1);
    expect(blocks[0]).toEqual({
      kind: 'tool',
      name: 'bash',
      input: { command: 'ls' },
      result: undefined,
    });
  });

  it('attaches result to the matching tool block', () => {
    const events: AgentEvent[] = [
      { type: 'tool_call', name: 'bash', input: {} },
      { type: 'tool_result', name: 'bash', output: 'output here' },
    ];
    const blocks = buildBlocks(events);
    expect(blocks).toHaveLength(1);
    const tool = blocks[0];
    expect(tool.kind).toBe('tool');
    if (tool.kind === 'tool') {
      expect(tool.result).toBe('output here');
    }
  });

  it('does not attach result to wrong tool name', () => {
    const events: AgentEvent[] = [
      { type: 'tool_call', name: 'bash', input: {} },
      { type: 'tool_result', name: 'read_file', output: 'data' },
    ];
    const blocks = buildBlocks(events);
    const bashBlock = blocks.find((b) => b.kind === 'tool');
    if (bashBlock?.kind === 'tool') {
      expect(bashBlock.result).toBeUndefined();
    }
  });

  it('handles two tool calls with their respective results', () => {
    const events: AgentEvent[] = [
      { type: 'tool_call', name: 'bash', input: { command: 'ls' } },
      { type: 'tool_result', name: 'bash', output: 'file1.txt' },
      { type: 'tool_call', name: 'read_file', input: { path: 'file1.txt' } },
      { type: 'tool_result', name: 'read_file', output: 'content' },
    ];
    const blocks = buildBlocks(events);
    expect(blocks).toHaveLength(2);
    const [bash, readFile] = blocks;
    if (bash.kind === 'tool') expect(bash.result).toBe('file1.txt');
    if (readFile.kind === 'tool') expect(readFile.result).toBe('content');
  });

  it('interleaves tool blocks with text blocks correctly', () => {
    const events: AgentEvent[] = [
      { type: 'text_delta', delta: 'Before' },
      { type: 'tool_call', name: 'bash', input: {} },
      { type: 'tool_result', name: 'bash', output: 'done' },
      { type: 'text_delta', delta: 'After' },
    ];
    const blocks = buildBlocks(events);
    expect(blocks[0]).toEqual({ kind: 'text', content: 'Before' });
    expect(blocks[1].kind).toBe('tool');
    expect(blocks[2]).toEqual({ kind: 'text', content: 'After' });
  });
});
