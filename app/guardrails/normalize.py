"""
Text normalization for matching, in English and Arabic.

Attackers hide trigger phrases with invisible characters, diacritics, letter variants,
presentation forms, full-width letters or spacing. Matching is done on text with all
of that folded away; the user's text itself is never changed.
"""

import re
import unicodedata


# Zero-width characters, bidi controls and the soft hyphen
INVISIBLE = re.compile("[\u00ad\u061c\u180e\u200b-\u200f\u202a-\u202e\u2060-\u2069\ufeff]")
# Arabic diacritics (tashkeel), Quranic marks, superscript alef, and tatweel
ARABIC_MARKS = re.compile("[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed\u0640]")
# Letter variants that people write interchangeably
ARABIC_LETTERS = str.maketrans(
    {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"}
)
# Arabic letters, without tatweel (U+0640)
ARABIC_LETTER = re.compile(
    "[\u0620-\u063f\u0641-\u064a\u066e-\u06d3\u06fa-\u06ff\u0750-\u077f\u08a0-\u08ff]"
)
LATIN_LETTER = re.compile("[A-Za-z\u00c0-\u024f]")


def normalize(text: str) -> str:
    """Fold case, width, presentation forms, invisible characters, diacritics and
    Arabic letter variants; collapse whitespace."""
    text = unicodedata.normalize("NFKC", text)  # presentation forms, full-width letters
    text = INVISIBLE.sub("", text)
    text = ARABIC_MARKS.sub("", text)
    text = text.translate(ARABIC_LETTERS).casefold()
    return re.sub(r"\s+", " ", text).strip()


def squash(text: str) -> str:
    """normalize(), then drop everything but letters and digits, which undoes
    "i g n o r e" and "i.g.n.o.r.e" style spacing."""
    return re.sub(r"[\W_]+", "", normalize(text))


def other_script_letters(text: str) -> int:
    """Letters that are neither Arabic nor Latin, e.g. CJK or Cyrillic."""
    text = unicodedata.normalize("NFKC", text).replace("\u0640", "")
    return sum(
        1
        for ch in text
        if ch.isalpha() and not ARABIC_LETTER.match(ch) and not LATIN_LETTER.match(ch)
    )


def script_share(text: str) -> tuple[float, float]:
    """The shares of letters that are Arabic and Latin, as (arabic, latin)."""
    text = unicodedata.normalize("NFKC", text)
    arabic = len(ARABIC_LETTER.findall(text))
    latin = len(LATIN_LETTER.findall(text))
    total = arabic + latin
    if total == 0:
        return 0.0, 0.0
    return arabic / total, latin / total
