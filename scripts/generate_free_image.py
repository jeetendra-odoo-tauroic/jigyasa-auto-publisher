#!/usr/bin/env python3
"""Create a free, API-free Jigyasa social image with Pillow.

This creates original illustrated editorial artwork (not photorealistic AI imagery).
It uses only Python/Pillow and system fonts; no paid API or external image service.
"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import math
import random
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Kolkata")
W, H = 1080, 1350
BRAND = "Jigyasa"
TAGLINE = "DISCOVER  |  LEARN  |  GROW"

POSTS = [
    {
        "topic": "नई शुरुआत",
        "title": "हर दिन एक नई शुरुआत",
        "quote": "छोटा कदम भी\nआपको आगे ले जाता है।",
        "caption": "ज़िंदगी एक ही दिन में नहीं बदलती। रोज़ की छोटी-छोटी अच्छी आदतें मिलकर बड़ा बदलाव लाती हैं। आज अपने लिए एक अच्छा कदम ज़रूर उठाइए। 🌱\n\nआप आज क्या बेहतर करने वाले हैं?",
        "hashtags": "#Jigyasa #HindiThoughts #SelfGrowth #DailyMotivation #जीवनकीसीख",
        "palette": ((24, 45, 67), (231, 154, 93), (255, 221, 158)),
    },
    {
        "topic": "आत्मसम्मान",
        "title": "अपनी कीमत पहचानिए",
        "quote": "सबको खुश करते-करते\nखुद को मत भूलिए।",
        "caption": "दूसरों की परवाह करना अच्छी बात है, लेकिन अपनी शांति और आत्मसम्मान का ध्यान रखना भी उतना ही ज़रूरी है। ❤️\n\nक्या आप सहमत हैं?",
        "hashtags": "#Jigyasa #SelfRespect #HindiQuotes #LifeLessons #सच्चीबात",
        "palette": ((40, 35, 57), (173, 103, 117), (255, 208, 177)),
    },
    {
        "topic": "मेहनत",
        "title": "धीरे चलना भी आगे बढ़ना है",
        "quote": "अपनी रफ़्तार से चलिए,\nबस रुकिए मत।",
        "caption": "हर किसी की मंज़िल और रफ़्तार अलग होती है। दूसरों से तुलना करने के बजाय अपनी कोशिश पर भरोसा रखिए। 🌿\n\nआज आपका छोटा-सा लक्ष्य क्या है?",
        "hashtags": "#Jigyasa #MotivationHindi #Consistency #GrowthMindset #प्रेरणा",
        "palette": ((23, 52, 48), (104, 145, 105), (238, 218, 162)),
    },
    {
        "topic": "रिश्ते",
        "title": "रिश्ते एहसास से चलते हैं",
        "quote": "जहाँ परवाह सच्ची हो,\nवहाँ बहाने कम होते हैं।",
        "caption": "रिश्तों की खूबसूरती बड़े वादों में नहीं, छोटी-छोटी परवाह में दिखाई देती है। ❤️\n\nआपके लिए रिश्ते में सबसे ज़रूरी क्या है?",
        "hashtags": "#Jigyasa #Relationships #HindiThoughts #दिलकीबात #LifeLessons",
        "palette": ((47, 35, 55), (174, 103, 111), (255, 215, 180)),
    },
    {
        "topic": "सकारात्मक सोच",
        "title": "हर मुश्किल हमेशा नहीं रहती",
        "quote": "बुरा वक्त भी गुज़रता है,\nहौसला बनाए रखिए।",
        "caption": "मुश्किल दिन आपकी पूरी कहानी नहीं हैं। थोड़ा ठहरिए, सीखिए और एक बार फिर कोशिश कीजिए। 🌅\n\nयह बात किसे सुनने की ज़रूरत है?",
        "hashtags": "#Jigyasa #PositiveThinking #Hope #HindiQuotes #नईशुरुआत",
        "palette": ((27, 43, 65), (198, 128, 88), (255, 219, 151)),
    },
]


def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def center_text(draw, text, y, fnt, fill, spacing=18, anchor_width=W):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align="center", stroke_width=0)
    x = (anchor_width - (box[2] - box[0])) / 2
    draw.multiline_text((x, y), text, font=fnt, fill=fill, spacing=spacing, align="center")


def make_art(post, output):
    top, horizon, glow = post["palette"]
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = min(1.0, y / H)
        # Smooth gradient from deep twilight to a warm horizon.
        for x in range(W):
            glow_factor = max(0.0, 1.0 - abs(y - 700) / 620) * max(0.0, 1.0 - abs(x - 540) / 800)
            px[x, y] = tuple(
                int(top[i] * (1 - t * 0.30) + horizon[i] * t * 0.30 + (glow[i] - top[i]) * glow_factor * 0.18)
                for i in range(3)
            )

    d = ImageDraw.Draw(im, "RGBA")
    # Soft sun glow and sun disk.
    for r, a in [(210, 12), (160, 16), (112, 24)]:
        d.ellipse((540-r, 670-r, 540+r, 670+r), fill=(*glow, a))
    d.ellipse((465, 595, 615, 745), fill=(*glow, 235))
    # Layered mountain silhouettes.
    d.polygon([(0, 790), (130, 650), (255, 790), (390, 610), (560, 815), (760, 635), (920, 790), (1080, 675), (1080, 1000), (0, 1000)], fill=(34, 49, 61, 220))
    d.polygon([(0, 865), (170, 735), (330, 890), (520, 720), (720, 895), (910, 735), (1080, 860), (1080, 1110), (0, 1110)], fill=(19, 39, 44, 235))
    # Foreground ridge.
    d.polygon([(0, 1000), (210, 920), (410, 1005), (650, 910), (850, 1000), (1080, 915), (1080, 1350), (0, 1350)], fill=(14, 31, 35, 255))
    # Small person silhouette looking toward the sunrise.
    d.ellipse((795, 858, 837, 900), fill=(13, 22, 27, 255))
    d.polygon([(800, 896), (833, 896), (850, 1000), (782, 1000)], fill=(13, 22, 27, 255))
    d.line((805, 925, 778, 976), fill=(13, 22, 27, 255), width=13)
    d.line((828, 924, 852, 971), fill=(13, 22, 27, 255), width=13)
    # Editorial typography area with dark translucent backing.
    d.rounded_rectangle((62, 65, 1018, 565), radius=36, fill=(9, 19, 30, 90), outline=(255, 255, 255, 50), width=2)
    d.text((95, 92), BRAND.upper(), font=font(28, True), fill=(255, 226, 176, 255))
    d.text((95, 132), TAGLINE, font=font(17), fill=(235, 236, 231, 230))
    d.line((95, 174, 260, 174), fill=(*glow, 230), width=4)
    center_text(d, post["title"], 220, font(57, True), (255, 255, 248, 255))
    center_text(d, post["quote"], 365, font(35), (255, 226, 184, 255), spacing=12)
    # Footer label.
    d.text((70, 1270), "सोचिए  •  सीखिए  •  आगे बढ़िए", font=font(22, True), fill=(255, 255, 245, 235))
    d.text((1010, 1277), "01", font=font(18, True), fill=(255, 255, 255, 190), anchor="ra")
    im.save(output, "JPEG", quality=94, optimize=True, progressive=True)


def main():
    today = datetime.now(TZ).date()
    post = POSTS[today.toordinal() % len(POSTS)]
    date = today.isoformat()
    out_dir = ROOT / "drafts" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    image_path = out_dir / f"{date}-jigyasa.jpg"
    make_art(post, image_path)
    if not image_path.exists() or image_path.stat().st_size < 20000:
        raise SystemExit("Image generation failed or output file is unexpectedly small.")

    draft = ROOT / "drafts" / f"{date}-jigyasa-post.md"
    draft.write_text(
        f"# {post['title']}\n\n"
        f"**Topic:** {post['topic']}\n\n"
        f"**Image:** `drafts/images/{image_path.name}`\n\n"
        f"## Caption\n\n{post['caption']}\n\n{post['hashtags']}\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "image": str(image_path.relative_to(ROOT)),
        "image_bytes": image_path.stat().st_size,
        "draft": str(draft.relative_to(ROOT)),
        "title": post["title"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
