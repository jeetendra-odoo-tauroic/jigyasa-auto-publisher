import io
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent
TIMEZONE = ZoneInfo("Asia/Kolkata")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
API_VERSION = os.environ.get("FACEBOOK_GRAPH_API_VERSION", "v23.0").strip()
SLOT = os.environ.get("POST_SLOT", "").strip()
VALID_SLOTS = {"07:00", "10:00", "13:30", "20:30"}


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def read_json_from_zip(zf, slot_file):
    # Preferred ZIP format: the JSON files are at the archive root.
    candidates = [n for n in zf.namelist() if not n.endswith("/") and Path(n).name == f"{slot_file}.json"]
    if len(candidates) != 1:
        fail(f"ZIP must contain exactly one {slot_file}.json; found {len(candidates)}.")
    try:
        return json.loads(zf.read(candidates[0]).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
        fail(f"Cannot parse {candidates[0]}: {exc}")


def find_image_in_zip(zf, image_value, slot_file):
    # JSON may use the repo-relative path or just the filename.
    requested_name = Path(image_value).name if image_value else f"{slot_file}.jpg"
    if requested_name not in {f"{slot_file}.jpg", f"{slot_file}.jpeg", f"{slot_file}.png"}:
        fail(f"Image in {slot_file}.json must be named {slot_file}.jpg/.jpeg/.png.")
    candidates = [
        n for n in zf.namelist()
        if not n.endswith("/") and Path(n).name == requested_name
    ]
    if len(candidates) != 1:
        fail(f"ZIP must contain exactly one {requested_name}; found {len(candidates)}.")
    try:
        data = zf.read(candidates[0])
    except KeyError:
        fail(f"Image file missing from ZIP: {requested_name}")
    if len(data) < 1000:
        fail(f"Image file is unexpectedly small: {requested_name}")
    return requested_name, data


def main():
    if not PAGE_ID or not ACCESS_TOKEN:
        fail("Add FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN to GitHub Secrets.")
    if SLOT not in VALID_SLOTS:
        fail(f"Invalid posting slot: {SLOT!r}")

    today = datetime.now(TIMEZONE).date().isoformat()
    slot_file = SLOT.replace(":", "-")
    folder = ROOT / "content" / today
    zip_path = folder / "jigyasa-daily.zip"

    # Preferred path: one daily ZIP contains all four JSON/image pairs.
    if zip_path.is_file():
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                bad_member = zf.testzip()
                if bad_member:
                    fail(f"ZIP integrity check failed for {bad_member}")
                post = read_json_from_zip(zf, slot_file)
                caption = str(post.get("caption", "")).strip()
                if not caption:
                    fail(f"{slot_file}.json has an empty caption.")
                image_name, image_bytes = find_image_in_zip(
                    zf, str(post.get("image", "")).strip(), slot_file
                )
        except zipfile.BadZipFile as exc:
            fail(f"Invalid daily ZIP: {exc}")
    else:
        # Backward-compatible support for existing separate image/JSON files.
        post_file = folder / f"{slot_file}.json"
        if not post_file.is_file():
            fail(f"Neither {zip_path} nor {post_file} exists.")
        try:
            post = json.loads(post_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(f"Cannot read post file: {exc}")
        caption = str(post.get("caption", "")).strip()
        image_value = str(post.get("image", "")).strip()
        if not caption or not image_value:
            fail("Post JSON must contain non-empty 'caption' and 'image' fields.")
        image_path = (ROOT / image_value).resolve()
        if not image_path.is_relative_to(ROOT.resolve()):
            fail("Image path must stay inside the repository.")
        if not image_path.is_file() or image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            fail(f"Image file missing or unsupported: {image_path}")
        image_name = image_path.name
        image_bytes = image_path.read_bytes()

    if not caption:
        fail("Post caption is empty.")

    url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/photos"
    mime = "image/png" if image_name.lower().endswith(".png") else "image/jpeg"
    try:
        response = requests.post(
            url,
            data={
                "access_token": ACCESS_TOKEN,
                "message": caption,
                "published": "true",
            },
            files={"source": (image_name, io.BytesIO(image_bytes), mime)},
            timeout=120,
        )
        try:
            result = response.json()
        except ValueError:
            fail(f"Facebook returned HTTP {response.status_code}.")
        if not response.ok or "error" in result:
            fail(f"Facebook publishing failed: {result}")
        print(f"Published successfully. Date={today}, slot={SLOT}, photo_id={result.get('id')}")
    except requests.RequestException as exc:
        fail(f"Facebook API request failed: {exc}")


if __name__ == "__main__":
    main()
