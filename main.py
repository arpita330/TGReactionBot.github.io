# ✅ Serverless Auto Reaction Bot with JSON Storage
# Requirements: pyrogram, tgcrypto

import json
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os

# 🔧 Configuration from Environment
CONFIG = {
    "API_ID": int(os.getenv("API_ID")),
    "API_HASH": os.getenv("API_HASH"),
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "ADMIN_ID": int(os.getenv("ADMIN_ID")),
    "UPI_ID": os.getenv("UPI_ID"),
    "REQUIRED_CHANNELS": [
        "arpita_Official_on_top",
        "arpita_official_chat",
        "arpita_official_backup",
        "+UzJ4zBYyEP0zZmI9",
        "+s29DWF1HTndiNzJl"
    ]
}

USERS_FILE = "users.json"
EMOJIS = ["⭐️", "👍", "❤", "🔥", "🥰", "👏", "😁", "🎉", "🤩", "🙏", "👌", "🕊", "😍", "🐳", "💯", "⚡", "🏆"]

# 🔄 Load & Save Users
def load_users():
    try:
        with open(USERS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# 🚀 Bot Initialization
app = Client("reaction_bot",
             api_id=CONFIG["API_ID"],
             api_hash=CONFIG["API_HASH"],
             bot_token=CONFIG["BOT_TOKEN"])

# ✅ Channel Membership Check
async def check_channel_membership(user_id):
    missing = []
    for channel in CONFIG["REQUIRED_CHANNELS"]:
        try:
            member = await app.get_chat_member(channel, user_id)
            if member.status not in ["member", "creator", "administrator"]:
                missing.append(channel)
        except:
            missing.append(channel)
    return missing

# 📌 /start Command
@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user_id = str(message.from_user.id)
    users.setdefault(user_id, {"paid": False})
    save_users(users)

    missing = await check_channel_membership(message.from_user.id)
    if missing:
        buttons = [
            [InlineKeyboardButton(f"Join @{ch.replace('+', '')}", url=f"https://t.me/{ch.replace('+', '')}")]
            for ch in missing
        ]
        buttons.append([InlineKeyboardButton("🟢 Joined", callback_data="check_join")])
        await message.reply("🔐 Please join all required channels:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await send_payment_info(message)

# 🔁 Join Check Button
@app.on_callback_query(filters.regex("check_join"))
async def check_join_callback(client, callback):
    user_id = str(callback.from_user.id)
    missing = await check_channel_membership(callback.from_user.id)
    if not missing:
        await callback.message.delete()
        await send_payment_info(callback.message)
    else:
        await callback.answer("You haven't joined all channels!", show_alert=True)

# 💳 Payment Prompt
async def send_payment_info(message):
    user_id = str(message.from_user.id)
    if not users[user_id].get("paid"):
        await message.reply(
            f"✅ You've joined all channels!\n💰 Please send ₹25 to UPI: `{CONFIG['UPI_ID']}`\n📸 Then send a screenshot for manual verification.",
            quote=True
        )
    else:
        await send_final_message(message)

# 🤖 Final Welcome Message
async def send_final_message(message):
    await message.reply(
        "👋 Hello there! I'm Free Auto Reaction Bot 🤖\n\n"
        "✨ I add fun emoji reactions directly to your posts and messages! 😄\n\n"
        "👉 Simply add me to your channel or group to get started!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add to Channel", url="https://t.me/YourBotUsername?startchannel=true")],
            [InlineKeyboardButton("➕ Add to Group", url="https://t.me/YourBotUsername?startgroup=true")]
        ])
    )

# 🧾 Handle Screenshot
@app.on_message(filters.photo & filters.private)
async def handle_screenshot(client, message: Message):
    user_id = str(message.from_user.id)
    if not users[user_id].get("paid"):
        await app.send_message(CONFIG["ADMIN_ID"],
                               f"🧾 Payment proof received from [{message.from_user.first_name}](tg://user?id={user_id})",
                               reply_to_message_id=message.id)
        await message.reply("🕐 Waiting for admin to verify...")

# ✅ Admin Verify Command
@app.on_message(filters.command("verify") & filters.user(CONFIG["ADMIN_ID"]))
async def verify_user(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /verify user_id")
    uid = message.command[1]
    if uid in users:
        users[uid]["paid"] = True
        save_users(users)
        await app.send_message(int(uid), "✅ Your payment has been verified!")
        await send_final_message(await app.get_messages(int(uid), 1))
        await message.reply("User verified successfully.")
    else:
        await message.reply("User ID not found.")

# 🔁 React to Channel Posts
@app.on_message(filters.channel)
async def react_to_posts(client, message: Message):
    for emoji in EMOJIS:
        try:
            await app.send_reaction(message.chat.id, message.id, emoji)
            await asyncio.sleep(0.2)
        except:
            continue

# ▶️ Run the Bot
app.run()
