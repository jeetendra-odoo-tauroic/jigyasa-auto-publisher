
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent
TIMEZONE = ZoneInfo("Asia/Kolkata")

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
API_VERSION = os.environ.get(
    "FACEBOOK_GRAPH_API_VERSION", "v23.0"
).strip()
SLOT = os.environ.get("POST_SLOT", "").strip()

VALID_SLOTS = {"07:00", "10:00", "13:30", "16:10", "20:30"}


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    if not PAGE_ID or not ACCESS_TOKEN:
        fail("Add FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN to GitHub Secrets.")

    if SLOT not in VALID_SLOTS:
        fail(f"Invalid posting slot: {SLOT!r}")

    today = datetime.now(TIMEZONE).date().isoformat()
    slot_file = SLOT.replace(":", "-")

    # Example: content/2026-10-22/07-00.json
    post_file = ROOT / "content" / today / f"{slot_file}.json"

    if not post_file.is_file():
        fail(
            f"No prepared post found for {today}, {SLOT}. "
            "Create the dated JSON file and its image before publishing."
        )

    try:
        post = json.loads(post_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Cannot read post file: {exc}")

    caption = str(post.get("caption", "")).strip()
    image_value = str(post.get("image", "")).strip()

    if not caption or not image_value:
        fail("Post JSON must contain non-empty 'caption' and 'image' fields.")

    image_path = (ROOT / image_value).resolve()

    # Keep image paths inside the repository.
    if not image_path.is_relative_to(ROOT.resolve()):
        fail("Image path must stay inside the repository.")

    if not image_path.is_file():
        fail(f"Image file not found: {image_path}")

    if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        fail("Image must be a JPG, JPEG, or PNG file.")

    url = (
        f"https://graph.facebook.com/{API_VERSION}/"
        f"{PAGE_ID}/photos"
    )

    try:
        with image_path.open("rb") as image_file:
            response = requests.post(
                url,
                data={
                    "access_token": ACCESS_TOKEN,
                    "message": caption,
                    "published": "true",
                },
                files={
                    "source": (
                        image_path.name,
                        image_file,
                        "image/png"
                        if image_path.suffix.lower() == ".png"
                        else "image/jpeg",
                    )
                },
                timeout=120,
            )

        try:
            result = response.json()
        except ValueError:
            fail(f"Facebook returned HTTP {response.status_code}.")

        if not response.ok or "error" in result:
            fail(f"Facebook publishing failed: {result}")

        print(
            f"Published successfully. "
            f"Date={today}, slot={SLOT}, "
            f"photo_id={result.get('id')}"
        )

    except requests.RequestException as exc:
        fail(f"Facebook API request failed: {exc}")


if __name__ == "__main__":
    main()
