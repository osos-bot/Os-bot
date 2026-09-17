import os
import requests
import base64
from flask import Flask, request

TOKEN = "8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk"

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_STT_URL = "https://openrouter.ai/api/v1/audio/transcriptions"

app = Flask(__name__)

def fetch_telegram_file_bytes(file_id):
    """Retrieves file path from Telegram and downloads raw file bytes."""
    file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
    if file_info.get("ok"):
        file_path = file_info["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        response = requests.get(download_url)
        return response.content
    return None

@app.route('/')
def index():
    return "Bot is active and running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    
    if update and "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        bot_reply = ""

        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com",
                "X-Title": "Telegram Bot"
            }

            # 1. TEXT MESSAGES
            if "text" in message:
                user_text = message["text"]
                data = {
                    "model": "nex-agi/nex-n2.5-pro:free",
                    "messages": [{"role": "user", "content": user_text}]
                }
                res = requests.post(OPENROUTER_CHAT_URL, headers=headers, json=data).json()
                bot_reply = res.get('choices', [{}])[0].get('message', {}).get('content', str(res))

            # 2. IMAGE / PHOTO PROCESSING
            elif "photo" in message:
                caption = message.get("caption", "Describe what is in this image.")
                file_id = message["photo"][-1]["file_id"]  # Select highest resolution image
                file_bytes = fetch_telegram_file_bytes(file_id)
                
                if file_bytes:
                    base64_img = base64.b64encode(file_bytes).decode('utf-8')
                    image_uri = f"data:image/jpeg;base64,{base64_img}"

                    data = {
                        "model": "google/gemini-2.0-flash-exp:free",  # Multimodal vision model
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": caption},
                                    {"type": "image_url", "image_url": {"url": image_uri}}
                                ]
                            }
                        ]
                    }
                    res = requests.post(OPENROUTER_CHAT_URL, headers=headers, json=data).json()
                    bot_reply = res.get('choices', [{}])[0].get('message', {}).get('content', str(res))
                else:
                    bot_reply = "Could not download image from Telegram."

            # 3. VOICE NOTE / AUDIO PROCESSING
            elif "voice" in message or "audio" in message:
                voice_obj = message.get("voice") or message.get("audio")
                file_id = voice_obj["file_id"]
                file_bytes = fetch_telegram_file_bytes(file_id)

                if file_bytes:
                    raw_base64_audio = base64.b64encode(file_bytes).decode('utf-8')
                    
                    # Transcribe voice to text via Whisper
                    stt_payload = {
                        "model": "openai/whisper-large-v3:free",
                        "input_audio": {
                            "data": raw_base64_audio,
                            "format": "ogg"
                        }
                    }
                    stt_res = requests.post(OPENROUTER_STT_URL, headers=headers, json=stt_payload).json()
                    transcript = stt_res.get("text", "")

                    if transcript:
                        # Process transcribed text through AI model
                        chat_data = {
                            "model": "nex-agi/nex-n2.5-pro:free",
                            "messages": [{"role": "user", "content": transcript}]
                        }
                        res = requests.post(OPENROUTER_CHAT_URL, headers=headers, json=chat_data).json()
                        ai_answer = res.get('choices', [{}])[0].get('message', {}).get('content', str(res))
                        bot_reply = f"🎤 *Transcript:* \"{transcript}\"\n\n🤖 *AI:* {ai_answer}"
                    else:
                        bot_reply = f"Voice transcription failed:\n{str(stt_res)}"
                else:
                    bot_reply = "Could not download voice note from Telegram."

        except Exception as e:
            bot_reply = f"Processing error: {str(e)}"

        if bot_reply:
            tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(tg_url, json={"chat_id": chat_id, "text": bot_reply})

    return 'OK', 200

if __name__ == '__main__':
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={render_url}/{TOKEN}"
        requests.get(set_url)
        
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
