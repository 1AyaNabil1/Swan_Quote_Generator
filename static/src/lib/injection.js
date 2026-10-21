/**
 * Prompt-injection detection for the user's topic and style, in English, Modern Standard
 * Arabic, Egyptian Arabic and Arabizi: the browser port of app/guardrails/injection.py.
 *
 * Swan only needs a subject and a tone, so text that tries to give the model orders,
 * change its role or read back its instructions has no legitimate use here. The
 * patterns are deliberately narrow: "ignore the rules", "act as a leader" and
 * "بدون قيود" are fine topics for a quote, so only phrases aimed at the model match.
 * On Zibby the person pays for every call, so this also spares them a charge for a
 * request that would only be refused.
 */
import { normalize, py, squash } from './normalize';

// Up to three words between a verb and its object: "ignore all of your previous instructions"
const GAP = String.raw`(?:\W+\w+){0,3}?\W+`;

// Patterns run on normalize()d text: lowercase, and Arabic with أ/إ/آ → ا, ى → ي, ة → ه
// and no diacritics, so they are written in that form.
const WORD_RULES = {
  override_en: py(
    String.raw`\b(?:ignore|disregard|forget|override|bypass)\b${GAP}` +
      String.raw`(?:instructions?|prompts?|directives?|programming)\b`,
  ),
  override_rules_en: py(
    String.raw`\b(?:ignore|disregard|forget|override|bypass)\b${GAP}` +
      String.raw`(?:previous|prior|above|earlier|system|safety|original|your)\W+` +
      String.raw`(?:rules|guidelines|constraints|filters|context)\b`,
  ),
  new_instructions_en: py(String.raw`\b(?:new|updated|real|actual)\W+(?:instructions?|task|system\W+prompt)\s*:`),
  role_en: py(
    String.raw`\b(?:you\W+are\W+now|from\W+now\W+on\W+you(?:\W+are)?|act\W+as|pretend\W+(?:to\W+be|you\W+are)|` +
      String.raw`roleplay\W+as)\W+(?:an?\W+)?(?:ai|assistant|chatbot|model|llm|unfiltered|unrestricted|` +
      String.raw`uncensored|jailbroken|evil|different)\b`,
  ),
  jailbreak_en: py(String.raw`\b(?:developer\W+mode|jailbreak|jailbroken|do\W+anything\W+now|dan\W+mode)\b`),
  exfiltrate_en: py(
    String.raw`\b(?:reveal|print|show|repeat|output|display|leak|tell\W+me|what\W+(?:is|are))\b` +
      String.raw`(?:\W+me)?\W+(?:your\W+(?:system\W+|hidden\W+|initial\W+|original\W+)?|the\W+(?:system|hidden|initial)\W+)` +
      String.raw`(?:prompt|instructions?|rules|message|configuration)\b`,
  ),
  system_prompt_en: py(String.raw`\bsystem\W+(?:prompt|instructions?|message)\b`),
  chat_markup: py(
    String.raw`<\|?\s*/?\s*(?:system|assistant|user|im_start|im_end|instructions?)\s*\|?>` +
      String.raw`|\[/?(?:inst|system)\]|#{2,}\s*(?:instruction|system)|^\s*(?:system|assistant)\s*:`,
  ),
  override_ar: py(
    String.raw`(?<!\w)(?:تجاهل|اهمل|انس|انسي|تناسي|تخط|تخطي|تجاوز|الغ|الغي|متسمعش|ماتسمعش)(?!\w)${GAP}` +
      String.raw`(?:ال)?(?:تعليمات|اوامر|توجيهات|برومبت|كلام\W+اللي\W+فوق)`,
  ),
  override_rules_ar: py(
    String.raw`(?<!\w)(?:تجاهل|اهمل|انس|انسي|تخط|تخطي|تجاوز|الغ|الغي)(?!\w)${GAP}` +
      String.raw`(?:ال)?(?:قواعد|قيود|ضوابط)\W+(?:ال)?(?:سابقه|اصليه|النظام|بتاعتك|الخاصه\W+بك)`,
  ),
  role_ar: py(
    String.raw`(?<!\w)(?:انت\W+(?:الان|دلوقتي|من\W+دلوقتي)|من\W+الان\W+انت|تظاهر\W+(?:بانك|انك)|` +
      String.raw`اعمل\W+نفسك|العب\W+دور|مثل\W+دور)(?!\w)` +
      String.raw`(?:${GAP})?(?:مساعد|نموذج|ذكاء\W+اصطناعي|بوت|شات\W*بوت|غير\W+مقيد|بلا\W+قيود|شرير)`,
  ),
  jailbreak_ar: py(String.raw`(?<!\w)(?:وضع\W+المطور|جيلبريك|جيلبرك)(?!\w)`),
  exfiltrate_ar: py(
    String.raw`(?<!\w)(?:اكشف|اطبع|اعرض|كرر|اظهر|قول(?:لي)?|اكتب(?:لي)?|ايه\W+هي|ما\W+هي|وريني)(?!\w)${GAP}` +
      String.raw`(?:ال)?(?:تعليمات|اوامر|برومبت|موجه)\W+(?:ال)?` +
      String.raw`(?:نظام|سريه|بتاعتك|الخاصه\W+بك|الاصليه|المخفيه|اللي\W+اتقالتلك)`,
  ),
  system_prompt_ar: py(
    String.raw`(?<!\w)(?:موجه|تعليمات|رساله)\W+النظام(?!\w)|(?<!\w)(?:سيستم|السيستم)\W+برومبت(?!\w)`,
  ),
  override_arabizi: py(
    String.raw`\b(?:t?ga+hel|etga+hel|tagahol|2?ensa|insa|ensy|2ensy)\b` +
      String.raw`(?:\W+\w+){0,3}?\W+(?:el\W*)?(?:ta3limat|t3limat|ta3leemat|awamer|2awamer)\b`,
  ),
};

// Patterns run on squash()ed text, which has no spaces left: only long, specific
// strings, since short ones would match inside ordinary words.
const SQUASHED_RULES = {
  override_en: py(
    String.raw`(?:ignore|disregard|forget|override|bypass)` +
      String.raw`(?:all|any|the|your|my|of|previous|prior|above|earlier|system)*` +
      String.raw`(?:instructions?|prompts?)`,
  ),
  system_prompt_en: py(String.raw`systemprompt|developermode|doanythingnow`),
  override_ar: py(String.raw`(?:تجاهل|اهمل|انسي|تخطي|تجاوز)(?:كل|جميع)?(?:ال)?(?:تعليمات|اوامر|توجيهات)`),
  system_prompt_ar: py(String.raw`موجهالنظام|تعليماتالنظام|وضعالمطور`),
};

/** The first rule `text` matches, as {field, rule}, or null. */
export function scanText(field, text) {
  if (!text) return null;
  const normalized = normalize(text);
  for (const [rule, pattern] of Object.entries(WORD_RULES)) {
    if (pattern.test(normalized)) return { field, rule };
  }
  const squashed = squash(text);
  for (const [rule, pattern] of Object.entries(SQUASHED_RULES)) {
    if (pattern.test(squashed)) return { field, rule: `${rule}_squashed` };
  }
  return null;
}

/** Scan each user-written field, e.g. scanRequest({ topic, style }). */
export function scanRequest(fields) {
  for (const [field, text] of Object.entries(fields)) {
    const finding = scanText(field, text);
    if (finding) return finding;
  }
  return null;
}
