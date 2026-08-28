"""Built-in thread splitter — no API keys, no network, just text.

Splits a post into pieces of at most ``limit`` characters, preferring to break
on paragraph boundaries, then sentences, then words, and only hard-splitting
mid-word as a last resort (e.g. a very long URL). The result is a list of
strings: the first is the root post, the rest are replies.
"""
from __future__ import annotations

import re

DEFAULT_LIMIT = 500

_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


def _hard_split(word: str, limit: int) -> list[str]:
    """Last resort: chop an oversized token (like a URL) into fixed-size pieces."""
    return [word[i:i + limit] for i in range(0, len(word), limit)]


def _split_long_paragraph(paragraph: str, limit: int) -> list[str]:
    """Split one over-limit paragraph into <=limit chunks along sentences/words."""
    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for sentence in _SENTENCE_END.split(paragraph):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) > limit:
            flush()
            # Sentence itself is too long: pack word by word.
            for word in sentence.split(" "):
                if len(word) > limit:
                    flush()
                    chunks.extend(_hard_split(word, limit))
                    continue
                candidate = f"{current} {word}".strip()
                if len(candidate) <= limit:
                    current = candidate
                else:
                    flush()
                    current = word
            flush()
            continue
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= limit:
            current = candidate
        else:
            flush()
            current = sentence
    flush()
    return chunks


def split_thread(text: str, limit: int = DEFAULT_LIMIT, cta: str = "") -> list[str]:
    """Split ``text`` into a list of posts, each <= ``limit`` characters.

    ``cta`` (optional) is appended as a final standalone post if it fits — handy
    for a closing "read more on my channel" reply.
    """
    text = (text or "").strip()
    if not text:
        return []

    # Normalize: unify newlines, collapse 3+ blank lines to a single blank line.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    posts: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            posts.append(current.strip())
        current = ""

    for para in paragraphs:
        if len(para) > limit:
            flush()
            posts.extend(_split_long_paragraph(para, limit))
            continue
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= limit:
            current = candidate
        else:
            flush()
            current = para
    flush()

    if cta:
        cta = cta.strip()
        if cta and len(cta) <= limit:
            posts.append(cta)

    return posts
