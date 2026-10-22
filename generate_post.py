#!/usr/bin/env python3
"""Create a free Hindi knowledge-card image for Jigyasa using Pillow."""
import argparse
import json
import os
import random
from io import BytesIO
from urllib.parse import quote

import requests
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo("Asia/Kolkata")
W, H = 1080, 1350
SLOTS = ["07:00", "10:00", "13:30", "20:30"]

FACTS = [
 {"topic":"मानव शरीर","title":"आपका दिल एक दिन में","body":"लगभग 1 लाख बार धड़कता है।\nयह लगातार शरीर तक खून पहुँचाता है।","caption":"क्या आपको पता था? हमारा दिल बिना रुके दिन-रात काम करता है। ऐसी ही विज्ञान की रोचक बातें जानने के लिए Jigyasa को फॉलो करें। #Jigyasa #HumanBody #ScienceFacts"},
 {"topic":"दिमाग","title":"दिमाग और नींद","body":"नींद के दौरान भी दिमाग सक्रिय रहता है।\nयह यादों को व्यवस्थित करने में मदद करता है।","caption":"सोते समय भी दिमाग अपना काम करता रहता है! नींद सीखने और याददाश्त के लिए अहम है। #Jigyasa #BrainFacts #HindiFacts"},
 {"topic":"अंतरिक्ष","title":"अंतरिक्ष में आवाज़?","body":"ध्वनि को फैलने के लिए माध्यम चाहिए।\nखाली अंतरिक्ष में आवाज़ सामान्य तरह नहीं चलती।","caption":"अंतरिक्ष फिल्मों जैसा नहीं होता! ध्वनि को हवा या किसी माध्यम की जरूरत होती है। #Jigyasa #SpaceFacts #Science"},
 {"topic":"पौधे","title":"पौधे भी करते हैं भोजन","body":"प्रकाश संश्लेषण में पौधे रोशनी की मदद से\nपानी और कार्बन डाइऑक्साइड से भोजन बनाते हैं।","caption":"हरे पौधे प्रकृति की कमाल की रसोई हैं। वे प्रकाश संश्लेषण से अपना भोजन बनाते हैं। #Jigyasa #Nature #ScienceFacts"},
 {"topic":"जानवर","title":"ऑक्टोपस की खासियत","body":"ऑक्टोपस के तीन दिल होते हैं।\nउसका खून नीला दिखाई देता है।","caption":"समुद्र की दुनिया कितनी अद्भुत है! ऑक्टोपस के तीन दिल होते हैं। #Jigyasa #AnimalFacts #Ocean"},
 {"topic":"मनोविज्ञान","title":"दिमाग ध्यान कहाँ देता है?","body":"नई या अचानक हुई चीज़ें\nअक्सर हमारा ध्यान जल्दी खींचती हैं।","caption":"हमारा ध्यान हर चीज़ पर बराबर नहीं जाता। नई और अचानक दिखने वाली चीज़ें अक्सर ध्यान खींचती हैं। #Jigyasa #Psychology #MindFacts"},
 {"topic":"भौतिकी","title":"आसमान नीला क्यों?","body":"वायुमंडल हवा के अणुओं से नीली रोशनी\nदूसरे रंगों की तुलना में अधिक बिखेरता है।","caption":"आसमान का नीला रंग प्रकाश के बिखरने से जुड़ा है। विज्ञान रोज़मर्रा में हर जगह है। #Jigyasa #Physics #ScienceFacts"},
 {"topic":"तकनीक","title":"QR कोड कैसे काम करता है?","body":"काले-सफेद पैटर्न में जानकारी एन्कोड होती है।\nकैमरा उसे पढ़कर डेटा तक पहुँचाता है।","caption":"एक छोटा-सा QR कोड जानकारी को पैटर्न में रख सकता है। #Jigyasa #Technology #DigitalIndia"},
 {"topic":"जेनेटिक्स","title":"DNA में क्या है?","body":"DNA में जीव के विकास और कामकाज से जुड़ी\nआनुवंशिक जानकारी होती है।","caption":"DNA जीवन की आनुवंशिक जानकारी सँभालने वाला अणु है। #Jigyasa #Genetics #Biology"},
 {"topic":"इतिहास","title":"कागज़ की शुरुआत","body":"कागज़ बनाने की शुरुआती तकनीक\nप्राचीन चीन में विकसित हुई थी।","caption":"कागज़ ने ज्ञान को लिखने और बाँटने का तरीका बदल दिया। #Jigyasa #History #Inventions"},
 {"topic":"पृथ्वी","title":"मिट्टी में जीवन","body":"मिट्टी में बैक्टीरिया, फंगस और कई छोटे जीव\nपोषक तत्वों के चक्र में मदद करते हैं।","caption":"मिट्टी सिर्फ धूल नहीं—यह जीवन से भरा एक छोटा संसार है। #Jigyasa #Environment #Nature"},
 {"topic":"मानव शरीर","title":"त्वचा शरीर की ढाल","body":"त्वचा शरीर को बाहरी वातावरण से बचाने\nऔर तापमान नियंत्रित करने में मदद करती है।","caption":"हमारी त्वचा शरीर की सुरक्षा में अहम भूमिका निभाती है। #Jigyasa #HumanBody #Biology"},
 {"topic":"पशु व्यवहार","title":"मधुमक्खियों का संदेश","body":"मधुमक्खियाँ खास तरह के नृत्य से\nदूसरी मधुमक्खियों को भोजन की दिशा बताती हैं।","caption":"मधुमक्खियों का वैगल डांस संवाद का अद्भुत तरीका है। #Jigyasa #AnimalBehaviour #Nature"},
 {"topic":"समुद्र","title":"समुद्र का नमक","body":"समुद्र के पानी में घुले हुए लवण होते हैं।\nनदियाँ चट्टानों से खनिज बहाकर लाती हैं।","caption":"समुद्र का खारापन लंबे समय में प्राकृतिक प्रक्रियाओं से बना है। #Jigyasa #Ocean #Science"},
 {"topic":"रोज़मर्रा का विज्ञान","title":"फ्रिज खाना ठंडा कैसे रखता है?","body":"फ्रिज अंदर की गर्मी बाहर निकालता है।\nइसलिए अंदर का तापमान कम रहता है।","caption":"फ्रिज ठंड पैदा करने से ज्यादा अंदर की गर्मी बाहर निकालता है। #Jigyasa #EverydayScience #Technology"},
 {"topic":"विकास","title":"जीव बदलते रहते हैं","body":"पीढ़ियों में आबादी के आनुवंशिक गुण बदल सकते हैं।\nइसे विकास की प्रक्रिया कहते हैं।","caption":"विकास पीढ़ियों में आबादी के आनुवंशिक गुणों में बदलाव की प्रक्रिया है। #Jigyasa #Evolution #Biology"},
]

PALETTES = [
 ((12, 35, 75), (20, 135, 155)), ((42, 25, 80), (165, 65, 125)),
 ((12, 65, 65), (65, 145, 95)), ((70, 35, 25), (200, 115, 45)),
 ((25, 40, 95), (80, 110, 190)), ((60, 25, 75), (130, 85, 170)),
]

def font(size, bold=False, latin=False):
    if latin:
        paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    else:
        paths = [
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Regular.ttf",
        ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)

def wrap(draw, text, fnt, max_width):
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = word if not line else line + " " + word
            if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines

def draw_wrapped(draw, text, xy, fnt, fill, max_width, line_height):
    x, y = xy
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y

def make_ai_background(fact, seed):
    """Try Pollinations' image API; only spend the account's available pollen."""
    api_key = os.environ.get("POLLINATIONS_API_KEY", "").strip()
    if not api_key:
        return None

    prompt = (
        "Premium editorial science-education illustration. Subject: " + fact["topic"] +
        ", concept: " + fact["title"] + ". Visually rich, cinematic lighting, "
        "intricate details, sophisticated deep navy and teal palette with warm "
        "golden highlights, polished magazine art direction, portrait 4:5 composition. "
        "Keep central-left area dark and uncluttered for Hindi text overlay. "
        "No words, letters, typography, logos, or watermark."
    )
    url = "https://gen.pollinations.ai/image/" + quote(prompt, safe="")
    try:
        response = requests.get(
            url,
            params={"model": "flux", "width": 1024, "height": 1280, "seed": seed},
            headers={"Authorization": f"Bearer {api_key}", "Accept": "image/*"},
            timeout=90,
        )
        response.raise_for_status()
        candidate = Image.open(BytesIO(response.content)).convert("RGB")
        scale = max(W / candidate.width, H / candidate.height)
        candidate = candidate.resize(
            (int(candidate.width * scale), int(candidate.height * scale)),
            Image.Resampling.LANCZOS,
        )
        left = (candidate.width - W) // 2
        top = (candidate.height - H) // 2
        print("AI background generated with Pollinations (flux).")
        return candidate.crop((left, top, left + W, top + H))
    except Exception as exc:
        print(f"AI generation unavailable; using local background ({type(exc).__name__}).")
        return None


def render(fact, output, seed):
    rng = random.Random(seed)
    c1, c2 = rng.choice(PALETTES)
    im = make_ai_background(fact, seed)
    if im is None:
        im = Image.new("RGB", (W, H))
        pix = im.load()
        for y in range(H):
            t = y / (H - 1)
            for x in range(W):
                dx, dy = (x - W*.78)/(W*.95), (y-H*.18)/(H*.65)
                glow = max(0, 1 - (dx*dx + dy*dy)**.5)
                pix[x, y] = tuple(min(255, int(c1[i]*(1-t)+c2[i]*t + glow*12)) for i in range(3))
    d = ImageDraw.Draw(im)
    # Header is high contrast: no white-on-white logo pill.
    d.rounded_rectangle((64, 62, 490, 136), radius=28, fill=(7, 20, 48), outline=(255, 225, 150), width=2)
    d.text((88, 82), "JIGYASA", font=font(32, True, latin=True), fill=(255, 225, 150))
    d.text((260, 88), "जानिए कुछ नया", font=font(24, True), fill=(255, 255, 255))
    for r in (115, 165, 215):
        d.ellipse((W-220-r, 185-r, W-220+r, 185+r), outline=(255,255,255,90), width=3)
    d.text((70, 235), fact["topic"], font=font(30, True), fill=(255,225,150))
    y = draw_wrapped(d, fact["title"], (68, 315), font(62, True), "white", 900, 84)
    d.rounded_rectangle((68, y+28, 1012, y+33), radius=3, fill=(255,255,255,190))
    y = draw_wrapped(d, fact["body"], (72, y+75), font(37), (246,248,255), 900, 66)
    # Keep body clear of footer even if title wraps to multiple lines.
    d.rounded_rectangle((68, 1110, 1012, 1260), radius=28, fill=(8, 15, 35), outline=(255,225,150), width=2)
    d.text((100, 1140), "ऐसी और रोचक बातें के लिए", font=font(28), fill="white")
    d.text((100, 1190), "FOLLOW @JIGYASA", font=font(32, True, latin=True), fill=(255,225,150))
    d.text((70, 1300), "सीखें  |  सोचें  |  सवाल पूछें", font=font(23), fill=(255,255,255))
    output.parent.mkdir(parents=True, exist_ok=True)
    im.save(output, format="JPEG", quality=92, optimize=True, progressive=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", choices=SLOTS, required=True)
    args = parser.parse_args()
    today = datetime.now(TZ).date().isoformat()
    slot_index = SLOTS.index(args.slot)
    day_number = datetime.now(TZ).date().toordinal()
    start = (day_number * 3) % len(FACTS)
    chosen = FACTS[(start + slot_index * 5) % len(FACTS)]
    out_dir = ROOT / "content" / today
    image_rel = f"content/{today}/{args.slot.replace(':','-')}.jpg"
    image_path = ROOT / image_rel
    render(chosen, image_path, day_number * 10 + slot_index)
    post = {"caption": chosen["caption"], "image": image_rel, "topic": chosen["topic"], "title": chosen["title"], "date": today, "slot": args.slot}
    json_path = out_dir / f"{args.slot.replace(':','-')}.json"
    json_path.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {json_path} and {image_path} ({chosen['topic']}: {chosen['title']})")

if __name__ == "__main__":
    main()
