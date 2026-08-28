"""A minimal Telegram Bot API client built on the standard library only.

Just the handful of methods Threadloom needs: identify the bot, long-poll for
updates, send/edit messages, and answer button taps.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class TelegramError(RuntimeError):
    pass


class Telegram:
    def __init__(self, token: str) -> None:
        self.token = token
        self.base = f"https://api.telegram.org/bot{token}"

    def _call(self, method: str, params: dict | None = None, timeout: int = 35) -> dict:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        data = urllib.parse.urlencode(params).encode()
        url = f"{self.base}/{method}"
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                payload = json.loads(r.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            raise TelegramError(f"{method} → HTTP {e.code}: {body[:200]}")
        except urllib.error.URLError as e:
            raise TelegramError(f"{method} → network error: {e.reason}")
        if not payload.get("ok"):
            raise TelegramError(f"{method} → {payload.get('description', 'unknown error')}")
        return payload.get("result")

    # --- methods -----------------------------------------------------------
    def get_me(self) -> dict:
        return self._call("getMe", timeout=15)

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list:
        return self._call(
            "getUpdates",
            {"offset": offset, "timeout": timeout, "allowed_updates": json.dumps(["message", "callback_query"])},
            timeout=timeout + 10,
        )

    def send_message(self, chat_id, text: str, buttons: list | None = None,
                     parse_mode: str = "HTML") -> dict:
        params = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode,
                  "disable_web_page_preview": "true"}
        if buttons is not None:
            params["reply_markup"] = json.dumps({"inline_keyboard": buttons})
        return self._call("sendMessage", params)

    def edit_message_text(self, chat_id, message_id, text: str, buttons: list | None = None,
                          parse_mode: str = "HTML") -> dict:
        params = {"chat_id": chat_id, "message_id": message_id, "text": text,
                  "parse_mode": parse_mode, "disable_web_page_preview": "true"}
        # Passing an empty keyboard removes the buttons.
        params["reply_markup"] = json.dumps({"inline_keyboard": buttons or []})
        return self._call("editMessageText", params)

    def answer_callback_query(self, callback_id, text: str | None = None) -> None:
        self._call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text}, timeout=15)

    def get_file(self, file_id: str) -> dict:
        return self._call("getFile", {"file_id": file_id}, timeout=15)

    def download_file(self, file_path: str) -> bytes:
        """Download a file previously located with ``get_file``. The URL embeds
        the bot token, so the bytes are fetched here and never shared as a link."""
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            raise TelegramError(f"file download → HTTP {e.code}")
        except urllib.error.URLError as e:
            raise TelegramError(f"file download → network error: {e.reason}")


def button(text: str, callback_data: str) -> dict:
    return {"text": text, "callback_data": callback_data}
