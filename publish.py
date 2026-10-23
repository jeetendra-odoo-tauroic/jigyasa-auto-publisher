import io
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent
TIMEZONE = ZoneInfo("Asia/Kolkata")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
API_VERSION = os.environ.get("FACEBOOK_GRAPH_API_VERSION", "v23.0").strip()
SLOT = os.environ.get("POST_SLOT", "").strip()
VALID_SLOTS = {"07:00", "10:00", "13:30", "20:30"}
ZIP_PATH = ROOT / "daily-posts.zip"


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def read_post_from_zip(day, slot):
    """Read the requested slot's JSON and image directly from daily-posts.zip."""
    json_member = f"content/{day}/{slot.replace(':', '-')}.json"
    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as archive:
            names = set(archive.namelist())
            if json_member not in names:
                fail(f"{json_member} is missing from daily-posts.zip. Upload the ZIP for today's date.")
            try:
                post = json.loads(archive.read(json_member).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
                fail(f"Cannot read {json_member} inside daily-posts.zip: {exc}")
            caption = str(post.get("caption", "")).strip()
            image_value = str(post.get("image", "")).strip()
            if not caption or not image_value:
                fail(f"{json_member} must contain non-empty 'caption' and 'image' fields.")
            image_member = PurePosixPath(image_value).as_posix()
            if image_member.startswith("/") or ".." in PurePosixPath(image_member).parts:
                fail("Image path in ZIP JSON must stay inside the content folder.")
            if image_member not in names:
                fail(f"Image '{image_member}' referenced by {json_member} is missing from the ZIP.")
            suffix = PurePosixPath(image_member).suffix.lower()
            if suffix not in {".jpg", ".jpeg", ".png"}:
                fail("Image in ZIP must be a JPG, JPEG, or PNG file.")
            image_bytes = archive.read(image_member)
            if len(image_bytes) < 1000:
                fail(f"Image '{image_member}' is empty or unexpectedly small.")
            return post, image_member, image_bytes, suffix
    except zipfile.BadZipFile:
        fail("daily-posts.zip is not a valid ZIP file. Recreate it and upload it again.")
    except OSError as exc:
        fail(f"Cannot open daily-posts.zip: {exc}")


def read_post_from_files(day, slot):
    """Backward compatibility for posts committed as individual files."""
    slot_file = slot.replace(":", "-")
    post_file = ROOT / "content" / day / f"{slot_file}.json"
    if not post_file.is_file():
        fail(
            f"No post found for {day}, {slot}. Expected daily-posts.zip at the repository root "
            f"with content/{day}/ files, or individual files in content/{day}/."
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
    if not image_path.is_relative_to(ROOT.resolve()):
        fail("Image path must stay inside the repository.")
    if not image_path.is_file():
        fail(f"Image file not found: {image_path}")
    suffix = image_path.suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        fail("Image must be a JPG, JPEG, or PNG file.")
    return post, image_path.name, image_path.read_bytes(), suffix


def main():
    if not PAGE_ID or not ACCESS_TOKEN:
        fail("Add FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN to GitHub Secrets.")
    if SLOT not in VALID_SLOTS:
        fail(f"Invalid posting slot: {SLOT!r}")

    today = datetime.now(TIMEZONE).date().isoformat()
    if ZIP_PATH.is_file():
        post, image_name, image_bytes, suffix = read_post_from_zip(today, SLOT)
        source = "daily-posts.zip"
    else:
        post, image_name, image_bytes, suffix = read_post_from_files(today, SLOT)
        source = "individual repository files"

    caption = str(post.get("caption", "")).strip()
    url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/photos"
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    try:
        response = requests.post(
            url,
            data={"access_token": ACCESS_TOKEN, "message": caption, "published": "true"},
            files={"source": (Path(image_name).name, io.BytesIO(image_bytes), mime)},
            timeout=120,
        )
        try:
            result = response.json()
        except ValueError:
            fail(f"Facebook returned HTTP {response.status_code}.")
        if not response.ok or "error" in result:
            fail(f"Facebook publishing failed: {result}")
        print(
            f"Published successfully. Date={today}, slot={SLOT}, source={source}, "
            f"photo_id={result.get('id')}"
        )
    except requests.RequestException as exc:
        fail(f"Facebook API request failed: {exc}")


if __name__ == "__main__":
    main()
