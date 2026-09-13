import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# التوكن والمفتاح الخاص بك (كما ظهر في الـ cURL)
TELEGRAM_TOKEN = "8622347113:AAFS2acI-kiIJvrGppytfJB2idJ2pXs9Cxk"
GEMINI_KEY = "AQ.Ab8RN6I5D9Wi9JuwptTzc0or8SHJOAQKcxcZjA-GhvCL9tk4qg"

# تم تعديل الرابط ليتطابق مع اسم النموذج الخاص بك 100%
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    processing_msg = await update.message.reply_text("أقرأ رسالتك...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': GEMINI_KEY
        }
        data = {
            "contents": [{
                "parts": [{"text": user_message}]
            }]
        }
        
        response = requests.post(URL, headers=headers, json=data)
        result = response.json()
        
        if 'candidates' in result:
            bot_reply = result['candidates'][0]['content']['parts'][0]['text']
            await processing_msg.edit_text(bot_reply)
        else:
            await processing_msg.edit_text(f"استجابة غير متوقعة:\n{result}")
            print(f"تفاصيل الخطأ: {result}")
            
    except Exception as e:
        await processing_msg.edit_text(f"حدث خطأ في الاتصال.")
        print(f"خطأ تقني: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    print("المساعد الذكي يعمل الآن... بانتظار رسائلك!")
    app.run_polling()

if __name__ == '__main__':
    main()
