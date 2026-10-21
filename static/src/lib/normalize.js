/**
 * Text normalization for matching, in English and Arabic: the browser port of
 * app/guardrails/normalize.py, kept rule for rule so both say the same thing.
 *
 * Attackers hide trigger phrases with invisible characters, diacritics, letter variants,
 * presentation forms, full-width letters or spacing. Matching is done on text with all
 * of that folded away; the user's text itself is never changed.
 */

// Python's \w, \W, \b and \d are Unicode-aware; JavaScript's are ASCII-only, so the
// patterns are written as in Python and these stand in for them.
const W = '[\\p{L}\\p{N}_]';
const NW = '[^\\p{L}\\p{N}_]';
const B = `(?:(?<=${W})(?!${W})|(?<!${W})(?=${W}))`;

/** A pattern written as in Python (`String.raw`), with \w \W \b \d meaning what they mean there. */
export function py(source, flags = '') {
  const converted = source.replace(/\\([bwWd])/g, (_, c) =>
    c === 'b' ? B : c === 'w' ? W : c === 'W' ? NW : '\\p{Nd}',
  );
  return new RegExp(converted, `${flags}u`);
}

// Zero-width characters, bidi controls and the soft hyphen
const INVISIBLE = /[­؜᠎​-‏‪-‮⁠-⁩﻿]/gu;
// Arabic diacritics (tashkeel), Quranic marks, superscript alef, and tatweel
const ARABIC_MARKS = /[ؐ-ًؚ-ٰٟۖ-ۭـ]/gu;
// Letter variants that people write interchangeably
const ARABIC_LETTERS = { 'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي' };
const ARABIC_VARIANT = /[أإآٱىةؤئ]/gu;
// Arabic letters, without tatweel (U+0640)
const ARABIC_LETTER = /[ؠ-ؿف-يٮ-ۓۺ-ۿݐ-ݿࢠ-ࣿ]/u;
const LATIN_LETTER = /[A-Za-zÀ-ɏ]/u;
const LETTER = /\p{L}/u;

/** Fold case, width, presentation forms, invisible characters, diacritics and
 * Arabic letter variants; collapse whitespace. */
export function normalize(text) {
  return text
    .normalize('NFKC') // presentation forms, full-width letters
    .replace(INVISIBLE, '')
    .replace(ARABIC_MARKS, '')
    .replace(ARABIC_VARIANT, (ch) => ARABIC_LETTERS[ch])
    .toLowerCase()
    .replace(/ß/g, 'ss') // what Python's casefold() adds over lower()
    .replace(/\s+/gu, ' ')
    .trim();
}

/** normalize(), then drop everything but letters and digits, which undoes
 * "i g n o r e" and "i.g.n.o.r.e" style spacing. */
export function squash(text) {
  return normalize(text).replace(/[^\p{L}\p{N}]+/gu, '');
}

/** Letters that are neither Arabic nor Latin, e.g. CJK or Cyrillic. */
export function otherScriptLetters(text) {
  let count = 0;
  for (const ch of text.normalize('NFKC').replace(/ـ/g, '')) {
    if (LETTER.test(ch) && !ARABIC_LETTER.test(ch) && !LATIN_LETTER.test(ch)) count += 1;
  }
  return count;
}

/** The shares of letters that are Arabic and Latin, as [arabic, latin]. */
export function scriptShare(text) {
  let arabic = 0;
  let latin = 0;
  for (const ch of text.normalize('NFKC')) {
    if (ARABIC_LETTER.test(ch)) arabic += 1;
    else if (LATIN_LETTER.test(ch)) latin += 1;
  }
  const total = arabic + latin;
  return total === 0 ? [0, 0] : [arabic / total, latin / total];
}
