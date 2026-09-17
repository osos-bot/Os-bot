import os
import requests
from flask import Flask, request

TOKEN = "8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk"

# Paste your OpenRouter API key here
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

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
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com",
                "X-Title": "Telegram Bot"
            }
            
            # Using Nex-N2.5-Pro (Free)
            data = {
                "model": "nex/nex-n2.5-pro:free",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                bot_reply = result['choices'][0]['message']['content']
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
