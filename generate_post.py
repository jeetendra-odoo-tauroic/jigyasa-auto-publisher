#!/usr/bin/env python3
"""Generate four fresh Hindi Facebook posts with Gemini and render graphics with Pillow."""
import argparse
import base64
import json
import os
import random
import sys
import requests
from io import BytesIO
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo(os.getenv("POST_TIMEZONE", "Asia/Kolkata"))
SLOTS = ["07:00", "10:00", "13:30", "20:30"]
BRAND = (os.getenv("BRAND_NAME") or "Jigyasa").strip()
NICHE = (os.getenv("CONTENT_NICHE") or "Hindi thoughts, life lessons and everyday knowledge").strip()
LANGUAGE = (os.getenv("POST_LANGUAGE") or "Hindi").strip()
AUDIENCE = (os.getenv("TARGET_AUDIENCE") or "general audience in India").strip()
WIDTH, HEIGHT = 1080, 1350

# Each entry contains a short Hindi graphic quote and its ready-to-publish caption.
POSTS = [
    {
        "topic": "जीवन की सच्चाई",
        "title": "हर बात का जवाब देना ज़रूरी नहीं",
        "quote": "हर बात का जवाब देना\nज़रूरी नहीं होता…",
        "subquote": "कभी-कभी आपकी ख़ामोशी ही\nआपकी सबसे बड़ी ताकत होती है।",
        "caption": "ज़िंदगी में हर बात पर सफ़ाई देना ज़रूरी नहीं। कभी-कभी सुकून चुनना ही सबसे सही जवाब होता है।\nआपकी क्या राय है?",
        "hashtags": "#ज़िंदगी #हिंदीविचार #सच्चीबात #LifeQuotes #Jigyasa",
    },
    {
        "topic": "रिश्ते",
        "title": "रिश्ते वक्त से नहीं, एहसास से चलते हैं",
        "quote": "रिश्ते वक्त से नहीं,\nएहसास से चलते हैं…",
        "subquote": "जहाँ परवाह सच्ची हो,\nवहाँ बहाने कम होते हैं।",
        "caption": "रिश्तों में सबसे कीमती चीज़ समय नहीं, बल्कि यह एहसास है कि कोई आपको दिल से याद करता है। ❤️\nक्या आप सहमत हैं?",
        "hashtags": "#रिश्ते #दिलकीबात #हिंदीकोट्स #TrueWords #Jigyasa",
    },
    {
        "topic": "मेहनत",
        "title": "धीरे चलना भी आगे बढ़ना है",
        "quote": "धीरे चल रहे हैं तो\nरुक मत जाइए…",
        "subquote": "छोटे कदम भी एक दिन\nबड़ी मंज़िल तक पहुँचाते हैं।",
        "caption": "हर किसी की रफ़्तार अलग होती है। अपनी मेहनत पर भरोसा रखिए और आगे बढ़ते रहिए। 🌱\nआज आपका लक्ष्य क्या है?",
        "hashtags": "#मेहनत #प्रेरणा #सकारात्मकसोच #HindiMotivation #Jigyasa",
    },
    {
        "topic": "समाज की सच्चाई",
        "title": "इंसान की पहचान उसके व्यवहार से",
        "quote": "इंसान की पहचान\nउसके शब्दों से नहीं…",
        "subquote": "मुश्किल वक्त में उसके\nव्यवहार से होती है।",
        "caption": "अच्छी बातें कहना आसान है, लेकिन मुश्किल समय में साथ देना असली पहचान है।\nआपके हिसाब से इंसान की पहचान किससे होती है?",
        "hashtags": "#समाज #सच्चाई #अनमोलवचन #HindiThoughts #Jigyasa",
    },
    {
        "topic": "आत्मसम्मान",
        "title": "अपनी कीमत पहचानिए",
        "quote": "सबको खुश करते-करते\nखुद को मत भूलिए…",
        "subquote": "आपका सुकून और\nआत्मसम्मान भी ज़रूरी है।",
        "caption": "दूसरों की परवाह कीजिए, लेकिन अपने मन की शांति और आत्मसम्मान का भी ख्याल रखिए। ❤️\nयह बात याद रखेंगे ना?",
        "hashtags": "#आत्मसम्मान #खुदसेप्यार #हिंदीविचार #SelfRespect #Jigyasa",
    },
]


def load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def centered_multiline(draw, text, y, font, fill, spacing=20, stroke_width=0, stroke_fill=None):
    # Pillow on GitHub Actions uses libraqm when available for Devanagari shaping.
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center",
                                  stroke_width=stroke_width, direction="ltr")
    text_w = bbox[2] - bbox[0]
    x = (WIDTH - text_w) / 2
    draw.multiline_text((x, y), text, font=font, fill=fill, spacing=spacing, align="center",
                        stroke_width=stroke_width, stroke_fill=stroke_fill, direction="ltr")


def create_image(post, output_path):
    """Generate a topic-specific hero image with Gemini Image, then add restrained Hindi branding."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY for image generation.")

    scene_prompt = f"""Create a premium, photorealistic editorial image for a Hindi Facebook knowledge/lifestyle page.
Topic: {post.get('topic', '')}
Post idea: {post.get('title', '')}. Context: {post.get('subquote', '')}
Visual direction: {post.get('visual_style', 'cinematic natural light, sophisticated colors')}.
Make the image tell the story visually with a clear subject, rich natural details, beautiful lighting, professional composition, and realistic textures.
Portrait 4:5 composition for a Facebook feed. Keep the main subject in the upper and middle areas; leave the lower 25 percent visually calm and darker so a short headline can be overlaid later.
No text, no letters, no typography, no logos, no watermarks, no borders, no quote-card design, no decorative circles, no collage, no infographic. It must look like a professional photograph/editorial visual, not a text poster."""

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "model": "gemini-3.1-flash-image",
            "input": [{"type": "text", "text": scene_prompt}],
            "response_format": {
                "type": "image",
                "mime_type": "image/jpeg",
                "aspect_ratio": "4:5",
                "image_size": "1K",
            },
        },
        timeout=(15, 150),
    )
    if not response.ok:
        raise RuntimeError(f"Gemini image API returned HTTP {response.status_code}: {response.text[:500]}")
    data = response.json()

    # The Interactions REST response may expose the final image directly or inside model_output steps.
    image_data = None
    direct = data.get("output_image")
    if isinstance(direct, dict):
        image_data = direct.get("data")
    if not image_data:
        def find_image(node):
            if isinstance(node, dict):
                if node.get("type") == "image" and isinstance(node.get("data"), str):
                    return node["data"]
                for value in node.values():
                    found = find_image(value)
                    if found:
                        return found
            elif isinstance(node, list):
                for value in node:
                    found = find_image(value)
                    if found:
                        return found
            return None
        image_data = find_image(data.get("output", data.get("steps", data)))
    if not image_data:
        raise RuntimeError("Gemini image response did not contain image data.")

    try:
        image = Image.open(BytesIO(base64.b64decode(image_data))).convert("RGB")
    except Exception as exc:
        raise RuntimeError("Could not decode Gemini-generated image bytes.") from exc

    # Crop to the Facebook 4:5 feed ratio without stretching the generated artwork.
    target_ratio = WIDTH / HEIGHT
    current_ratio = image.width / image.height
    if current_ratio > target_ratio:
        crop_width = int(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    else:
        crop_height = int(image.width / target_ratio)
        top = max(0, (image.height - crop_height) // 3)
        image = image.crop((0, top, image.width, top + crop_height))
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGBA")

    # A subtle bottom fade keeps the photograph dominant while preserving Hindi headline readability.
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pixels = overlay.load()
    fade_start = int(HEIGHT * 0.66)
    for y in range(fade_start, HEIGHT):
        alpha = int(12 + 175 * ((y - fade_start) / max(1, HEIGHT - fade_start)))
        for x in range(WIDTH):
            pixels[x, y] = (9, 14, 24, alpha)
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)
    brand_font = load_font(28, bold=True)
    title_font = load_font(54, bold=True)
    subtitle_font = load_font(29)

    # Keep branding small and the amount of overlaid copy deliberately low.
    draw.text((66, HEIGHT - 235), BRAND, font=brand_font, fill=(245, 204, 128, 255))
    title = str(post.get("title", "")).strip()
    # Wrap title to fit the available width; title only, not a large quote-card paragraph.
    words = title.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=title_font)[2] <= WIDTH - 132:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    title_text = "\\n".join(lines[:2])
    draw.multiline_text((66, HEIGHT - 190), title_text, font=title_font,
                        fill=(255, 255, 255, 255), spacing=8, stroke_width=0)
    image.convert("RGB").save(output_path, "JPEG", quality=93, optimize=True)


def generate_with_gemini(day):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY GitHub Actions secret.")
    slots_text = ", ".join(SLOTS)
    prompt = f"""Create exactly four distinct, engaging Facebook posts in Hindi for the brand {BRAND}.
Niche: {NICHE}. Audience: {AUDIENCE}. Language: {LANGUAGE}. Date: {day}.
One post for each slot, exactly: {slots_text}. Return only a valid JSON array.
Each object must contain: slot, topic, title, quote, subquote, caption, hashtags, visual_style.
Rules:
- Use natural, correct Hindi in Devanagari. Avoid repeated themes or wording across the four posts.
- quote should be a short emotionally resonant line, suitable for a graphic, with at most two lines separated by \n.
- subquote should add a meaningful second thought, at most two lines separated by \n.
- title should be short. caption should be ready to publish and invite genuine comments without engagement bait.
- hashtags must be a string of 4-8 relevant hashtags, including #Jigyasa.
- visual_style should be a short description of a color palette/mood for a text graphic.
- Avoid fabricated statistics, current-affairs claims, medical/financial advice, hate, and political misinformation.
- Do not include markdown fences or any extra text.
JSON example shape: [{{"slot":"07:00","topic":"जीवन","title":"...","quote":"...\n...","subquote":"...\n...","caption":"...","hashtags":"#... #Jigyasa","visual_style":"warm sunrise palette"}}]"""
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.8},
    }
    response = None
    errors = []
    # Use the preferred model first, then a lighter stable fallback if it is overloaded.
    for model in ("gemini-3.8-flash", "gemini-3.5-flash-lite"):
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for attempt in range(2):
            try:
                candidate = requests.post(
                    endpoint,
                    headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                    json=payload,
                    timeout=(10, 45),
                )
            except requests.RequestException as exc:
                errors.append(f"{model} attempt {attempt + 1}: {exc}")
                continue
            if candidate.ok:
                response = candidate
                print(f"Gemini model used: {model}")
                break
            errors.append(f"{model} HTTP {candidate.status_code}: {candidate.text[:250]}")
            if candidate.status_code not in (408, 429, 500, 502, 503, 504):
                break
            import time
            if attempt == 0:
                time.sleep(2)
        if response is not None:
            break
    if response is None:
        raise RuntimeError("All Gemini model attempts failed. " + " | ".join(errors[-4:]))
    data = response.json()
    try:
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        posts = json.loads(raw)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Gemini returned an invalid JSON response.") from exc
    if not isinstance(posts, list) or len(posts) != len(SLOTS):
        raise RuntimeError("Gemini must return exactly four post objects.")
    by_slot = {}
    required = ("topic", "title", "quote", "subquote", "caption", "hashtags")
    for post in posts:
        if not isinstance(post, dict) or post.get("slot") not in SLOTS:
            raise RuntimeError("Gemini returned a missing or invalid slot.")
        slot = post["slot"]
        if slot in by_slot or any(not str(post.get(k, "")).strip() for k in required):
            raise RuntimeError(f"Gemini returned duplicate slot or missing fields for {slot}.")
        by_slot[slot] = post
    if set(by_slot) != set(SLOTS):
        raise RuntimeError("Gemini did not return all four required slots.")
    return by_slot


def save_post(post, day, slot):
    post.update({
        "date": day,
        "slot": slot,
        "brand": BRAND,
        "language": LANGUAGE,
        "niche": NICHE,
        "target_audience": AUDIENCE,
        "generator": "gemini-3.8-flash+pillow",
    })
    post["caption"] = post["caption"].strip() + "\n\n" + post["hashtags"].strip()
    folder = ROOT / "content" / day
    folder.mkdir(parents=True, exist_ok=True)
    slot_name = slot.replace(":", "-")
    image_rel = f"content/{day}/{slot_name}.jpg"
    image_path = ROOT / image_rel
    create_image(post, image_path)
    if not image_path.is_file() or image_path.stat().st_size < 10000:
        raise RuntimeError(f"Generated image is missing or unexpectedly small: {image_rel}")
    post["image"] = image_rel
    (folder / f"{slot_name}.json").write_text(
        json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created: {image_rel} | {post['title']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-slots", action="store_true", help="Generate the four daily posts.")
    parser.add_argument("--slot", choices=SLOTS, help="Generate only one post for this slot.")
    args = parser.parse_args()
    if not args.all_slots and not args.slot:
        parser.error("Use --all-slots or --slot.")
    now = datetime.now(TZ)
    day = now.date().isoformat()
    try:
        generated = generate_with_gemini(day)
        slots = SLOTS if args.all_slots else [args.slot]
        for slot in slots:
            post = dict(generated[slot])
            post["image_prompt"] = post.get("visual_style", "Elegant Hindi quote graphic")
            save_post(post, day, slot)
        print(f"Generated {len(slots)} post(s) for {day} using Gemini and Pillow.")
    except Exception as exc:
        sys.exit("Post generation failed: " + str(exc))


if __name__ == "__main__":
    main()
