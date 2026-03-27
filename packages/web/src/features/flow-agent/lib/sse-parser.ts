/**
 * Pure SSE parsing utilities — framework-free, fully testable.
 */

export interface SseFrame {
  event: string;
  data: Record<string, unknown>;
}

/**
 * Split a raw SSE buffer into parsed frames.
 * Returns the parsed frames and the leftover buffer (incomplete frame).
 */
export function parseSseBuffer(
  buffer: string,
): { frames: SseFrame[]; remaining: string } {
  const parts = buffer.split('\n\n');
  const remaining = parts.pop() ?? '';
  const frames: SseFrame[] = [];

  for (const part of parts) {
    const frame = parseSseFrame(part);
    if (frame) frames.push(frame);
  }

  return { frames, remaining };
}

export function parseSseFrame(raw: string): SseFrame | null {
  if (!raw.trim()) return null;

  let eventType = '';
  let dataLine = '';

  for (const line of raw.split('\n')) {
    if (line.startsWith('event: ')) {
      eventType = line.slice(7).trim();
    } else if (line.startsWith('data: ')) {
      dataLine = line.slice(6);
    }
  }

  if (!eventType || !dataLine) return null;

  try {
    return { event: eventType, data: JSON.parse(dataLine) };
  } catch {
    return null;
  }
}
