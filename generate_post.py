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
    """Draw a topic-aware cinematic editorial scene with Pillow; no image API required."""
    topic = str(post.get("topic", "")).lower()
    title = str(post.get("title", "")).strip()
    palettes = {
        "warm": ((29, 43, 64), (197, 123, 79), (255, 213, 145), (28, 38, 48)),
        "rose": ((49, 34, 54), (174, 101, 108), (249, 207, 170), (29, 28, 39)),
        "green": ((24, 49, 45), (102, 142, 97), (231, 205, 147), (20, 38, 37)),
        "blue": ((20, 38, 60), (83, 128, 148), (228, 218, 184), (18, 33, 43)),
    }
    if any(k in topic for k in ("रिश्त", "परिवार", "प्यार", "प्रेम")):
        top, horizon, light, dark = palettes["rose"]
    elif any(k in topic for k in ("मेहनत", "सफल", "प्रेरणा", "लक्ष्य")):
        top, horizon, light, dark = palettes["green"]
    elif any(k in topic for k in ("समाज", "ज्ञान", "शिक्षा", "देश")):
        top, horizon, light, dark = palettes["blue"]
    else:
        top, horizon, light, dark = palettes["warm"]

    image = Image.new("RGB", (WIDTH, HEIGHT))
    pix = image.load()
    for y in range(HEIGHT):
        t = y / HEIGHT
        for x in range(WIDTH):
            glow = max(0.0, 1 - (((x-WIDTH*.68)/(WIDTH*.8))**2 + ((y-HEIGHT*.38)/(HEIGHT*.6))**2))
            pix[x, y] = tuple(max(0, min(255, int(top[i]*(1-t) + horizon[i]*t + light[i]*glow*.20))) for i in range(3))
    draw = ImageDraw.Draw(image, "RGBA")
    sx, sy = int(WIDTH*.70), int(HEIGHT*.34)
    for r, a in ((190, 15), (130, 25), (70, 45)):
        draw.ellipse((sx-r, sy-r, sx+r, sy+r), fill=(*light, a))
    draw.ellipse((sx-48, sy-48, sx+48, sy+48), fill=(*light, 220))
    draw.polygon([(0,650),(170,510),(320,630),(500,475),(710,630),(900,500),(WIDTH,590),(WIDTH,1000),(0,1000)], fill=(*dark,150))
    draw.polygon([(0,790),(210,650),(420,770),(650,610),(850,730),(WIDTH,650),(WIDTH,HEIGHT),(0,HEIGHT)], fill=(13,27,35,225))

    if any(k in topic for k in ("रिश्त", "परिवार", "प्यार", "प्रेम", "दोस्ती")):
        for cx, cy, scale in ((425,700,1.0),(585,710,.88)):
            r = int(30*scale)
            draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(15,23,32,255))
            draw.rounded_rectangle((cx-int(48*scale),cy+r-2,cx+int(48*scale),1020), radius=30, fill=(15,23,32,255))
    elif any(k in topic for k in ("मेहनत", "सफल", "प्रेरणा", "लक्ष्य", "संघर्ष")):
        draw.polygon([(70,1050),(250,850),(365,930),(520,730),(650,820),(790,680),(WIDTH,900),(WIDTH,HEIGHT)], fill=(14,30,34,245))
        draw.line([(140,1030),(300,900),(420,930),(540,785)], fill=(*light,190), width=7)
        cx,cy=470,770
        draw.ellipse((cx-22,cy-72,cx+22,cy-28), fill=(12,22,29,255))
        draw.polygon([(cx-23,cy-30),(cx+23,cy-30),(cx+43,cy+58),(cx-35,cy+58)], fill=(12,22,29,255))
        draw.line((cx-10,cy+50,cx-42,cy+125), fill=(12,22,29,255), width=16)
        draw.line((cx+15,cy+50,cx+45,cy+112), fill=(12,22,29,255), width=16)
    elif any(k in topic for k in ("ज्ञान", "सीख", "शिक्षा", "किताब")):
        draw.rectangle((90,740,990,1050), fill=(45,31,25,200))
        draw.polygon([(150,800),(510,850),(510,1000),(150,930)], fill=(240,224,190,255))
        draw.polygon([(510,850),(880,785),(880,925),(510,1000)], fill=(250,237,205,255))
        for yy in (855,885,915):
            draw.line((215,yy,455,yy+34), fill=(112,94,73,170), width=3)
            draw.line((565,yy+20,820,yy-25), fill=(112,94,73,170), width=3)
        draw.line((510,850,510,1000), fill=(105,76,48,220), width=5)
    else:
        draw.polygon([(0,900),(WIDTH,820),(WIDTH,HEIGHT),(0,HEIGHT)], fill=(15,32,37,230))
        draw.polygon([(360,HEIGHT),(525,850),(595,850),(800,HEIGHT)], fill=(*light,90))

    shade = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    sp = shade.load()
    for y in range(int(HEIGHT*.68), HEIGHT):
        alpha = int(12 + 175*((y-HEIGHT*.68)/(HEIGHT*.32)))
        for x in range(WIDTH):
            sp[x,y] = (6,12,19,alpha)
    image = Image.alpha_composite(image.convert("RGBA"), shade)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((66, HEIGHT-225), BRAND, font=load_font(28, True), fill=(245,204,128,255))
    font = load_font(51, True)
    lines, current = [], ""
    for word in title.split():
        trial = (current + " " + word).strip()
        if draw.textbbox((0,0), trial, font=font)[2] <= WIDTH-132:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    draw.multiline_text((66, HEIGHT-180), "\n".join(lines[:2]), font=font, fill=(255,255,255,255), spacing=8, stroke_width=1, stroke_fill=(0,0,0,110))
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
- visual_style should describe a realistic editorial scene that visually represents the topic; avoid text-card/quote-card concepts.
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
        "generator": "gemini-text+pillow-scene-art",
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
            post["image_prompt"] = post.get("visual_style", "cinematic realistic editorial scene with natural light")
            save_post(post, day, slot)
        print(f"Generated {len(slots)} post(s) for {day} using Gemini and Pillow.")
    except Exception as exc:
        sys.exit("Post generation failed: " + str(exc))


if __name__ == "__main__":
    main()
