"""
Checks on the model's answer before it reaches the user.

Each failed check is a Violation. Its `hint` goes back to the model when the quote is
regenerated, so it says what to do differently; it never repeats the model's output.
"""

import re
from dataclasses import dataclass

from app.guardrails.normalize import normalize, other_script_letters, script_share


@dataclass(frozen=True)
class Violation:
    check: (
        str  # "refusal", "empty", "truncated", "recitation", "language", "length", "format", "leak"
    )
    hint: str


# Accepted word counts per requested length. Loose on purpose: Arabic packs more into
# a word than English, and a quote a few words off is still a good quote. The point is
# to catch a cut-off answer or an essay.
WORD_RANGES = {"short": (3, 30), "medium": (6, 50), "long": (12, 90)}

# The share of letters that must be in the requested script
MIN_SCRIPT_SHARE = 0.9

MAX_LINES = 4

# Run on normalize()d text. Phrases a model adds around a quote, never ones a quote
# might contain: "Love needs no translation." is fine, "Translation: ..." is not.
META = re.compile(
    r"^(?:as an? (?:ai|language model)|here(?: is|['’]s| are) (?:your |a |an |the )?"
    r"(?:quote|response|answer)|sure[,!]|certainly[,!]|of course[,!]|quote:|"
    r"(?:بالطبع|بالتاكيد)\W|اليك\W+(?:ال)?اقتباس|هذا\W+(?:هو\W+)?(?:ال)?اقتباس|اقتباس\s*:)"
    r"|\btranslation\s*:|\b(?:english|arabic) translation\b|الترجمه\s*:"
)
# The model declining in its own words, inside an otherwise valid answer. Narrow, so a
# quote like "I cannot change the wind..." or «لا أستطيع أن أنسى أمي» is still a quote.
# Run on normalize()d text: Arabic without hamza on alef, with ه for ة and ي for ى.
REFUSAL = re.compile(
    r"\bi (?:cannot|can['’]?t|can not|won['’]?t|will not|am unable to|am not able to) "
    r"(?:fulfill|comply with|help with|assist with|generate|create|write|provide|produce)"
    r"(?: (?:this|that|your|such|any|the))? (?:request|content|quote|material|kind of)\b"
    r"|\bi (?:cannot|can['’]?t|won['’]?t|will not) (?:fulfill|comply)\b"
    r"|\bi do not (?:generate|create|produce|write) (?:content|material|quotes?) that\b"
    r"|^(?:i['’]?m sorry|i apologi[sz]e|sorry),? (?:but )?i (?:can['’]?t|cannot|won['’]?t|am unable)"
    r"|لا (?:استطيع|يمكنني|اقدر|يمكن) (?:تلبيه|تنفيذ|المساعده|انشاء|كتابه|تقديم) "
    r"(?:هذا|هذه|ذلك|مثل|اي|محتوي|الطلب|طلبك)"
    r"|^(?:عذرا|اعتذر|اسف|اسفه|معلش)\W+(?:\w+\W+){0,2}?(?:لا|لن|مش|ما)\b"
    r"|(?:هذا|هذه) الطلب|مش هقدر (?:اكتب|اساعد)"
)
MARKDOWN = re.compile(r"\*\*|__|^#+\s|^\s*(?:[-*•]|\d+[.)])\s", re.MULTILINE)


def word_count(text: str) -> int:
    return len(text.split())


def check_quote(
    quote: str,
    *,
    language: str,
    length: str,
    finish_reason: str,
    instructions: str,
) -> list[Violation]:
    """Every check the quote fails; empty if it is fine to show."""
    if finish_reason == "recitation":
        return [Violation("recitation", "Write an original quote, not an existing one.")]
    if REFUSAL.search(normalize(quote)):
        return [Violation("refusal", "")]  # not regenerated: see quote_controller
    if not quote.strip():
        if finish_reason == "max_tokens":
            return [Violation("truncated", "Keep the quote short enough to finish.")]
        return [Violation("empty", "Write the quote; the answer was empty.")]

    violations = []
    if finish_reason == "max_tokens":
        violations.append(Violation("truncated", "Keep the quote short enough to finish."))

    arabic, latin = script_share(quote)
    if other_script_letters(quote):
        violations.append(
            Violation(
                "language",
                f"Write the quote entirely in {'Arabic' if language == 'ar' else 'English'}, "
                "with no letters from any other script.",
            )
        )
    elif language == "ar" and arabic < MIN_SCRIPT_SHARE:
        violations.append(
            Violation("language", "Write the quote entirely in Arabic, with no other language.")
        )
    elif language == "en" and latin < MIN_SCRIPT_SHARE:
        violations.append(
            Violation("language", "Write the quote entirely in English, with no other language.")
        )

    low, high = WORD_RANGES[length]
    words = word_count(quote)
    if words < low:
        violations.append(Violation("length", f"Write at least {low} words."))
    elif words > high:
        violations.append(Violation("length", f"Write at most {high} words."))

    normalized = normalize(quote)
    lines = [line for line in quote.splitlines() if line.strip()]
    if META.search(normalized) or MARKDOWN.search(quote) or len(lines) > MAX_LINES:
        violations.append(
            Violation(
                "format",
                "Give only the quote itself: no introduction, translation, list or formatting.",
            )
        )

    if leaks_instructions(normalized, instructions):
        violations.append(
            Violation("leak", "Write a quote about the topic; do not mention your instructions.")
        )
    return violations


def leaks_instructions(normalized_quote: str, instructions: str, n: int = 6) -> bool:
    """True if the quote repeats any run of `n` words from the instructions."""
    words = re.findall(r"\w+", normalize(instructions))
    shingles = {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}
    quote_words = re.findall(r"\w+", normalized_quote)
    return any(
        " ".join(quote_words[i : i + n]) in shingles for i in range(len(quote_words) - n + 1)
    )


def clean_quote(text: str) -> str:
    """Strip whitespace and the quotation marks models like to wrap quotes in."""
    return text.strip().strip("\"'“”«»„‟").strip()
