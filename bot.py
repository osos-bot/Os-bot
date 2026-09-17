import os
import requests
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv("8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk", "8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk")
OPENROUTER_API_KEY = os.getenv("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", "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")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Selected Free Models
MODEL_TEXT = "nvidia/nemotron-3-ultra-550b-a55b:free"
MODEL_VISION = "google/gemma-4-31b-it:free"
MODEL_AUDIO = "thinkingmachines/inkling:free"

def get_headers():
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY":
        raise ValueError("OPENROUTER_API_KEY is missing. Export it in your environment or set it directly in code.")
    
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "TelegramBot"
    }

# 1. Text & Chat Handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = {
        "model": MODEL_TEXT,
        "messages": [{"role": "user", "content": update.message.text}]
    }
    
    try:
        res = requests.post(OPENROUTER_URL, headers=get_headers(), json=payload)
        data = res.json()
        
        if res.status_code == 200:
            reply = data['choices'][0]['message']['content']
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text(f"API Error {res.status_code}: {data.get('error', {}).get('message')}")
    except Exception as e:
        await update.message.reply_text(f"System Error: {str(e)}")

# 2. Image Analysis Handler (Vision)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    base64_image = base64.b64encode(photo_bytes).decode('utf-8')
    caption = update.message.caption or "Describe this image in detail."

    payload = {
        "model": MODEL_VISION,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": caption},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]
    }
    
    try:
        res = requests.post(OPENROUTER_URL, headers=get_headers(), json=payload)
        data = res.json()
        
        if res.status_code == 200:
            reply = data['choices'][0]['message']['content']
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text(f"API Error {res.status_code}: {data.get('error', {}).get('message')}")
    except Exception as e:
        await update.message.reply_text(f"System Error: {str(e)}")

# 3. Audio & Voice Analysis Handler
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_file = await update.message.voice.get_file()
    voice_bytes = await voice_file.download_as_bytearray()
    base64_audio = base64.b64encode(voice_bytes).decode('utf-8')

    payload = {
        "model": MODEL_AUDIO,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Listen to this audio and transcribe or answer it."},
                    {
                        "type": "input_audio",
                        "input_audio": {"data": base64_audio, "format": "ogg"}
                    }
                ]
            }
        ]
    }

    try:
        res = requests.post(OPENROUTER_URL, headers=get_headers(), json=payload)
        data = res.json()

        if res.status_code == 200:
            reply = data['choices'][0]['message']['content']
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text(f"API Error {res.status_code}: {data.get('error', {}).get('message')}")
    except Exception as e:
        await update.message.reply_text(f"System Error: {str(e)}")

# 4. Image Generation Command (/generate <prompt>)
async def handle_generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Usage: /generate <image description>")
        return
        
    encoded_prompt = requests.utils.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    
    await update.message.reply_photo(photo=image_url, caption=f"Prompt: {prompt}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("generate", handle_generate_image))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print("Bot is active...")
    app.run_polling()
