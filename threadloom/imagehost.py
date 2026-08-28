"""Anonymous, temporary image hosting for photo posts (stdlib only).

The Threads API accepts only a public ``image_url`` — it cannot take file
bytes — so a photo from Telegram must briefly live at a URL that Meta's
servers can fetch. Handing Meta the Telegram file URL is not an option: that
URL embeds the bot token.

We use Litterbox (litterbox.catbox.moe): anonymous, no account or API key,
and every upload self-destructs after one hour. Meta copies the image to its
own CDN within seconds of publishing, so the temporary copy is only ever
needed for a moment.
"""
from __future__ import annotations

import secrets
import urllib.error
import urllib.request

API = "https://litterbox.catbox.moe/resources/internals/api.php"
EXPIRY = "1h"  # shortest Litterbox offers; Meta fetches the image immediately


class ImageHostError(RuntimeError):
    pass


def upload_temporary(data: bytes, filename: str = "photo.jpg") -> str:
    """Upload ``data`` anonymously; return a public URL that expires in 1 hour."""
    boundary = "----threadloom" + secrets.token_hex(16)

    def field(name: str, value: str) -> bytes:
        return (f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                f"{value}\r\n").encode()

    body = field("reqtype", "fileupload") + field("time", EXPIRY)
    body += (f"--{boundary}\r\n"
             f'Content-Disposition: form-data; name="fileToUpload"; filename="{filename}"\r\n'
             f"Content-Type: application/octet-stream\r\n\r\n").encode()
    body += data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "Threadloom/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            url = r.read().decode("utf-8", "ignore").strip()
    except urllib.error.HTTPError as e:
        raise ImageHostError(f"image host HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}")
    except urllib.error.URLError as e:
        raise ImageHostError(f"image host network error: {e.reason}")
    if not url.startswith("https://"):
        raise ImageHostError(f"image host refused the upload: {url[:200]}")
    return url
