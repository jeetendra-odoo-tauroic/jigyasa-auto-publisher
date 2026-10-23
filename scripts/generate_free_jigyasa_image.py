#!/usr/bin/env python3
"""Create a free, locally rendered Jigyasa Hindi social post (no image API required)."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import math
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "drafts" / "images"
W, H = 1080, 1350
TZ = ZoneInfo("Asia/Kolkata")
BRAND = "Jigyasa"
TAGLINE = "DISCOVER  |  LEARN  |  GROW"

POSTS = [
    {
        "topic": "नई शुरुआत",
        "title": "हर दिन एक नई शुरुआत",
        "quote": "छोटे कदम भी\nआपको आगे ले जाते हैं।",
        "caption": "ज़िंदगी में बदलाव हमेशा बड़े फैसलों से नहीं आता। कभी-कभी रोज़ उठाया गया एक छोटा-सा सही कदम भी नई शुरुआत बन जाता है। 🌱\n\nआज आप कौन-सा छोटा कदम उठाएँगे? कमेंट में बताइए।",
        "hashtags": "#Jigyasa #HindiThoughts #SelfGrowth #LifeLessons #PositiveThinking #नईशुरुआत",
        "palette": ((24, 43, 66), (236, 160, 99), (255, 219, 157), (44, 75, 83)),
    },
    {
        "topic": "आत्मविश्वास",
        "title": "खुद पर भरोसा रखिए",
        "quote": "रफ़्तार धीमी हो सकती है,\nहौसला नहीं।",
        "caption": "हर किसी का सफ़र अलग होता है। दूसरों से तुलना करने के बजाय अपनी कोशिशों पर भरोसा रखिए और हर दिन थोड़ा आगे बढ़िए। ❤️\n\nआपको आगे बढ़ने की प्रेरणा कहाँ से मिलती है?",
        "hashtags": "#Jigyasa #HindiMotivation #आत्मविश्वास #SelfGrowth #LifeLessons",
        "palette": ((26, 49, 47), (115, 153, 109), (239, 215, 160), (35, 70, 65)),
    },
    {
        "topic": "रिश्ते",
        "title": "रिश्तों में एहसास ज़रूरी है",
        "quote": "जहाँ सच्ची परवाह होती है,\nवहाँ कोशिश भी होती है।",
        "caption": "रिश्ते सिर्फ़ बातों से नहीं, बल्कि छोटे-छोटे एहसासों और मुश्किल वक्त में किए गए प्रयासों से मज़बूत होते हैं। ❤️\n\nआपके लिए रिश्ते में सबसे ज़रूरी क्या है?",
        "hashtags": "#Jigyasa #रिश्ते #HindiThoughts #दिलकीबात #LifeLessons",
        "palette": ((55, 37, 58), (180, 106, 116), (255, 210, 177), (73, 48, 67)),
    },
    {
        "topic": "सीख",
        "title": "गलतियाँ भी सिखाती हैं",
        "quote": "हर गलती अंत नहीं,\nएक नई सीख भी है।",
        "caption": "गलती होने पर खुद को रोकिए मत। उससे सीखिए, अपनी दिशा सुधारिए और फिर कोशिश कीजिए। आगे बढ़ना ही असली बात है। 🌿\n\nआपने अपनी किसी गलती से क्या सीखा?",
        "hashtags": "#Jigyasa #जीवनकीसीख #HindiThoughts #GrowthMindset #PositiveThinking",
        "palette": ((31, 46, 63), (100, 139, 148), (241, 217, 166), (37, 66, 72)),
    },
    {
        "topic": "सुकून",
        "title": "हर बात दिल पर न लें",
        "quote": "अपना सुकून बचाना भी\nएक समझदारी है।",
        "caption": "हर बात का जवाब देना और हर किसी को खुश रखना ज़रूरी नहीं। कभी-कभी अपनी शांति को प्राथमिकता देना भी ज़रूरी होता है। 🌼\n\nक्या आप इस बात से सहमत हैं?",
        "hashtags": "#Jigyasa #सुकून #HindiQuotes #SelfRespect #LifeLessons",
        "palette": ((39, 48, 67), (138, 130, 164), (245, 217, 174), (52, 65, 79)),
    },
]

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()

def mix(a, b, t):
    return tuple(int(a[i] * (1-t) + b[i] * t) for i in range(3))

def centered(draw, text, y, fnt, fill, spacing=20):
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align="center", stroke_width=0)
    draw.multiline_text(((W-(box[2]-box[0]))/2, y), text, font=fnt, fill=fill, spacing=spacing, align="center")

def make_art(post, path, seed):
    random.seed(seed)
    top, horizon, sun, hill = post["palette"]
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = min(1, y / (H * 0.78))
        c = mix(top, horizon, t)
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(im, "RGBA")

    # Sun glow and sun disc
    sx, sy = W * 0.72, H * 0.34
    for r in range(250, 20, -8):
        alpha = int(2 + (250-r) * 0.07)
        d.ellipse((sx-r, sy-r, sx+r, sy+r), fill=(*sun, max(0, min(35, alpha))))
    d.ellipse((sx-78, sy-78, sx+78, sy+78), fill=(*sun, 245))

    # Distant ridges
    ridge1 = [(0, 760), (120, 620), (260, 710), (430, 560), (620, 700), (790, 580), (1080, 700), (1080, 1350), (0, 1350)]
    d.polygon(ridge1, fill=(*mix(hill, top, .25), 230))
    ridge2 = [(0, 840), (190, 700), (360, 800), (560, 665), (760, 820), (930, 680), (1080, 760), (1080, 1350), (0, 1350)]
    d.polygon(ridge2, fill=(*hill, 245))

    # Foreground path
    d.polygon([(380, 1350), (700, 1350), (590, 900), (520, 900)], fill=(220, 177, 124, 75))
    # A small person silhouette looking toward sunrise
    d.ellipse((510, 760, 552, 802), fill=(18, 28, 35, 255))
    d.polygon([(508, 800), (553, 800), (570, 910), (490, 910)], fill=(18, 28, 35, 255))
    d.polygon([(500, 900), (520, 900), (506, 970), (485, 970)], fill=(18, 28, 35, 255))
    d.polygon([(540, 900), (559, 900), (575, 965), (555, 965)], fill=(18, 28, 35, 255))

    # Subtle vegetation silhouettes
    for i in range(18):
        x = random.randint(0, W)
        y = random.randint(860, 1280)
        h = random.randint(35, 115)
        d.line((x, y, x-12, y-h), fill=(13, 36, 37, 180), width=random.randint(3, 6))
        d.line((x-12, y-h+18, x-35, y-h+35), fill=(13, 36, 37, 160), width=3)
        d.line((x-12, y-h+27, x+10, y-h+43), fill=(13, 36, 37, 160), width=3)

    # Dark translucent lower panel keeps Hindi typography legible while retaining the scene.
    d.rounded_rectangle((52, 72, 1028, 625), radius=34, fill=(12, 22, 34, 158), outline=(255,255,255,48), width=2)
    centered(d, BRAND.upper(), 100, font(28, True), (245, 220, 175, 255))
    centered(d, post["title"], 165, font(56, True), (255, 255, 255, 255), spacing=16)
    d.line((390, 285, 690, 285), fill=(*sun, 220), width=4)
    centered(d, post["quote"], 325, font(43, True), (255, 239, 215, 255), spacing=22)
    centered(d, TAGLINE, 555, font(18, True), (255, 255, 255, 225))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "JPEG", quality=94, optimize=True, progressive=True)

def main():
    now = datetime.now(TZ)
    day = now.strftime("%Y-%m-%d")
    # One post per date; deterministic rotation avoids dependencies and API keys.
    post = POSTS[now.toordinal() % len(POSTS)]
    out_dir = OUT / day
    out_dir.mkdir(parents=True, exist_ok=True)
    image_path = out_dir / "jigyasa-post.jpg"
    make_art(post, image_path, now.toordinal())
    if not image_path.exists() or image_path.stat().st_size < 20000:
        raise RuntimeError("Image was not generated correctly.")
    metadata = {
        "date": day, "brand": BRAND, "topic": post["topic"], "title": post["title"],
        "caption": post["caption"], "hashtags": post["hashtags"],
        "image": str(image_path.relative_to(ROOT)),
        "generator": "Python + Pillow (free, no external image API)",
        "facebook_published": False
    }
    (out_dir / "post.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "caption.md").write_text(
        f"# {post['title']}\n\n{post['caption']}\n\n{post['hashtags']}\n\n"
        "_Generated automatically for review. Not published to Facebook._\n",
        encoding="utf-8"
    )
    print(f"Generated image: {image_path} ({image_path.stat().st_size} bytes)")
    print(f"Generated caption: {out_dir / 'caption.md'}")

if __name__ == "__main__":
    main()
