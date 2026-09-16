import os
import requests
from flask import Flask, request

TOKEN = "8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk"
# Your new AIza key
GEMINI_KEY = "AIzaSyCySeXRK2jFm-foUsdFNLbIhVQCJ0ok49A"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is active and running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    
    if update and "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_message = update["message"]["text"]
        
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
            else:
                bot_reply = f"Unexpected response:\n{str(result)}"
                
        except Exception as e:
            bot_reply = f"Connection error: {str(e)}"

        try:
            tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(tg_url, json={"chat_id": chat_id, "text": bot_reply})
        except Exception as e:
            print(f"Error sending to Telegram: {e}")

    return 'OK', 200

if __name__ == '__main__':
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={render_url}/{TOKEN}"
        requests.get(set_url)
        
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
