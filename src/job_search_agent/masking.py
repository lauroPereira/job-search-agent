"""Masking of personal data, before the embeddings and in the trace.

Replaced by markers: e-mails, personal profile links, CPF, phone numbers, other long numbers and
the names of `[masking] names` (compared without accents and case). Company names stay, because
the search needs them.
"""

import re
import unicodedata
from collections.abc import Iterable
from functools import lru_cache

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PROFILE = re.compile(
    r"(?:https?://)?(?:[\w-]+\.)?"
    r"(?:linkedin\.com/(?:in|pub)|github\.com|instagram\.com|facebook\.com|twitter\.com|x\.com)"
    r"/[\w./%-]+",
    re.IGNORECASE,
)
CPF = re.compile(r"(?<![\w.-])\d{3}[.\s]\d{3}[.\s]\d{3}[-\s]\d{2}(?![\w-])|(?<!\d)\d{11}(?!\d)")
# A pair of years ("2019-2023", "2019 2023") is not a phone number.
_NOT_YEARS = r"(?!(?:19|20)\d\d[-\s](?:19|20)\d\d(?!\d))"
# Mobile: 9 + 8 digits, area code optional. Landline (8 digits): area code required.
PHONE = re.compile(
    r"(?<![\w+])(?:\+55\s?)?"
    r"(?:(?:\(\d{2}\)\s?|\d{2}\s?)?9(?:\s" + _NOT_YEARS + r")?\d{4}[-\s]?\d{4}"
    r"|(?:\(\d{2}\)\s?|\d{2}\s)" + _NOT_YEARS + r"\d{4}[-\s]?\d{4})"
    r"(?!\d)"
)
LONG_NUMBER = re.compile(r"(?<!\d)\d{8,}(?!\d)")

# In order: the e-mail before the link and the CPF before the phone and the long number.
PATTERNS = (
    (EMAIL, "[email]"),
    (PROFILE, "[perfil]"),
    (CPF, "[cpf]"),
    (PHONE, "[telefone]"),
    (LONG_NUMBER, "[numero]"),
)
PERSON = "[pessoa]"


def fold(text: str) -> str:
    """Lowercase without accents, keeping one character per character (same positions)."""
    folded = []
    for character in text:
        base = unicodedata.normalize("NFD", character)[0].lower()
        folded.append(base if len(base) == 1 else character)
    return "".join(folded)


@lru_cache(maxsize=8)
def _names_pattern(names: tuple[str, ...]) -> re.Pattern | None:
    parts = sorted({fold(name).strip() for name in names if name.strip()}, key=len, reverse=True)
    if not parts:
        return None
    alternatives = (r"\s+".join(map(re.escape, part.split())) for part in parts)
    return re.compile(r"(?<!\w)(?:" + "|".join(alternatives) + r")(?!\w)")


def mask(text: str, names: Iterable[str] = ()) -> str:
    """Return `text` with personal data replaced by markers."""
    pattern = _names_pattern(tuple(names))
    if pattern is not None:
        # Search the folded text and replace the same positions in the original.
        pieces, last = [], 0
        for found in pattern.finditer(fold(text)):
            pieces += [text[last : found.start()], PERSON]
            last = found.end()
        text = "".join(pieces) + text[last:]
    for regex, marker in PATTERNS:
        text = regex.sub(marker, text)
    return text
