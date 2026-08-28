"""Bilingual strings (English / Russian) for the wizard and the bot.

Every user-facing string lives here so the whole tool speaks one language,
chosen once during setup and stored as ``LANG`` in ``.env``.

Usage:
    from .i18n import t
    print(t("wizard_done", lang, path="/path/to/.env"))
"""

LANGS = ("en", "ru")

# ---------------------------------------------------------------------------
# Strings. Each key maps to {"en": ..., "ru": ...}. Use {placeholders} with
# ``t(key, lang, name=value)``.
# ---------------------------------------------------------------------------
S = {
    # ----- wizard: framing -------------------------------------------------
    "wizard_banner": {
        "en": "🧵  Threadloom — first-time setup\n"
              "Turn a Telegram message into a published thread on Meta Threads.",
        "ru": "🧵  Threadloom — первичная настройка\n"
              "Превращаем сообщение в Telegram в опубликованный тред в Meta Threads.",
    },
    "wizard_choose_lang": {
        "en": "Choose a language / Выберите язык:\n"
              "  [1] English\n"
              "  [2] Русский\n"
              "> ",
        "ru": "Choose a language / Выберите язык:\n"
              "  [1] English\n"
              "  [2] Русский\n"
              "> ",
    },
    "wizard_intro": {
        "en": "\nThis wizard walks you through everything, step by step:\n"
              "  1. Create a Telegram bot and grab its token\n"
              "  2. Let the bot learn your Telegram ID (so only you can use it)\n"
              "  3. Connect Meta Threads (the part that actually publishes)\n"
              "  4. (Optional) plug in your own AI model for smarter thread-splitting\n"
              "\nYou can press Ctrl+C at any time and re-run it later. Nothing is\n"
              "sent anywhere until you finish. Ready? Let's go.\n",
        "ru": "\nЭтот мастер проведёт тебя через всё по шагам:\n"
              "  1. Создать Telegram-бота и получить его токен\n"
              "  2. Дать боту узнать твой Telegram ID (чтобы им пользовалась только ты)\n"
              "  3. Подключить Meta Threads (то, что и публикует треды)\n"
              "  4. (По желанию) подключить свою нейросеть для умной нарезки на тред\n"
              "\nВ любой момент можно нажать Ctrl+C и вернуться позже. Никуда ничего\n"
              "не уходит, пока ты не закончишь. Готова? Поехали.\n",
    },

    # ----- wizard: Telegram bot token -------------------------------------
    "wizard_tg_steps": {
        "en": "\n── Step 1 of 3 · Telegram bot ─────────────────────────────\n"
              "In the Telegram app:\n"
              "  1. Open a chat with @BotFather (it has a blue verified check).\n"
              "  2. Send the command:  /newbot\n"
              "  3. Give it a display name (e.g. \"My Threadloom\").\n"
              "  4. Give it a username that ends in \"bot\" (e.g. my_threadloom_bot).\n"
              "  5. BotFather replies with a token that looks like:\n"
              "        123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
              "  6. Copy that token and paste it here.\n",
        "ru": "\n── Шаг 1 из 3 · Telegram-бот ──────────────────────────────\n"
              "В приложении Telegram:\n"
              "  1. Открой чат с @BotFather (у него синяя галочка).\n"
              "  2. Отправь команду:  /newbot\n"
              "  3. Задай отображаемое имя (например, «My Threadloom»).\n"
              "  4. Задай username, который заканчивается на «bot» (например, my_threadloom_bot).\n"
              "  5. BotFather пришлёт токен вида:\n"
              "        123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
              "  6. Скопируй этот токен и вставь сюда.\n",
    },
    "wizard_tg_prompt": {
        "en": "Paste your bot token: ",
        "ru": "Вставь токен бота: ",
    },
    "wizard_tg_checking": {
        "en": "Checking the token with Telegram…",
        "ru": "Проверяю токен через Telegram…",
    },
    "wizard_tg_bad": {
        "en": "✗ Telegram rejected that token. Check you copied all of it and try again.\n",
        "ru": "✗ Telegram не принял токен. Проверь, что скопировала его целиком, и попробуй снова.\n",
    },
    "wizard_tg_ok": {
        "en": "✓ Connected to bot @{username} ({name}).\n",
        "ru": "✓ Подключились к боту @{username} ({name}).\n",
    },

    # ----- wizard: capture owner id ---------------------------------------
    "wizard_id_steps": {
        "en": "\nNow the bot needs to know it's you. Open Telegram, find your bot\n"
              "@{username}, press Start (or just send it any message like \"hi\").\n"
              "I'll wait and pick up your ID automatically.\n",
        "ru": "\nТеперь боту нужно понять, что это ты. Открой Telegram, найди своего бота\n"
              "@{username}, нажми «Начать» (или просто напиши ему что угодно, например «привет»).\n"
              "Я подожду и подхвачу твой ID сам.\n",
    },
    "wizard_id_waiting": {
        "en": "Waiting for your message to @{username}… ({left}s)",
        "ru": "Жду твоё сообщение боту @{username}… (осталось {left}с)",
    },
    "wizard_id_ok": {
        "en": "✓ Got it — you are {name} (ID {uid}). Only this account can drive the bot.\n",
        "ru": "✓ Поймал — это ты, {name} (ID {uid}). Управлять ботом сможет только этот аккаунт.\n",
    },
    "wizard_id_timeout": {
        "en": "Didn't see a message in time. You can paste your numeric Telegram ID\n"
              "manually (get it from @userinfobot), or press Enter to try waiting again.\n"
              "Your Telegram ID (or Enter to retry): ",
        "ru": "Не увидел сообщение вовремя. Можешь вставить свой числовой Telegram ID\n"
              "вручную (узнать у @userinfobot) или нажать Enter, чтобы подождать ещё раз.\n"
              "Твой Telegram ID (или Enter, чтобы повторить): ",
    },

    # ----- wizard: Threads -------------------------------------------------
    "wizard_th_steps": {
        "en": "\n── Step 2 of 3 · Meta Threads ─────────────────────────────\n"
              "This is the fiddly part (Meta's fault, not yours). One-time setup:\n"
              "  1. Make sure you have a Threads account (threads.net).\n"
              "  2. Go to  https://developers.facebook.com/  and log in.\n"
              "  3. Click \"Create App\". When asked what you're building, pick the\n"
              "     use case  \"Access the Threads API\"  and finish creating the app.\n"
              "  4. In the app, open the Threads use case and add these permissions:\n"
              "        threads_basic , threads_content_publish\n"
              "  5. Add yourself as a Threads tester and accept the invite inside the\n"
              "     Threads app (Settings → Account → Website permissions).\n"
              "  6. Generate a user access token for your account and copy it.\n"
              "     (Full walkthrough with screenshots is linked in the README.)\n"
              "\nYou only need to paste the ACCESS TOKEN — I'll fetch your user ID for you.\n",
        "ru": "\n── Шаг 2 из 3 · Meta Threads ──────────────────────────────\n"
              "Это самая муторная часть (вина Meta, не твоя). Настраивается один раз:\n"
              "  1. Убедись, что у тебя есть аккаунт Threads (threads.net).\n"
              "  2. Зайди на  https://developers.facebook.com/  и залогинься.\n"
              "  3. Нажми «Create App». На вопрос, что ты создаёшь, выбери сценарий\n"
              "     use case  «Access the Threads API»  и доведи создание до конца.\n"
              "  4. В приложении открой use case Threads и добавь права:\n"
              "        threads_basic , threads_content_publish\n"
              "  5. Добавь себя как Threads-тестировщика и прими приглашение внутри\n"
              "     приложения Threads (Настройки → Аккаунт → Разрешения для сайтов).\n"
              "  6. Сгенерируй user access token для своего аккаунта и скопируй его.\n"
              "     (Полная инструкция со скриншотами — в README.)\n"
              "\nВставить нужно только ACCESS TOKEN — твой user ID я подтяну сам.\n",
    },
    "wizard_th_prompt": {
        "en": "Paste your Threads access token (or press Enter to skip for now): ",
        "ru": "Вставь Threads access token (или нажми Enter, чтобы пока пропустить): ",
    },
    "wizard_th_checking": {
        "en": "Checking the token with Meta…",
        "ru": "Проверяю токен через Meta…",
    },
    "wizard_th_bad": {
        "en": "✗ Meta rejected that token: {err}\n  Try again, or press Enter to skip.\n",
        "ru": "✗ Meta не принял токен: {err}\n  Попробуй снова или нажми Enter, чтобы пропустить.\n",
    },
    "wizard_th_ok": {
        "en": "✓ Threads connected as @{username} (user ID {uid}).\n",
        "ru": "✓ Threads подключён как @{username} (user ID {uid}).\n",
    },
    "wizard_th_skipped": {
        "en": "○ Skipped Threads for now. The bot will run, but publishing stays off\n"
              "  until you add THREADS_ACCESS_TOKEN to .env (re-run setup any time).\n",
        "ru": "○ Threads пока пропущен. Бот запустится, но публикация будет выключена,\n"
              "  пока не добавишь THREADS_ACCESS_TOKEN в .env (мастер можно перезапустить).\n",
    },

    # ----- wizard: optional LLM -------------------------------------------
    "wizard_llm_steps": {
        "en": "\n── Step 3 of 3 · Smart splitting (optional) ───────────────\n"
              "By default Threadloom splits your post into a thread on its own — no\n"
              "keys, no accounts, works out of the box.\n"
              "If you'd rather have an AI model do the splitting (nicer breaks, better\n"
              "hooks), you can plug in your own. It works with any OpenAI-compatible\n"
              "endpoint (OpenAI, OpenRouter, a local Ollama/LM Studio server, …) or\n"
              "Anthropic. You can always skip and turn it on later in .env.\n",
        "ru": "\n── Шаг 3 из 3 · Умная нарезка (по желанию) ────────────────\n"
              "По умолчанию Threadloom сам режет пост на тред — без ключей, без\n"
              "аккаунтов, работает из коробки.\n"
              "Если хочешь, чтобы нарезкой занималась нейросеть (аккуратнее переходы,\n"
              "цепляющее начало) — можно подключить свою. Подходит любой\n"
              "OpenAI-совместимый эндпоинт (OpenAI, OpenRouter, локальный Ollama/LM\n"
              "Studio…) или Anthropic. Можно пропустить и включить позже в .env.\n",
    },
    "wizard_llm_enable": {
        "en": "Plug in an AI model now? [y/N]: ",
        "ru": "Подключить нейросеть сейчас? [y/N]: ",
    },
    "wizard_llm_provider": {
        "en": "Provider — [1] OpenAI-compatible  [2] Anthropic  (default 1): ",
        "ru": "Провайдер — [1] OpenAI-совместимый  [2] Anthropic  (по умолчанию 1): ",
    },
    "wizard_llm_base": {
        "en": "API base URL (e.g. https://api.openai.com/v1 , or http://localhost:11434/v1 for Ollama): ",
        "ru": "Base URL API (например https://api.openai.com/v1 или http://localhost:11434/v1 для Ollama): ",
    },
    "wizard_llm_key": {
        "en": "API key (leave empty for a local server that needs none): ",
        "ru": "API-ключ (оставь пустым для локального сервера без ключа): ",
    },
    "wizard_llm_model": {
        "en": "Model name (e.g. gpt-4o-mini , llama3.1 , claude-haiku-4-5): ",
        "ru": "Название модели (например gpt-4o-mini, llama3.1, claude-haiku-4-5): ",
    },
    "wizard_llm_on": {
        "en": "✓ AI splitting enabled ({model}). If it ever fails, the built-in splitter takes over.\n",
        "ru": "✓ Умная нарезка включена ({model}). Если она сорвётся — подхватит встроенная.\n",
    },
    "wizard_llm_off": {
        "en": "○ Using the built-in splitter. Simple and reliable.\n",
        "ru": "○ Используем встроенную нарезку. Просто и надёжно.\n",
    },

    # ----- wizard: finish --------------------------------------------------
    "wizard_done": {
        "en": "\n✓ All set. Your settings are saved to:\n    {path}\n"
              "  (this file holds your secrets — it is git-ignored, never commit it)\n"
              "\nStart the bot with:\n    python run.py\n"
              "Then open Telegram, send your bot a post, and tap “Publish to Threads”.\n",
        "ru": "\n✓ Готово. Настройки сохранены в:\n    {path}\n"
              "  (в этом файле твои секреты — он в .gitignore, никогда не коммить его)\n"
              "\nЗапусти бота командой:\n    python run.py\n"
              "Потом открой Telegram, пришли боту пост и нажми «Опубликовать в Threads».\n",
    },

    # ----- bot -------------------------------------------------------------
    "bot_start": {
        "en": "🧵 <b>Threadloom</b> is ready.\n\n"
              "Send me any post and I'll split it into a Threads thread and show you a "
              "preview. Tap a button to publish it to Meta Threads.\n\n"
              "Commands: /help",
        "ru": "🧵 <b>Threadloom</b> на связи.\n\n"
              "Пришли мне любой пост — я нарежу его на тред для Threads и покажу превью. "
              "Нажми кнопку, чтобы опубликовать в Meta Threads.\n\n"
              "Команды: /help",
    },
    "bot_help": {
        "en": "Send a post as a normal message. I split it into pieces of up to 500 "
              "characters (a root post + replies) and show a preview with buttons:\n\n"
              "📤  Publish to Threads\n"
              "✂️  Re-split\n"
              "✖️  Cancel\n\n"
              "That's it. Long posts become a tidy thread automatically.",
        "ru": "Пришли пост обычным сообщением. Я нарежу его на куски до 500 знаков "
              "(корневой пост + реплаи) и покажу превью с кнопками:\n\n"
              "📤  Опубликовать в Threads\n"
              "✂️  Перенарезать\n"
              "✖️  Отмена\n\n"
              "Вот и всё. Длинные посты сами превращаются в аккуратный тред.",
    },
    "bot_not_owner": {
        "en": "This is a private Threadloom bot. Your ID {uid} isn't its owner, so it "
              "won't publish for you.",
        "ru": "Это личный бот Threadloom. Твой ID {uid} — не его владелец, публиковать он "
              "для тебя не будет.",
    },
    "bot_cutting": {
        "en": "✂️ Splitting into a thread…",
        "ru": "✂️ Режу на тред…",
    },
    "bot_preview": {
        "en": "🧵 <b>Thread preview</b> — {n} post(s):\n\n{body}",
        "ru": "🧵 <b>Превью треда</b> — постов: {n}\n\n{body}",
    },
    "bot_cut_failed": {
        "en": "❌ Couldn't split that: {err}",
        "ru": "❌ Не получилось нарезать: {err}",
    },
    "bot_btn_publish": {"en": "📤 Publish to Threads", "ru": "📤 Опубликовать в Threads"},
    "bot_btn_recut": {"en": "✂️ Re-split", "ru": "✂️ Перенарезать"},
    "bot_btn_cancel": {"en": "✖️ Cancel", "ru": "✖️ Отмена"},
    "bot_publishing": {
        "en": "📤 Publishing to Threads…",
        "ru": "📤 Публикую в Threads…",
    },
    "bot_published": {
        "en": "✅ Published! {n} post(s) live.\n{link}",
        "ru": "✅ Опубликовано! Постов в треде: {n}.\n{link}",
    },
    "bot_publish_failed": {
        "en": "❌ Publishing failed: {err}",
        "ru": "❌ Публикация не удалась: {err}",
    },
    "bot_no_threads": {
        "en": "⚠️ Threads isn't connected yet. Add THREADS_ACCESS_TOKEN to .env "
              "(or re-run: python run.py setup).",
        "ru": "⚠️ Threads ещё не подключён. Добавь THREADS_ACCESS_TOKEN в .env "
              "(или перезапусти: python run.py setup).",
    },
    "bot_cancelled": {
        "en": "Cancelled. Nothing was published.",
        "ru": "Отменено. Ничего не опубликовано.",
    },
    "bot_expired": {
        "en": "This preview expired (the bot restarted). Send the post again.",
        "ru": "Это превью устарело (бот перезапускался). Пришли пост ещё раз.",
    },
}


def t(key: str, lang: str = "en", **kw) -> str:
    """Return the localized string for ``key`` in ``lang`` with placeholders filled.

    Falls back to English if the language or key is missing, and leaves the raw
    template untouched if a placeholder is absent (never raises on formatting).
    """
    entry = S.get(key, {})
    text = entry.get(lang) or entry.get("en") or key
    if kw:
        try:
            text = text.format(**kw)
        except (KeyError, IndexError, ValueError):
            pass
    return text
