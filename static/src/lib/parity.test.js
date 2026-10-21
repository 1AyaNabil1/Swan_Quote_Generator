// The browser guardrails against the Python ones, string for string. The fixture is
// written by scripts/guardrail_parity.py from the backend's own tests and eval cases.
import fixture from './parity.fixture.json';
import { scanText } from './injection';
import { normalize, squash } from './normalize';
import { checkQuote, cleanQuote } from './output';

const cases = fixture.cases;

test('the fixture covers attacks and ordinary text', () => {
  expect(cases.length).toBeGreaterThan(150);
  expect(cases.filter((c) => c.scan).length).toBeGreaterThan(40);
});

test.each(cases.map((c) => [c.text, c]))('normalizes %j as Python does', (_, c) => {
  expect(normalize(c.text)).toBe(c.normalize);
  expect(squash(c.text)).toBe(c.squash);
  expect(cleanQuote(c.text)).toBe(c.clean);
});

test.each(cases.map((c) => [c.text, c]))('scans %j as Python does', (_, c) => {
  expect(scanText('topic', c.text)?.rule ?? null).toBe(c.scan);
});

test.each(cases.map((c) => [c.text, c]))('checks %j as Python does', (_, c) => {
  for (const [key, expected] of Object.entries(c.check)) {
    const [language, finishReason] = key.split('-');
    const got = checkQuote(c.text, { language, length: 'medium', finishReason, instructions: fixture.instructions });
    expect([key, got.map((v) => [v.check, v.hint])]).toEqual([key, expected]);
  }
});
