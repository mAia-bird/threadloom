<h1 align="center">🧵 Threadloom</h1>

<p align="center">
  <b>Write a post in Telegram. Publish it as a thread on Meta Threads — one tap.</b>
</p>

<p align="center">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue">
  <img alt="Dependencies: none" src="https://img.shields.io/badge/dependencies-none-brightgreen">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-black">
</p>

<p align="center"><a href="README.ru.md">🇷🇺 Русская версия</a></p>

---

Threadloom is a tiny personal Telegram bot. You send it a post; it splits the text
into a proper thread (a root post plus replies, each within the 500-character
Threads limit), shows you a preview, and — when you tap **Publish** — posts the
whole thread to [Meta Threads](https://www.threads.net).

```
You in Telegram  ──▶  🧵 Threadloom bot  ──▶  preview + buttons  ──▶  Meta Threads
   "long post"          splits into a thread      📤 Publish            thread is live
```

It has **no dependencies at all** — only the Python standard library — and a
friendly setup wizard that walks you through every token step by step. It runs on
your own computer; your tokens never leave your machine.

## Why you might like it

- ✍️ **Draft in Telegram, publish to Threads.** Telegram is a comfortable place to
  write; Threads is where the thread goes.
- ✂️ **Automatic thread-splitting.** Long posts become a tidy thread that respects
  paragraphs and sentences. No manual chopping at 500 characters.
- 📷 **Photos too.** Send a photo (with or without a caption) and it becomes the
  first post of the thread. See [how photos travel](#how-photos-travel) below.
- 🔒 **Private by design.** Only *your* Telegram account can drive the bot.
- 🧰 **Zero setup pain.** `python run.py` launches an interactive wizard that
  creates the bot, learns your ID automatically, and validates every token.
- 🤖 **Bring your own AI (optional).** Want smarter splits? Plug in any
  OpenAI-compatible endpoint (OpenAI, OpenRouter, a local Ollama/LM Studio server)
  or Anthropic. Off by default — the built-in splitter needs no keys.

## Requirements

- Python **3.9 or newer**. That's it. No `pip install`, no virtual environment
  needed.
- A Telegram account and a [Threads](https://www.threads.net) account.

## Quick start

```bash
git clone https://github.com/mAia-bird/threadloom.git
cd threadloom
python run.py
```

The first run launches the setup wizard. Follow it, then start the bot with
`python run.py` again. Open Telegram, send your bot a post, and tap
**📤 Publish to Threads**.

## The setup wizard, step by step

Running `python run.py` the first time (or `python run.py setup` any time) starts
an interactive guide. Here is exactly what it asks for and how to get it.

### 1. A Telegram bot token

The wizard tells you to:

1. Open Telegram and start a chat with **[@BotFather](https://t.me/BotFather)**
   (it has a blue verified check).
2. Send `/newbot`.
3. Give the bot a **display name** (e.g. *My Threadloom*).
4. Give it a **username** ending in `bot` (e.g. `my_threadloom_bot`).
5. BotFather replies with a **token** like `123456789:AAExxxxx…`.
6. Paste the token into the wizard. It checks the token with Telegram and confirms
   your bot's name.

### 2. Your Telegram ID (captured automatically)

So that *only you* can use the bot, Threadloom needs your numeric Telegram ID.
You don't have to look it up — the wizard says *"go message your bot"*, you send it
any message (e.g. "hi"), and it picks up your ID for you. (If you'd rather, you can
also paste it manually; [@userinfobot](https://t.me/userinfobot) tells you your ID.)

### 3. Meta Threads access (the fiddly one)

This is a one-time setup on Meta's developer site. The wizard summarizes it; here
it is in full:

1. Make sure you have a **Threads account** ([threads.net](https://www.threads.net)).
2. Go to **[developers.facebook.com](https://developers.facebook.com/)** and log in.
3. Click **Create App**. When asked what you're building, choose the use case
   **"Access the Threads API"**, and finish creating the app.
4. Open the **Threads** use case in your app and add these permissions:
   - `threads_basic`
   - `threads_content_publish`
5. Add yourself as a **Threads tester**, then accept the invite inside the Threads
   app (**Settings → Account → Website permissions**).
6. Generate a **user access token** for your account and copy it.
7. Paste the token into the wizard. It calls the Threads API to validate the token
   and **auto-discovers your Threads user ID** — so you only ever paste the token.

> 📎 Meta's official guide, with screenshots:
> <https://developers.facebook.com/docs/threads/get-started>

You can skip this step for now (just press Enter) and add it later — the bot still
runs, it just won't publish until Threads is connected.

> ⏳ **Tokens expire.** Threads access tokens are valid for about 60 days. When
> yours expires, generate a fresh one and re-run `python run.py setup` (or update
> `THREADS_ACCESS_TOKEN` in `.env`). See
> [long-lived tokens](https://developers.facebook.com/docs/threads/get-started/long-lived-tokens).

### 4. Smart splitting with your own AI (optional)

By default Threadloom splits posts itself — no keys, works offline. If you'd like
an AI model to do the splitting (nicer breaks, stronger opening line), the wizard
lets you plug one in:

- **OpenAI-compatible** — works with OpenAI, OpenRouter, Together, or a **local**
  server like [Ollama](https://ollama.com) (`http://localhost:11434/v1`) or LM Studio.
- **Anthropic** — Claude models.

If the model ever fails or returns something odd, Threadloom quietly falls back to
the built-in splitter, so publishing never breaks.

## Using the bot

Start it:

```bash
python run.py
```

Then, in Telegram:

- **Send any post** as a normal message → the bot replies with a thread preview and
  buttons.
- **Send a photo** (optionally with a caption) → the photo becomes the first post;
  a long caption continues as text replies.
- **📤 Publish to Threads** — posts the thread; you get back a link to the live thread.
- **✂️ Re-split** — splits the same post again (handy after you toggle an AI model).
- **✖️ Cancel** — throws the preview away.

Commands: `/start`, `/help`.

### How photos travel

The Threads API can't accept an image file directly — it only takes a **public
URL** that Meta's servers fetch. Handing Meta the Telegram file URL would be a
security hole (that URL contains your bot token), so Threadloom does this instead:

1. downloads the photo from Telegram locally,
2. uploads it anonymously to **[Litterbox](https://litterbox.catbox.moe)**
   (catbox.moe's temporary host — no account, no API key),
3. gives that temporary URL to Threads; Meta copies the image to its own CDN
   within seconds,
4. the Litterbox copy **self-destructs after 1 hour**.

So the photo is only ever public in two places: briefly on Litterbox, and then in
your published Threads post — where you were publishing it anyway. Your bot token
never leaves your machine. If you'd rather not route photos through a third-party
host at all, simply don't send photos — text posts never touch it.

### Keeping it running

`python run.py` runs in the foreground. To keep it alive after you close the
terminal, the simplest option:

```bash
nohup python run.py > threadloom.log 2>&1 &
```

On macOS you can use a `launchd` agent; on Linux, a `systemd --user` service. Any
process manager works — it's just a normal Python program.

## Configuration reference

Everything the wizard writes lives in `.env` (git-ignored). You can edit it by
hand; see [`.env.example`](.env.example) for the annotated template.

| Variable | What it is |
| --- | --- |
| `LANG_UI` | Interface language: `en` or `ru`. |
| `TELEGRAM_TOKEN` | Bot token from @BotFather. |
| `OWNER_ID` | Your numeric Telegram ID — the only account allowed to use the bot. |
| `THREADS_ACCESS_TOKEN` | Your Meta Threads access token. |
| `THREADS_USER_ID` | Your Threads user ID (auto-filled from the token). |
| `THREADS_CTA` | Optional closing post appended to every thread (≤ 500 chars), e.g. a link to your channel. |
| `LLM_ENABLED` | `true` to split with an AI model, else the built-in splitter. |
| `LLM_PROVIDER` | `openai` (any OpenAI-compatible endpoint) or `anthropic`. |
| `LLM_API_BASE` | API base URL, e.g. `https://api.openai.com/v1` or `http://localhost:11434/v1`. |
| `LLM_API_KEY` | API key (leave empty for a local server that needs none). |
| `LLM_MODEL` | Model name, e.g. `gpt-4o-mini`, `llama3.1`, `claude-haiku-4-5`. |

## Troubleshooting

- **"Telegram rejected that token."** You didn't copy the whole token, or there's a
  stray space. Copy it again from BotFather.
- **The wizard didn't catch my ID.** Make sure you messaged the *right* bot
  (`@your_bot`), then let it wait, or paste your ID from
  [@userinfobot](https://t.me/userinfobot).
- **Publishing fails with a Threads API error.** Usually the token expired (~60
  days) or the `threads_content_publish` permission is missing. Regenerate the
  token and re-run `python run.py setup`.
- **A post won't fit.** Each Threads post is capped at 500 characters. Threadloom
  splits automatically; if a single unbroken word (like a huge URL) is longer than
  500 chars, it's chopped as a last resort.

## How it works

Small and readable — four moving parts, all standard library:

| File | Role |
| --- | --- |
| `threadloom/telegram_api.py` | Minimal Telegram Bot API client (long polling). |
| `threadloom/threads_api.py` | Publishes a thread via the Threads Graph API. |
| `threadloom/splitter.py` | The built-in thread splitter (paragraphs → sentences → words). |
| `threadloom/imagehost.py` | Anonymous 1-hour photo hosting (Litterbox) for image posts. |
| `threadloom/llm.py` | Optional AI splitter (OpenAI-compatible / Anthropic). |
| `threadloom/bot.py` | Ties it together: preview, buttons, publish. |
| `threadloom/setup_wizard.py` | The interactive first-run setup. |

## Contributing

Issues and pull requests are welcome — especially translations (the UI strings all
live in `threadloom/i18n.py`) and improvements to the splitter.

## License

[MIT](LICENSE) © 2026 Maya ([@mayamastra](https://github.com/mayamastra))
