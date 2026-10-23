#!/usr/bin/env python3
"""Generate one free Jigyasa image locally with Pillow; no paid image API."""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image
from generate_post import create_image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "drafts" / "images"
POSTS = [
 {"topic":"मेहनत और उम्मीद","title":"छोटे कदम, बड़ी मंज़िल","quote":"धीरे चल रहे हैं तो\nरुक मत जाइए…","subquote":"छोटे कदम भी एक दिन\nबड़ी मंज़िल तक पहुँचाते हैं।","caption":"हर किसी की रफ़्तार अलग होती है। अपनी मेहनत पर भरोसा रखिए और रोज़ थोड़ा आगे बढ़ते रहिए। 🌱\n\nआप आज कौन-सा छोटा कदम उठाएँगे?","hashtags":"#Jigyasa #HindiThoughts #जीवनकीसीख #SelfGrowth #DailyMotivation"},
 {"topic":"रिश्तों की सच्चाई","title":"रिश्ते एहसास से चलते हैं","quote":"रिश्ते वक्त से नहीं,\nएहसास से चलते हैं…","subquote":"जहाँ परवाह सच्ची हो,\nवहाँ बहाने कम होते हैं।","caption":"रिश्तों में सबसे कीमती चीज़ सिर्फ़ साथ बिताया समय नहीं, बल्कि यह एहसास है कि कोई आपकी परवाह करता है। ❤️\n\nआपके लिए रिश्ते में सबसे ज़रूरी क्या है?","hashtags":"#Jigyasa #रिश्ते #HindiQuotes #LifeLessons #दिलकीबात"},
 {"topic":"आत्मसम्मान","title":"खुद को मत भूलिए","quote":"सबको खुश करते-करते\nखुद को मत भूलिए…","subquote":"आपका सुकून और\nआत्मसम्मान भी ज़रूरी है।","caption":"दूसरों की परवाह करना अच्छी बात है, लेकिन अपनी शांति और आत्मसम्मान का ख्याल रखना भी उतना ही ज़रूरी है। ❤️\n\nक्या आप खुद के लिए भी समय निकालते हैं?","hashtags":"#Jigyasa #आत्मसम्मान #HindiThoughts #SelfRespect #LifeLessons"},
 {"topic":"नई शुरुआत","title":"हर दिन एक नई शुरुआत","quote":"बीता हुआ कल सीख है,\nआज एक नया मौका…","subquote":"एक छोटा सही कदम\nनई राह बना सकता है।","caption":"ज़िंदगी में सब कुछ एक दिन में नहीं बदलता, लेकिन एक छोटा-सा सही कदम नई शुरुआत बन सकता है। 🌅\n\nआज आप कौन-सी अच्छी आदत अपनाएँगे?","hashtags":"#Jigyasa #नईशुरुआत #PositiveThinking #HindiMotivation #जीवनकीसीख"},
 {"topic":"सच्चाई और व्यवहार","title":"पहचान व्यवहार से होती है","quote":"बातों से नहीं,\nव्यवहार से पहचानिए…","subquote":"मुश्किल वक्त में ही\nरिश्तों की सच्चाई दिखती है।","caption":"अच्छी बातें कहना आसान है, लेकिन मुश्किल समय में साथ देना असली पहचान है।\n\nआपके हिसाब से इंसान की पहचान किससे होती है?","hashtags":"#Jigyasa #सच्चीबात #HindiThoughts #LifeLessons #रिश्ते"},
]
def main():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    day = now.date().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    post = dict(POSTS[now.timetuple().tm_yday % len(POSTS)])
    post.update({"date":day,"brand":"Jigyasa","language":"Hindi","generator":"local-python-pillow"})
    image_path = OUT / f"{day}-jigyasa.jpg"
    create_image(post, image_path)
    if not image_path.is_file() or image_path.stat().st_size < 10000:
        raise RuntimeError(f"Missing or too-small image: {image_path}")
    with Image.open(image_path) as image: image.verify()
    post["image"] = str(image_path.relative_to(ROOT))
    (OUT / f"{day}-jigyasa.json").write_text(json.dumps(post,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Verified image: {post['image']} ({image_path.stat().st_size} bytes)")
if __name__ == "__main__": main()
