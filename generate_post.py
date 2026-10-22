#!/usr/bin/env python3
"""Create a post caption and image with the OpenAI API."""
import argparse, base64, json, os, sys
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo(os.getenv("POST_TIMEZONE", "Asia/Kolkata"))
SLOTS = ["07:00", "10:00", "13:30", "16:10", "20:30"]
KEY = os.getenv("OPENAI_API_KEY", "").strip()
TEXT_MODEL = (os.getenv("OPENAI_TEXT_MODEL") or "gpt-4.1-mini")
IMAGE_MODEL = (os.getenv("OPENAI_IMAGE_MODEL") or "gpt-image-1")
BRAND = (os.getenv("BRAND_NAME") or "Jigyasa")
NICHE = (os.getenv("CONTENT_NICHE") or "Hindi educational content, science, history, technology and everyday knowledge")
LANGUAGE = (os.getenv("POST_LANGUAGE") or "Hindi")
AUDIENCE = (os.getenv("TARGET_AUDIENCE") or "general audience in India")

def api(endpoint, payload, timeout=240):
    try:
        r = requests.post("https://api.openai.com/v1/" + endpoint,
            headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
            json=payload, timeout=timeout)
        data = r.json()
    except Exception as e:
        sys.exit("API request failed: " + str(e))
    if not r.ok:
        sys.exit("OpenAI API error: " + str(data.get("error", {}).get("message", r.status_code)))
    return data

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slot", required=True, choices=SLOTS)
    slot = p.parse_args().slot
    if not KEY:
        sys.exit("Missing OPENAI_API_KEY GitHub Actions secret.")
    day = datetime.now(TZ).date().isoformat()
    instruction = f"""Create an original, accurate, engaging social post.
Brand: {BRAND}; niche: {NICHE}; language: {LANGUAGE}; audience: {AUDIENCE}.
Date: {day}; slot: {slot}.
Return JSON with string fields topic, title, caption, hashtags, image_prompt.
Make title short. Caption ready to publish with a natural call to action.
Provide 5-10 relevant hashtags beginning with #. Avoid unsupported claims.
image_prompt should describe a premium, polished, vivid image illustrating this topic,
with clear composition and no text, letters, logos or watermark. Portrait social format."""
    text = api("chat/completions", {"model": TEXT_MODEL,
        "messages":[{"role":"system","content":"You are a careful social content editor. Return valid JSON only."},
                   {"role":"user","content":instruction}],
        "response_format":{"type":"json_object"}})
    try:
        post = json.loads(text["choices"][0]["message"]["content"])
        for k in ("topic","title","caption","hashtags","image_prompt"):
            if not isinstance(post.get(k), str) or not post[k].strip():
                raise ValueError("missing " + k)
    except Exception as e:
        sys.exit("Invalid post JSON: " + str(e))
    post["caption"] = post["caption"].strip() + "\n\n" + post["hashtags"].strip()
    img = api("images/generations", {"model":IMAGE_MODEL,"prompt":post["image_prompt"],
        "size":"1024x1536","quality":(os.getenv("OPENAI_IMAGE_QUALITY") or "medium"),
        "output_format":"jpeg"}, timeout=300)
    try:
        raw = base64.b64decode(img["data"][0]["b64_json"])
        folder = ROOT / "content" / day
        folder.mkdir(parents=True, exist_ok=True)
        slot_name = slot.replace(":","-")
        image_rel = f"content/{day}/{slot_name}.jpg"
        image_path = ROOT / image_rel
        with Image.open(BytesIO(raw)) as im:
            im.convert("RGB").save(image_path,"JPEG",quality=92,optimize=True)
    except Exception as e:
        sys.exit("Could not save generated image: " + str(e))
    if image_path.stat().st_size < 10000:
        sys.exit("Image file is unexpectedly small.")
    post.update({"image":image_rel,"date":day,"slot":slot,"brand":BRAND})
    (folder / f"{slot_name}.json").write_text(json.dumps(post,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Created: {image_rel}")
    print("Title:",post["title"])
    print("Hashtags:",post["hashtags"])

if __name__ == "__main__":
    main()
