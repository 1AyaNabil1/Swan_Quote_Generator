import { SIZES, THEMES, wrapText } from './quoteCard';

// 10px per character, like a monospace font
const ctx = { measureText: (text) => ({ width: text.length * 10 }) };

test('wraps at the width and keeps every word', () => {
  const lines = wrapText(ctx, 'Keep going; the road remembers every step.', 120);
  expect(lines).toEqual(['Keep going;', 'the road', 'remembers', 'every step.']);
  expect(lines.every((line) => line.length * 10 <= 120)).toBe(true);
});

test('a word longer than the width gets its own line', () => {
  expect(wrapText(ctx, 'a extraordinarily b', 50)).toEqual(['a', 'extraordinarily', 'b']);
});

test('wraps Arabic by words too', () => {
  expect(wrapText(ctx, 'الصبر مفتاح الفرج', 110)).toEqual(['الصبر مفتاح', 'الفرج']);
});

test('sizes and themes are complete', () => {
  expect(SIZES.story).toMatchObject({ width: 1080, height: 1920 });
  Object.values(THEMES).forEach((theme) => {
    expect(theme.label.en && theme.label.ar && theme.text && theme.from && theme.to).toBeTruthy();
  });
});
