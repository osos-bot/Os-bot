import os
import requests
from flask import Flask, request

TOKEN = "8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk"
GEMINI_KEY = "AIzaSyDGMpZOBcP41JfkgYCYOAdtss69ioNqc4U"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is active and running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    
    # التأكد من أن التحديث يحتوي على رسالة نصية من المستخدم
    if update and "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_message = update["message"]["text"]
        
        try:
            # 1. إرسال رسالة المستخدم إلى جيميني
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': GEMINI_KEY
            }
            data = {
                "contents": [{"parts": [{"text": user_message}]}]
            }
            response = requests.post(GEMINI_URL, headers=headers, json=data)
            result = response.json()
            
            # 2. استخراج الرد من جيميني
            if 'candidates' in result:
                bot_reply = result['candidates'][0]['content']['parts'][0]['text']
            else:
                bot_reply = f"استجابة غير متوقعة من جيميني:\n{str(result)}"
                
        except Exception as e:
            bot_reply = f"خطأ في الاتصال بجيميني: {str(e)}"

        # 3. إرسال الرد إلى المستخدم في تليجرام مباشرة
        try:
            tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(tg_url, json={"chat_id": chat_id, "text": bot_reply})
        except Exception as e:
            print(f"Error sending to Telegram: {e}")

    return 'OK', 200

if __name__ == '__main__':
    # ربط الـ Webhook مع تليجرام تلقائياً عند التشغيل
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={render_url}/{TOKEN}"
        requests.get(set_url)
        
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
