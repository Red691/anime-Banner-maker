

import os
import json
import requests
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message

#===================== ENV BASED CONFIG (HEROKU READY) =====================

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN") # <-- your bot token

BASE_DIR = "data" TEMPLATE_DIR = "templates" FONT_DIR = "fonts"

os.makedirs(BASE_DIR, exist_ok=True) os.makedirs(TEMPLATE_DIR, exist_ok=True) os.makedirs(FONT_DIR, exist_ok=True)

USERS_FILE = f"{BASE_DIR}/users.json" SETTINGS_FILE = f"{BASE_DIR}/settings.json"

if not os.path.exists(USERS_FILE): json.dump({"authorized": []}, open(USERS_FILE, "w"))

if not os.path.exists(SETTINGS_FILE): json.dump({ "watermark": "@Anime_Sensei_Official", "blur": 7, "text_color": "white", "font": "default.ttf" }, open(SETTINGS_FILE, "w"))

#===================== BOT =====================

bot = Client("anime_banner_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

#===================== HELPERS =====================

def is_authorized(user_id): users = json.load(open(USERS_FILE)) return user_id in users["authorized"]

def anime_search(name): url = f"https://api.jikan.moe/v4/anime?q={name}&limit=1" r = requests.get(url).json() if not r.get("data"): return None return r["data"][0]

#===================== BANNER GENERATOR =====================

def create_banner(anime): bg = Image.new("RGB", (1280, 720), "black")

poster_url = anime["images"]["jpg"]["large_image_url"]
poster = Image.open(requests.get(poster_url, stream=True).raw).resize((1280, 720))

img = np.array(poster)
img = cv2.GaussianBlur(img, (15, 15), 0)
bg = Image.fromarray(img)

draw = ImageDraw.Draw(bg)
font_title = ImageFont.truetype(f"{FONT_DIR}/default.ttf", 60)
font_desc = ImageFont.truetype(f"{FONT_DIR}/default.ttf", 28)

title = anime["title"]
desc = anime["synopsis"][:300] + "..."
genres = ", ".join([g["name"] for g in anime["genres"]])

draw.text((60, 80), title, fill="white", font=font_title)
draw.text((60, 170), genres, fill="orange", font=font_desc)
draw.text((60, 230), desc, fill="white", font=font_desc)

watermark = json.load(open(SETTINGS_FILE))["watermark"]
draw.text((1000, 680), watermark, fill="white", font=font_desc)

output = "banner.jpg"
bg.save(output)
return output

#===================== COMMANDS =====================

@bot.on_message(filters.command("start")) def start(_, m: Message): m.reply("🎨 Anime Banner Maker Bot\n\nSend anime name to create banner")

@bot.on_message(filters.text & ~filters.command) def generate(_, m: Message): anime = anime_search(m.text) if not anime: return m.reply("❌ Anime not found")

banner = create_banner(anime)
m.reply_photo(banner, caption=f"✅ Banner created for **{anime['title']}**")

#===================== RUN =====================

bot.run()
