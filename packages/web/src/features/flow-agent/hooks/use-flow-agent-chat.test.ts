import { describe, it, expect } from 'vitest';

import { parseSseBuffer, parseSseFrame } from '../lib/sse-parser';

// ── parseSseFrame ─────────────────────────────────────────────────────────────

describe('parseSseFrame', () => {
  it('parses a valid frame', () => {
    const raw = 'event: text_delta\ndata: {"delta":"hello"}';
    const frame = parseSseFrame(raw);
    expect(frame).toEqual({ event: 'text_delta', data: { delta: 'hello' } });
  });

  it('returns null for empty string', () => {
    expect(parseSseFrame('')).toBeNull();
  });

  it('returns null when event is missing', () => {
    expect(parseSseFrame('data: {"delta":"x"}')).toBeNull();
  });

  it('returns null when data is missing', () => {
    expect(parseSseFrame('event: done')).toBeNull();
  });

  it('returns null when JSON is invalid', () => {
    expect(parseSseFrame('event: text_delta\ndata: not-json')).toBeNull();
  });

  it('trims event name whitespace', () => {
    const frame = parseSseFrame('event:  session  \ndata: {"session_id":"abc"}');
    expect(frame?.event).toBe('session');
  });
});

// ── parseSseBuffer ────────────────────────────────────────────────────────────

describe('parseSseBuffer', () => {
  it('splits on double newline and returns frames', () => {
    const buffer =
      'event: session\ndata: {"session_id":"s1"}\n\nevent: done\ndata: {}\n\n';
    const { frames, remaining } = parseSseBuffer(buffer);
    expect(frames).toHaveLength(2);
    expect(frames[0].event).toBe('session');
    expect(frames[1].event).toBe('done');
    expect(remaining).toBe('');
  });

  it('keeps incomplete frame in remaining', () => {
    const buffer = 'event: text_delta\ndata: {"delta":"hi"}\n\nevent: tool_call';
    const { frames, remaining } = parseSseBuffer(buffer);
    expect(frames).toHaveLength(1);
    expect(remaining).toBe('event: tool_call');
  });

  it('handles empty buffer', () => {
    const { frames, remaining } = parseSseBuffer('');
    expect(frames).toHaveLength(0);
    expect(remaining).toBe('');
  });

  it('skips blank frames', () => {
    const buffer = 'event: done\ndata: {}\n\n\n\n';
    const { frames } = parseSseBuffer(buffer);
    expect(frames).toHaveLength(1);
  });

  it('accumulates multiple data across calls by prepending remaining', () => {
    const part1 = 'event: text_delta\ndata: {"delta"';
    const part2 = ':"hello"}\n\n';
    const { remaining } = parseSseBuffer(part1);
    const { frames } = parseSseBuffer(remaining + part2);
    expect(frames).toHaveLength(1);
    expect(frames[0].data).toEqual({ delta: 'hello' });
  });
});
