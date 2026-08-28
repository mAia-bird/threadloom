"""Interactive first-run setup — walks a brand-new user through every token.

Run automatically on first launch (or via ``python run.py setup``). It:
  1. picks a language,
  2. creates + validates a Telegram bot token,
  3. auto-captures the owner's Telegram ID by watching for their message,
  4. connects Meta Threads (validates the token, auto-discovers the user ID),
  5. optionally wires up a bring-your-own AI model,
and writes everything to a git-ignored ``.env``.
"""
from __future__ import annotations

import sys
import time

from . import threads_api
from .config import ENV_PATH, write_env
from .i18n import t
from .telegram_api import Telegram, TelegramError


def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        # stdin closed (e.g. piped input ran out) — abort cleanly instead of looping.
        raise KeyboardInterrupt


def _choose_language() -> str:
    while True:
        ans = _ask(t("wizard_choose_lang")).lower()
        if ans in ("1", "en", "english"):
            return "en"
        if ans in ("2", "ru", "russian", "русский", "рус"):
            return "ru"
        if ans == "":
            return "en"


def _setup_telegram(lang: str) -> tuple[Telegram, dict]:
    print(t("wizard_tg_steps", lang))
    while True:
        token = _ask(t("wizard_tg_prompt", lang))
        if not token:
            continue
        print(t("wizard_tg_checking", lang))
        tg = Telegram(token)
        try:
            me = tg.get_me()
        except TelegramError:
            print(t("wizard_tg_bad", lang))
            continue
        print(t("wizard_tg_ok", lang, username=me.get("username", "?"),
                name=me.get("first_name", "bot")))
        return tg, me


def _capture_owner_id(tg: Telegram, me: dict, lang: str) -> str:
    username = me.get("username", "your_bot")
    while True:
        print(t("wizard_id_steps", lang, username=username))
        # Skip any old updates so we only react to a fresh message.
        try:
            backlog = tg.get_updates(offset=-1, timeout=0)
        except TelegramError:
            backlog = []
        offset = (backlog[-1]["update_id"] + 1) if backlog else None

        deadline = time.time() + 120
        found = None
        while time.time() < deadline:
            left = int(deadline - time.time())
            print("  " + t("wizard_id_waiting", lang, username=username, left=left) + "        ",
                  end="\r", flush=True)
            try:
                updates = tg.get_updates(offset=offset, timeout=0)
            except TelegramError:
                time.sleep(2)
                continue
            for upd in updates:
                offset = upd["update_id"] + 1
                sender = upd.get("message", {}).get("from") or upd.get("callback_query", {}).get("from")
                if sender and not sender.get("is_bot"):
                    found = sender
                    break
            if found:
                break
            time.sleep(2)

        print(" " * 70, end="\r")  # clear the countdown line
        if found:
            name = found.get("first_name", "you")
            uid = str(found["id"])
            print(t("wizard_id_ok", lang, name=name, uid=uid))
            return uid

        manual = _ask(t("wizard_id_timeout", lang))
        if manual.isdigit():
            print(t("wizard_id_ok", lang, name="you", uid=manual))
            return manual
        # empty / non-numeric -> loop and wait again


def _setup_threads(lang: str) -> tuple[str, str]:
    print(t("wizard_th_steps", lang))
    while True:
        token = _ask(t("wizard_th_prompt", lang))
        if not token:
            print(t("wizard_th_skipped", lang))
            return "", ""
        print(t("wizard_th_checking", lang))
        try:
            who = threads_api.whoami(token)
        except threads_api.ThreadsError as e:
            print(t("wizard_th_bad", lang, err=str(e)))
            continue
        uid = str(who.get("id", ""))
        print(t("wizard_th_ok", lang, username=who.get("username", "?"), uid=uid))
        return uid, token


def _setup_llm(lang: str) -> dict:
    print(t("wizard_llm_steps", lang))
    if _ask(t("wizard_llm_enable", lang)).lower() not in ("y", "yes", "д", "да"):
        print(t("wizard_llm_off", lang))
        return {}
    provider = "anthropic" if _ask(t("wizard_llm_provider", lang)) == "2" else "openai"
    if provider == "anthropic":
        base = "https://api.anthropic.com"
    else:
        base = _ask(t("wizard_llm_base", lang)) or "https://api.openai.com/v1"
    key = _ask(t("wizard_llm_key", lang))
    model = _ask(t("wizard_llm_model", lang))
    print(t("wizard_llm_on", lang, model=model or "?"))
    return {
        "LLM_ENABLED": "true",
        "LLM_PROVIDER": provider,
        "LLM_API_BASE": base,
        "LLM_API_KEY": key,
        "LLM_MODEL": model,
    }


def run() -> None:
    print(t("wizard_banner"))
    lang = _choose_language()
    print(t("wizard_intro", lang))

    tg, me = _setup_telegram(lang)
    owner_id = _capture_owner_id(tg, me, lang)
    threads_user_id, threads_token = _setup_threads(lang)
    llm_values = _setup_llm(lang)

    values = {
        "LANG_UI": lang,
        "TELEGRAM_TOKEN": tg.token,
        "OWNER_ID": owner_id,
        "THREADS_USER_ID": threads_user_id,
        "THREADS_ACCESS_TOKEN": threads_token,
        **llm_values,
    }
    write_env(values)
    print(t("wizard_done", lang, path=str(ENV_PATH)))


def main() -> None:
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n(cancelled — re-run any time with:  python run.py setup)")
        sys.exit(1)
