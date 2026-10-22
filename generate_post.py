#!/usr/bin/env python3
"""Generate Hindi social quote graphics with Pillow; no paid API required.

Future extension point: keep create_image(post, output_path) as the media
provider boundary so a local or hosted AI image model can be added later.
"""
import argparse
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo(os.getenv("POST_TIMEZONE", "Asia/Kolkata"))
SLOTS = ["07:00", "10:00", "13:30", "16:10", "20:30"]
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True, choices=SLOTS)
    slot = parser.parse_args().slot
    now = datetime.now(TZ)
    day = now.date().isoformat()

    # Rotate content by date and slot without needing an external API.
    index = (now.date().toordinal() + SLOTS.index(slot)) % len(POSTS)
    post = dict(POSTS[index])
    post.update({
        "image_prompt": "Pillow-generated Hindi quote graphic; future AI artwork can be plugged in here.",
        "date": day,
        "slot": slot,
        "brand": BRAND,
        "language": LANGUAGE,
        "niche": NICHE,
        "target_audience": AUDIENCE,
        "generator": "pillow_quote_graphic",
    })
    post["caption"] = post["caption"].strip() + "\n\n" + post["hashtags"].strip()

    folder = ROOT / "content" / day
    folder.mkdir(parents=True, exist_ok=True)
    slot_name = slot.replace(":", "-")
    image_rel = f"content/{day}/{slot_name}.jpg"
    image_path = ROOT / image_rel
    try:
        create_image(post, image_path)
    except Exception as exc:
        sys.exit("Could not create quote graphic: " + str(exc))
    if not image_path.is_file() or image_path.stat().st_size < 10000:
        sys.exit("Generated image is missing or unexpectedly small.")

    post["image"] = image_rel
    (folder / f"{slot_name}.json").write_text(
        json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created: {image_rel}")
    print("Generator: Pillow (no paid API)")
    print("Title:", post["title"])
    print("Hashtags:", post["hashtags"])


if __name__ == "__main__":
    main()
