"""
Prompt-injection detection for the user's topic and style, in English, Modern Standard
Arabic, Egyptian Arabic and Arabizi.

Swan only needs a subject and a tone, so text that tries to give the model orders,
change its role or read back its instructions has no legitimate use here. The
patterns are deliberately narrow: "ignore the rules", "act as a leader" and
"بدون قيود" are fine topics for a quote, so only phrases aimed at the model match.
This is one layer; the system instruction, the quoting of user text and the output
checks are the others.
"""

import re
from dataclasses import dataclass

from app.guardrails.normalize import normalize, squash


@dataclass(frozen=True)
class Finding:
    field: str  # "topic" or "style"
    rule: str  # which pattern matched, for logs and metrics


# Up to three words between a verb and its object: "ignore all of your previous instructions"
GAP = r"(?:\W+\w+){0,3}?\W+"

# Patterns run on normalize()d text: lowercase, and Arabic with أ/إ/آ → ا, ى → ي, ة → ه
# and no diacritics, so they are written in that form.
WORD_RULES: dict[str, re.Pattern[str]] = {
    "override_en": re.compile(
        rf"\b(?:ignore|disregard|forget|override|bypass)\b{GAP}"
        r"(?:instructions?|prompts?|directives?|programming)\b"
    ),
    "override_rules_en": re.compile(
        rf"\b(?:ignore|disregard|forget|override|bypass)\b{GAP}"
        r"(?:previous|prior|above|earlier|system|safety|original|your)\W+"
        r"(?:rules|guidelines|constraints|filters|context)\b"
    ),
    "new_instructions_en": re.compile(
        r"\b(?:new|updated|real|actual)\W+(?:instructions?|task|system\W+prompt)\s*:"
    ),
    "role_en": re.compile(
        r"\b(?:you\W+are\W+now|from\W+now\W+on\W+you(?:\W+are)?|act\W+as|pretend\W+(?:to\W+be|you\W+are)|"
        r"roleplay\W+as)\W+(?:an?\W+)?(?:ai|assistant|chatbot|model|llm|unfiltered|unrestricted|"
        r"uncensored|jailbroken|evil|different)\b"
    ),
    "jailbreak_en": re.compile(
        r"\b(?:developer\W+mode|jailbreak|jailbroken|do\W+anything\W+now|dan\W+mode)\b"
    ),
    "exfiltrate_en": re.compile(
        r"\b(?:reveal|print|show|repeat|output|display|leak|tell\W+me|what\W+(?:is|are))\b"
        r"(?:\W+me)?\W+(?:your\W+(?:system\W+|hidden\W+|initial\W+|original\W+)?|the\W+(?:system|hidden|initial)\W+)"
        r"(?:prompt|instructions?|rules|message|configuration)\b"
    ),
    "system_prompt_en": re.compile(r"\bsystem\W+(?:prompt|instructions?|message)\b"),
    "chat_markup": re.compile(
        r"<\|?\s*/?\s*(?:system|assistant|user|im_start|im_end|instructions?)\s*\|?>"
        r"|\[/?(?:inst|system)\]|#{2,}\s*(?:instruction|system)|^\s*(?:system|assistant)\s*:"
    ),
    "override_ar": re.compile(
        rf"(?<!\w)(?:تجاهل|اهمل|انس|انسي|تناسي|تخط|تخطي|تجاوز|الغ|الغي|متسمعش|ماتسمعش)(?!\w){GAP}"
        r"(?:ال)?(?:تعليمات|اوامر|توجيهات|برومبت|كلام\W+اللي\W+فوق)"
    ),
    "override_rules_ar": re.compile(
        rf"(?<!\w)(?:تجاهل|اهمل|انس|انسي|تخط|تخطي|تجاوز|الغ|الغي)(?!\w){GAP}"
        r"(?:ال)?(?:قواعد|قيود|ضوابط)\W+(?:ال)?(?:سابقه|اصليه|النظام|بتاعتك|الخاصه\W+بك)"
    ),
    "role_ar": re.compile(
        r"(?<!\w)(?:انت\W+(?:الان|دلوقتي|من\W+دلوقتي)|من\W+الان\W+انت|تظاهر\W+(?:بانك|انك)|"
        r"اعمل\W+نفسك|العب\W+دور|مثل\W+دور)(?!\w)"
        rf"(?:{GAP})?(?:مساعد|نموذج|ذكاء\W+اصطناعي|بوت|شات\W*بوت|غير\W+مقيد|بلا\W+قيود|شرير)"
    ),
    "jailbreak_ar": re.compile(r"(?<!\w)(?:وضع\W+المطور|جيلبريك|جيلبرك)(?!\w)"),
    "exfiltrate_ar": re.compile(
        rf"(?<!\w)(?:اكشف|اطبع|اعرض|كرر|اظهر|قول(?:لي)?|اكتب(?:لي)?|ايه\W+هي|ما\W+هي|وريني)(?!\w){GAP}"
        r"(?:ال)?(?:تعليمات|اوامر|برومبت|موجه)\W+(?:ال)?"
        r"(?:نظام|سريه|بتاعتك|الخاصه\W+بك|الاصليه|المخفيه|اللي\W+اتقالتلك)"
    ),
    "system_prompt_ar": re.compile(
        r"(?<!\w)(?:موجه|تعليمات|رساله)\W+النظام(?!\w)|(?<!\w)(?:سيستم|السيستم)\W+برومبت(?!\w)"
    ),
    "override_arabizi": re.compile(
        r"\b(?:t?ga+hel|etga+hel|tagahol|2?ensa|insa|ensy|2ensy)\b"
        r"(?:\W+\w+){0,3}?\W+(?:el\W*)?(?:ta3limat|t3limat|ta3leemat|awamer|2awamer)\b"
    ),
}

# Patterns run on squash()ed text, which has no spaces left: only long, specific
# strings, since short ones would match inside ordinary words.
SQUASHED_RULES: dict[str, re.Pattern[str]] = {
    "override_en": re.compile(
        r"(?:ignore|disregard|forget|override|bypass)"
        r"(?:all|any|the|your|my|of|previous|prior|above|earlier|system)*"
        r"(?:instructions?|prompts?)"
    ),
    "system_prompt_en": re.compile(r"systemprompt|developermode|doanythingnow"),
    "override_ar": re.compile(
        r"(?:تجاهل|اهمل|انسي|تخطي|تجاوز)(?:كل|جميع)?(?:ال)?(?:تعليمات|اوامر|توجيهات)"
    ),
    "system_prompt_ar": re.compile(r"موجهالنظام|تعليماتالنظام|وضعالمطور"),
}


def scan_text(field: str, text: str | None) -> Finding | None:
    """Return the first rule `text` matches, or None."""
    if not text:
        return None
    normalized = normalize(text)
    for rule, pattern in WORD_RULES.items():
        if pattern.search(normalized):
            return Finding(field, rule)
    squashed = squash(text)
    for rule, pattern in SQUASHED_RULES.items():
        if pattern.search(squashed):
            return Finding(field, f"{rule}_squashed")
    return None


def scan_request(**fields: str | None) -> Finding | None:
    """Scan each user-written field, e.g. scan_request(topic=..., style=...)."""
    for field, text in fields.items():
        finding = scan_text(field, text)
        if finding:
            return finding
    return None
