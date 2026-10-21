/**
 * Checks on the model's answer before it reaches the person: the browser port of
 * app/guardrails/output.py.
 *
 * Each failed check is a violation {check, hint}. Its hint goes back to the model when
 * the person asks for a repair, so it says what to do differently; it never repeats the
 * model's output.
 */
import { normalize, otherScriptLetters, py, scriptShare } from './normalize';

// Accepted word counts per requested length. Loose on purpose: Arabic packs more into
// a word than English, and a quote a few words off is still a good quote. The point is
// to catch a cut-off answer or an essay.
export const WORD_RANGES = { short: [3, 30], medium: [6, 50], long: [12, 90] };

// The share of letters that must be in the requested script
const MIN_SCRIPT_SHARE = 0.9;

const MAX_LINES = 4;

// Run on normalize()d text. Phrases a model adds around a quote, never ones a quote
// might contain: "Love needs no translation." is fine, "Translation: ..." is not.
const META = py(
  String.raw`^(?:as an? (?:ai|language model)|here(?: is|['’]s| are) (?:your |a |an |the )?` +
    String.raw`(?:quote|response|answer)|sure[,!]|certainly[,!]|of course[,!]|quote:|` +
    String.raw`(?:بالطبع|بالتاكيد)\W|اليك\W+(?:ال)?اقتباس|هذا\W+(?:هو\W+)?(?:ال)?اقتباس|اقتباس\s*:)` +
    String.raw`|\btranslation\s*:|\b(?:english|arabic) translation\b|الترجمه\s*:`,
);
// The model declining in its own words, inside an otherwise valid answer. Narrow, so a
// quote like "I cannot change the wind..." or «لا أستطيع أن أنسى أمي» is still a quote.
// Run on normalize()d text: Arabic without hamza on alef, with ه for ة and ي for ى.
const REFUSAL = py(
  String.raw`\bi (?:cannot|can['’]?t|can not|won['’]?t|will not|am unable to|am not able to) ` +
    String.raw`(?:fulfill|comply with|help with|assist with|generate|create|write|provide|produce)` +
    String.raw`(?: (?:this|that|your|such|any|the))? (?:request|content|quote|material|kind of)\b` +
    String.raw`|\bi (?:cannot|can['’]?t|won['’]?t|will not) (?:fulfill|comply)\b` +
    String.raw`|\bi do not (?:generate|create|produce|write) (?:content|material|quotes?) that\b` +
    String.raw`|^(?:i['’]?m sorry|i apologi[sz]e|sorry),? (?:but )?i (?:can['’]?t|cannot|won['’]?t|am unable)` +
    String.raw`|لا (?:استطيع|يمكنني|اقدر|يمكن) (?:تلبيه|تنفيذ|المساعده|انشاء|كتابه|تقديم) ` +
    String.raw`(?:هذا|هذه|ذلك|مثل|اي|محتوي|الطلب|طلبك)` +
    String.raw`|^(?:عذرا|اعتذر|اسف|اسفه|معلش)\W+(?:\w+\W+){0,2}?(?:لا|لن|مش|ما)\b` +
    String.raw`|(?:هذا|هذه) الطلب|مش هقدر (?:اكتب|اساعد)`,
);
const MARKDOWN = py(String.raw`\*\*|__|^#+\s|^\s*(?:[-*•]|\d+[.)])\s`, 'm');
const WORD = py(String.raw`\w+`, 'g');

export function wordCount(text) {
  return text.split(/\s+/u).filter(Boolean).length;
}

/** True if the quote repeats any run of `n` words from the instructions. */
export function leaksInstructions(normalizedQuote, instructions, n = 6) {
  const words = normalize(instructions).match(WORD) ?? [];
  const shingles = new Set();
  for (let i = 0; i + n <= words.length; i += 1) shingles.add(words.slice(i, i + n).join(' '));
  const quoteWords = normalizedQuote.match(WORD) ?? [];
  for (let i = 0; i + n <= quoteWords.length; i += 1) {
    if (shingles.has(quoteWords.slice(i, i + n).join(' '))) return true;
  }
  return false;
}

/**
 * Every check the quote fails; empty if it is fine to show.
 * `finishReason` is "max_tokens" when the answer hit the output ceiling. Gemini's
 * "recitation" stop has no Claude counterpart, so that check is not here.
 */
export function checkQuote(quote, { language, length, finishReason, instructions }) {
  if (REFUSAL.test(normalize(quote))) return [{ check: 'refusal', hint: '' }]; // final: see quote.js
  if (!quote.trim()) {
    if (finishReason === 'max_tokens') return [{ check: 'truncated', hint: 'Keep the quote short enough to finish.' }];
    return [{ check: 'empty', hint: 'Write the quote; the answer was empty.' }];
  }

  const violations = [];
  if (finishReason === 'max_tokens') violations.push({ check: 'truncated', hint: 'Keep the quote short enough to finish.' });

  const [arabic, latin] = scriptShare(quote);
  if (otherScriptLetters(quote)) {
    violations.push({
      check: 'language',
      hint: `Write the quote entirely in ${language === 'ar' ? 'Arabic' : 'English'}, with no letters from any other script.`,
    });
  } else if (language === 'ar' && arabic < MIN_SCRIPT_SHARE) {
    violations.push({ check: 'language', hint: 'Write the quote entirely in Arabic, with no other language.' });
  } else if (language === 'en' && latin < MIN_SCRIPT_SHARE) {
    violations.push({ check: 'language', hint: 'Write the quote entirely in English, with no other language.' });
  }

  const [low, high] = WORD_RANGES[length];
  const words = wordCount(quote);
  if (words < low) violations.push({ check: 'length', hint: `Write at least ${low} words.` });
  else if (words > high) violations.push({ check: 'length', hint: `Write at most ${high} words.` });

  const normalized = normalize(quote);
  const lines = quote.split(/\r\n|\r|\n/).filter((line) => line.trim());
  if (META.test(normalized) || MARKDOWN.test(quote) || lines.length > MAX_LINES) {
    violations.push({
      check: 'format',
      hint: 'Give only the quote itself: no introduction, translation, list or formatting.',
    });
  }

  if (leaksInstructions(normalized, instructions)) {
    violations.push({ check: 'leak', hint: 'Write a quote about the topic; do not mention your instructions.' });
  }
  return violations;
}

const WRAPPING_MARKS = /^["'“”«»„‟]+|["'“”«»„‟]+$/gu;

/** Strip whitespace and the quotation marks models like to wrap quotes in. */
export function cleanQuote(text) {
  return text.trim().replace(WRAPPING_MARKS, '').trim();
}
