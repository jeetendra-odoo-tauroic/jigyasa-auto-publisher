#!/usr/bin/env python3
"""Generate four fresh Hindi Facebook posts with Gemini and render graphics with Pillow."""
import argparse
import json
import os
import random
import sys
import requests
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
    """Media-provider boundary: replace/extend this for future AI artwork."""
    # Choose a reproducible palette per post so scheduled runs look varied.
    seed = f"{post['date']}-{post['slot']}-{post['topic']}"
    rng = random.Random(seed)
    palettes = [
        ((22, 25, 68), (99, 43, 113), (255, 204, 128)),
        ((7, 68, 78), (20, 126, 120), (255, 225, 170)),
        ((83, 34, 53), (164, 67, 76), (255, 218, 185)),
        ((24, 48, 91), (58, 92, 151), (255, 215, 126)),
        ((57, 44, 94), (126, 71, 120), (255, 225, 170)),
    ]
    top, bottom, accent = rng.choice(palettes)
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(WIDTH):
            pixels[x, y] = color

    draw = ImageDraw.Draw(image, "RGBA")
    # Decorative circles and border.
    draw.ellipse((-180, -170, 360, 370), fill=(*accent, 24), outline=(*accent, 100), width=3)
    draw.ellipse((790, 970, 1260, 1440), fill=(*accent, 20), outline=(*accent, 90), width=3)
    draw.rounded_rectangle((54, 54, WIDTH - 54, HEIGHT - 54), radius=34,
                           outline=(*accent, 190), width=3)
    draw.rounded_rectangle((WIDTH // 2 - 80, 145, WIDTH // 2 + 80, 155), radius=5,
                           fill=(*accent, 255))

    brand_font = load_font(34, bold=True)
    quote_font = load_font(68, bold=True)
    sub_font = load_font(42)
    footer_font = load_font(28)
    draw.text((WIDTH // 2, 205), BRAND, font=brand_font, fill=(255, 238, 204, 255),
              anchor="mm", stroke_width=0)
    centered_multiline(draw, post["quote"], 380, quote_font, (255, 255, 255, 255),
                       spacing=28, stroke_width=1, stroke_fill=(0, 0, 0, 35))
    draw.line((WIDTH // 2 - 75, 770, WIDTH // 2 + 75, 770), fill=(*accent, 255), width=5)
    centered_multiline(draw, post["subquote"], 825, sub_font, (255, 239, 220, 255), spacing=22)
    draw.text((WIDTH // 2, 1170), "सोचिए • समझिए • आगे बढ़िए", font=footer_font,
              fill=(255, 232, 195, 255), anchor="mm")
    image.save(output_path, "JPEG", quality=92, optimize=True)


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
- quote should be a short emotionally resonant line, suitable for a graphic, with at most two lines separated by \\n.
- subquote should add a meaningful second thought, at most two lines separated by \\n.
- title should be short. caption should be ready to publish and invite genuine comments without engagement bait.
- hashtags must be a string of 4-8 relevant hashtags, including #Jigyasa.
- visual_style should be a short description of a color palette/mood for a text graphic.
- Avoid fabricated statistics, current-affairs claims, medical/financial advice, hate, and political misinformation.
- Do not include markdown fences or any extra text.
JSON example shape: [{{"slot":"07:00","topic":"जीवन","title":"...","quote":"...\\n...","subquote":"...\\n...","caption":"...","hashtags":"#... #Jigyasa","visual_style":"warm sunrise palette"}}]"""
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9},
        },
        timeout=90,
    )
    if not response.ok:
        raise RuntimeError(f"Gemini API returned HTTP {response.status_code}: {response.text[:500]}")
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
        "generator": "gemini-2.5-flash+pillow",
    })
    post["caption"] = post["caption"].strip() + "\\n\\n" + post["hashtags"].strip()
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
        json.dumps(post, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8"
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
