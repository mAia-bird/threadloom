"""Publish threads to Meta Threads via the Threads Graph API (stdlib only).

A thread is a root post plus a chain of replies (each ``reply_to_id`` points at
the previously published post), like a tweetstorm. Every post must be <= 500
characters, which is the Threads limit.

Per post the mechanic is the same: create a container -> wait until it's ready
-> publish it. Credentials come from the environment:
    THREADS_USER_ID, THREADS_ACCESS_TOKEN
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.threads.net/v1.0"
MAX_LEN = 500


class ThreadsError(RuntimeError):
    pass


def _call(method: str, url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode()
    full = url if method == "POST" else f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url if method == "POST" else full,
                                 data=data if method == "POST" else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ThreadsError(f"Threads API {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}")
    except urllib.error.URLError as e:
        raise ThreadsError(f"Threads API network error: {e.reason}")


def whoami(token: str) -> dict:
    """Return {id, username} for the account behind ``token``. Used to validate
    a pasted token and to auto-discover THREADS_USER_ID during setup."""
    res = _call("GET", f"{GRAPH}/me", {"fields": "id,username", "access_token": token})
    if "id" not in res:
        raise ThreadsError(res.get("error", {}).get("message", str(res)) if isinstance(res, dict) else str(res))
    return res


def _wait_container(container_id: str, token: str, attempts: int = 10) -> None:
    """TEXT containers are usually ready at once, but we check the status honestly."""
    for _ in range(attempts):
        res = _call("GET", f"{GRAPH}/{container_id}",
                    {"fields": "status,error_message", "access_token": token})
        status = res.get("status")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise ThreadsError(f"Threads rejected the post: {res.get('error_message')}")
        time.sleep(2)
    raise ThreadsError("Threads is taking too long to prepare the post — try again.")


def publish_thread(texts: list[str], user_id: str, token: str) -> tuple[list[str], str]:
    """Publish ``texts`` as a thread: root + chained replies.

    Returns (list of published post ids, permalink of the root post).
    """
    if not texts:
        raise ThreadsError("Empty thread — nothing to publish.")
    for i, txt in enumerate(texts, 1):
        if len(txt) > MAX_LEN:
            raise ThreadsError(f"Post {i} is longer than {MAX_LEN} chars ({len(txt)}) — re-split.")
    if not user_id or not token:
        raise ThreadsError("Threads is not connected (missing THREADS_USER_ID / THREADS_ACCESS_TOKEN).")

    ids: list[str] = []
    for i, text in enumerate(texts):
        params = {"media_type": "TEXT", "text": text, "access_token": token}
        if ids:
            params["reply_to_id"] = ids[-1]
        container = _call("POST", f"{GRAPH}/{user_id}/threads", params)
        if "id" not in container:
            raise ThreadsError(f"Post {i + 1}: container was not created — {container}")
        _wait_container(container["id"], token)
        pub = _call("POST", f"{GRAPH}/{user_id}/threads_publish",
                    {"creation_id": container["id"], "access_token": token})
        if "id" not in pub:
            raise ThreadsError(f"Post {i + 1}: publishing failed — {pub}")
        ids.append(pub["id"])
        time.sleep(2)  # let the reply see its parent before the next call

    root = _call("GET", f"{GRAPH}/{ids[0]}", {"fields": "permalink", "access_token": token})
    return ids, root.get("permalink", "")
