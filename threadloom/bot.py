"""The Threadloom bot: long-polls Telegram, previews threads, publishes to Threads.

Standard library only. Send the bot a post; it splits it into a thread and shows
a preview with buttons. Tap "Publish" and it posts the thread to Meta Threads.
"""
from __future__ import annotations

import html
import logging
import time

from . import threads_api
from .config import Config
from .i18n import t
from .splitter import split_thread
from .telegram_api import Telegram, TelegramError, button

log = logging.getLogger("threadloom")

# Preview message id -> {"posts": [...], "source": "..."}. In memory only; a
# restart forgets pending previews (the bot tells the user to resend).
_pending: dict[int, dict] = {}
_MAX_PREVIEW = 3600


def make_thread(cfg: Config, text: str) -> list[str]:
    """Split ``text`` into a thread, using the LLM if enabled, else the built-in
    splitter, and appending the optional CTA post."""
    posts = None
    if cfg.llm_enabled:
        try:
            from .llm import llm_split
            posts = llm_split(text, cfg)
        except Exception as e:  # noqa: BLE001 - any failure falls back gracefully
            log.warning("LLM split failed, using built-in splitter: %s", e)
            posts = None
    if posts is None:
        posts = split_thread(text)
    cta = cfg.cta.strip()
    if cta and len(cta) <= threads_api.MAX_LEN and (not posts or posts[-1] != cta):
        posts.append(cta)
    return posts


def render_preview(cfg: Config, posts: list[str]) -> str:
    """Human-readable preview of the thread, HTML-escaped for Telegram."""
    marks = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    sep = "\n\n———\n\n"
    blocks: list[str] = []
    used = 0
    for i, p in enumerate(posts):
        mark = marks[i] if i < len(marks) else f"[{i + 1}]"
        head = f"{mark} <i>({len(p)}/500)</i>\n"
        room = _MAX_PREVIEW - used - (len(sep) if blocks else 0) - len(head)
        if room <= 0:
            blocks.append("…")
            break
        text = html.escape(p)
        truncated = len(text) > room
        if truncated:
            # Trim the raw text, never the escaped form — a blind cut could
            # split an entity or leave an unclosed tag and break the message.
            raw = p[:room]
            while raw and len(html.escape(raw)) > room - 1:
                raw = raw[:-16] if len(raw) > 16 else raw[:-1]
            text = html.escape(raw) + "…"
        blocks.append(head + text)
        used += (len(sep) if len(blocks) > 1 else 0) + len(blocks[-1])
        if truncated:
            break
    body = sep.join(blocks)
    return t("bot_preview", cfg.lang, n=len(posts), body=body)


def preview_buttons(cfg: Config, key: int) -> list:
    return [
        [button(t("bot_btn_publish", cfg.lang), f"pub:{key}")],
        [button(t("bot_btn_recut", cfg.lang), f"recut:{key}"),
         button(t("bot_btn_cancel", cfg.lang), f"cancel:{key}")],
    ]


def _handle_message(tg: Telegram, cfg: Config, msg: dict) -> None:
    chat_id = msg["chat"]["id"]
    from_id = str(msg.get("from", {}).get("id", ""))
    text = (msg.get("text") or "").strip()

    if from_id != str(cfg.owner_id):
        tg.send_message(chat_id, t("bot_not_owner", cfg.lang, uid=from_id))
        return

    if text.startswith("/start"):
        tg.send_message(chat_id, t("bot_start", cfg.lang))
        return
    if text.startswith("/help"):
        tg.send_message(chat_id, t("bot_help", cfg.lang))
        return
    if not text:
        return

    thinking = tg.send_message(chat_id, t("bot_cutting", cfg.lang))
    key = thinking["message_id"]
    try:
        posts = make_thread(cfg, text)
        if not posts:
            raise ValueError("empty")
    except Exception as e:  # noqa: BLE001
        tg.edit_message_text(chat_id, key, t("bot_cut_failed", cfg.lang, err=html.escape(str(e))))
        return
    _pending[key] = {"posts": posts, "source": text}
    tg.edit_message_text(chat_id, key, render_preview(cfg, posts), preview_buttons(cfg, key))


def _handle_callback(tg: Telegram, cfg: Config, cq: dict) -> None:
    data = cq.get("data", "")
    msg = cq.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    message_id = msg.get("message_id")
    from_id = str(cq.get("from", {}).get("id", ""))
    tg.answer_callback_query(cq["id"])

    if from_id != str(cfg.owner_id):
        return
    action, _, key_s = data.partition(":")
    try:
        key = int(key_s)
    except ValueError:
        return

    entry = _pending.get(key)
    if entry is None:
        tg.edit_message_text(chat_id, message_id, t("bot_expired", cfg.lang))
        return

    if action == "cancel":
        _pending.pop(key, None)
        tg.edit_message_text(chat_id, message_id, t("bot_cancelled", cfg.lang))
        return

    if action == "recut":
        if entry.get("published"):
            return  # part of the thread is already live — re-splitting would desync it
        posts = make_thread(cfg, entry["source"])
        entry["posts"] = posts
        tg.edit_message_text(chat_id, message_id, render_preview(cfg, posts), preview_buttons(cfg, key))
        return

    if action == "pub":
        if not cfg.threads_ready:
            tg.edit_message_text(chat_id, message_id, t("bot_no_threads", cfg.lang))
            return
        tg.edit_message_text(chat_id, message_id, t("bot_publishing", cfg.lang))
        published = entry.setdefault("published", [])
        try:
            _ids, permalink = threads_api.publish_thread(
                entry["posts"], cfg.threads_user_id, cfg.threads_token, published)
        except Exception as e:  # noqa: BLE001
            if published:
                # Part of the thread is live; Publish resumes from the next post
                # instead of starting over (no Re-split — that would desync it).
                text = t("bot_publish_partial", cfg.lang, done=len(published),
                         n=len(entry["posts"]), err=html.escape(str(e)))
                buttons = [[button(t("bot_btn_publish", cfg.lang), f"pub:{key}")],
                           [button(t("bot_btn_cancel", cfg.lang), f"cancel:{key}")]]
            else:
                text = t("bot_publish_failed", cfg.lang, err=html.escape(str(e)))
                buttons = preview_buttons(cfg, key)
            tg.edit_message_text(chat_id, message_id, text, buttons)
            return
        _pending.pop(key, None)
        link = permalink or ""
        tg.edit_message_text(chat_id, message_id,
                             t("bot_published", cfg.lang, n=len(entry["posts"]), link=html.escape(link)))


def run() -> None:
    """Entry point: validate config and poll forever."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = Config()
    if not cfg.configured:
        raise SystemExit("Not configured yet. Run:  python run.py setup")

    tg = Telegram(cfg.telegram_token)
    me = tg.get_me()
    log.info("Threadloom online as @%s. Owner ID: %s. Threads: %s.",
             me.get("username"), cfg.owner_id, "on" if cfg.threads_ready else "off (publish disabled)")

    # Fast-forward past any backlog so we don't re-preview old messages.
    offset = None
    backlog = tg.get_updates(offset=-1, timeout=0)
    if backlog:
        offset = backlog[-1]["update_id"] + 1

    while True:
        try:
            updates = tg.get_updates(offset=offset, timeout=25)
        except TelegramError as e:
            log.warning("getUpdates failed, retrying: %s", e)
            time.sleep(3)
            continue
        for upd in updates:
            offset = upd["update_id"] + 1
            try:
                if "message" in upd and "text" in upd["message"]:
                    _handle_message(tg, cfg, upd["message"])
                elif "callback_query" in upd:
                    _handle_callback(tg, cfg, upd["callback_query"])
            except TelegramError as e:
                log.warning("handler telegram error: %s", e)
            except Exception:  # noqa: BLE001 - never let one bad update kill the loop
                log.exception("handler crashed on update %s", upd.get("update_id"))
