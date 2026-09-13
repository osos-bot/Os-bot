import os
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

TOKEN = "8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk"
GEMINI_KEY = "AQ.Ab8RN6I5D9Wi9JuwptTzc0or8SHJOAQKcxcZjA-GhvCL9tk4qg"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route('/')
def index():
    return "Bot is active and running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_data = request.get_json()
    if json_data:
        update = Update.de_json(json_data, application.bot)
        asyncio.run(handle_message(update))
    return 'OK', 200

async def handle_message(update: Update):
    if update.message and update.message.text:
        user_message = update.message.text
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': GEMINI_KEY
            }
            data = {
                "contents": [{"parts": [{"text": user_message}]}]
            }
            response = requests.post(GEMINI_URL, headers=headers, json=data)
            result = response.json()
            
            if 'candidates' in result:
                bot_reply = result['candidates'][0]['content']['parts'][0]['text']
                await update.message.reply_text(bot_reply)
            else:
                await update.message.reply_text(f"استجابة غير متوقعة من السيرفر.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    # ربط الـ Webhook تلقائياً مع رابط منصة Render الخارجي
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={render_url}/{TOKEN}"
        requests.get(set_url)
        
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
