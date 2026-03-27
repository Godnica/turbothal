import { describe, it, expect } from 'vitest';

import { buildBlocks } from './lib/build-blocks';
import { parseSseBuffer, parseSseFrame } from './lib/sse-parser';
import { type AgentEvent } from './hooks/use-flow-agent-chat';

/**
 * Integration-level pure logic tests for the Flow Agent chat flow.
 * These test the complete data pipeline: raw SSE bytes → parsed frames → rendered blocks.
 */

describe('Flow Agent — end-to-end data pipeline', () => {
  it('full agent turn: session + thinking + tool_call + tool_result + text + done', () => {
    const rawBuffer = [
      'event: session\ndata: {"session_id":"sess-1"}\n\n',
      'event: thinking\ndata: {"delta":"Let me think..."}\n\n',
      'event: tool_call\ndata: {"name":"bash","input":{"command":"ls"}}\n\n',
      'event: tool_result\ndata: {"name":"bash","output":"file1.txt"}\n\n',
      'event: text_delta\ndata: {"delta":"The flow is ready!"}\n\n',
      'event: done\ndata: {}\n\n',
    ].join('');

    const { frames } = parseSseBuffer(rawBuffer);
    expect(frames).toHaveLength(6);
    expect(frames[0].event).toBe('session');
    expect(frames[5].event).toBe('done');

    // Simulate building agent events from the frames
    const agentEvents: AgentEvent[] = [];
    for (const frame of frames) {
      switch (frame.event) {
        case 'thinking':
          agentEvents.push({ type: 'thinking', delta: String(frame.data.delta) });
          break;
        case 'tool_call':
          agentEvents.push({ type: 'tool_call', name: String(frame.data.name), input: frame.data.input });
          break;
        case 'tool_result':
          agentEvents.push({ type: 'tool_result', name: String(frame.data.name), output: String(frame.data.output) });
          break;
        case 'text_delta':
          agentEvents.push({ type: 'text_delta', delta: String(frame.data.delta) });
          break;
      }
    }

    const blocks = buildBlocks(agentEvents);

    expect(blocks).toHaveLength(3); // thinking + tool + text
    expect(blocks[0]).toEqual({ kind: 'thinking', content: 'Let me think...' });
    expect(blocks[1].kind).toBe('tool');
    if (blocks[1].kind === 'tool') {
      expect(blocks[1].name).toBe('bash');
      expect(blocks[1].result).toBe('file1.txt');
    }
    expect(blocks[2]).toEqual({ kind: 'text', content: 'The flow is ready!' });
  });

  it('accumulates chunks arriving in multiple reads', () => {
    // Simulate a chunk split mid-frame
    const chunk1 = 'event: text_delta\ndata: {"del';
    const chunk2 = 'ta":"hello world"}\n\n';

    const { frames: f1, remaining: r1 } = parseSseBuffer(chunk1);
    expect(f1).toHaveLength(0);

    const { frames: f2 } = parseSseBuffer(r1 + chunk2);
    expect(f2).toHaveLength(1);
    expect(f2[0].data.delta).toBe('hello world');
  });

  it('multiple text_delta events are accumulated into one text block', () => {
    const events: AgentEvent[] = [
      { type: 'text_delta', delta: 'Hello' },
      { type: 'text_delta', delta: ' ' },
      { type: 'text_delta', delta: 'world' },
    ];
    const blocks = buildBlocks(events);
    expect(blocks).toHaveLength(1);
    expect(blocks[0]).toEqual({ kind: 'text', content: 'Hello world' });
  });

  it('session_id is extracted from session frame', () => {
    const frame = parseSseFrame('event: session\ndata: {"session_id":"abc-123"}');
    expect(frame?.data.session_id).toBe('abc-123');
  });

  it('error frame is correctly parsed', () => {
    const frame = parseSseFrame('event: error\ndata: {"message":"API error: 400"}');
    expect(frame?.event).toBe('error');
    expect(frame?.data.message).toBe('API error: 400');
  });
});
