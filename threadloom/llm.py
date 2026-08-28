"""Optional AI-powered splitter — bring your own model.

Off by default. When enabled in ``.env`` it asks an LLM to split the post into
a thread. It speaks two dialects with the standard library only:

  * OpenAI-compatible ``/chat/completions`` — works with OpenAI, OpenRouter,
    Together, a local Ollama or LM Studio server ("your own model"), etc.
  * Anthropic ``/v1/messages``.

If anything goes wrong (no key, bad JSON, an over-limit post), the caller falls
back to the built-in splitter, so publishing never breaks because of the AI.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request

from .splitter import DEFAULT_LIMIT

_SYSTEM = (
    "You split a social-media post into a thread. Keep the author's wording, tone "
    "and language exactly — do not rewrite, translate, summarize or add hashtags. "
    "Break it into a sequence where the first post hooks the reader and the rest "
    "continue naturally. Every post MUST be at most {limit} characters. Do not "
    "number the posts. Return ONLY a JSON array of strings and nothing else."
)


def _post(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={**headers, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"LLM HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"LLM network error: {e.reason}")


def _extract_array(content: str) -> list[str]:
    """Pull a JSON array of strings out of a model response, tolerating stray prose."""
    content = content.strip()
    # Strip a ```json ... ``` fence if present.
    fence = re.search(r"```(?:json)?\s*(.+?)```", content, re.S)
    if fence:
        content = fence.group(1).strip()
    start, end = content.find("["), content.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("model did not return a JSON array")
    posts = json.loads(content[start:end + 1])
    posts = [str(p).strip() for p in posts if str(p).strip()]
    if not posts:
        raise RuntimeError("model returned an empty thread")
    return posts


def llm_split(text: str, cfg, limit: int = DEFAULT_LIMIT) -> list[str]:
    """Split ``text`` via the configured model. Raises on any problem."""
    if not cfg.llm_model:
        raise RuntimeError("no LLM_MODEL configured")
    system = _SYSTEM.format(limit=limit)
    base = cfg.llm_base.rstrip("/")

    if cfg.llm_provider == "anthropic":
        if base.endswith("/messages"):
            url = base
        elif base.endswith("/v1"):
            url = f"{base}/messages"
        else:
            url = f"{base}/v1/messages"
        headers = {"x-api-key": cfg.llm_key, "anthropic-version": "2023-06-01"}
        body = {"model": cfg.llm_model, "max_tokens": 4096, "system": system,
                "messages": [{"role": "user", "content": text}]}
        res = _post(url, headers, body)
        content = "".join(b.get("text", "") for b in res.get("content", []) if b.get("type") == "text")
    else:  # openai-compatible
        url = f"{base}/chat/completions"
        headers = {"Authorization": f"Bearer {cfg.llm_key}"} if cfg.llm_key else {}
        body = {"model": cfg.llm_model, "temperature": 0.3,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": text}]}
        res = _post(url, headers, body)
        content = res["choices"][0]["message"]["content"]

    posts = _extract_array(content)
    over = [i + 1 for i, p in enumerate(posts) if len(p) > limit]
    if over:
        raise RuntimeError(f"model returned over-limit post(s): {over}")
    return posts
