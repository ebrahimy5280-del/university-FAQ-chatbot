import os
import time
import requests
from dotenv import load_dotenv
from rag_engine import FAQChatbot


load_dotenv()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    print("❌ خطا: توکن TELEGRAM_TOKEN در فایل .env پیدا نشد!")
    print("لطفاً توکن ربات تلگرام خود را در فایل .env قرار دهید.")
    exit(1)


BASE_URL = f"https://long-pond-3b36.ebrahim-y5280.workers.dev/bot{TELEGRAM_TOKEN}"

print("🤖 در حال راه‌اندازی و اتصال ربات تلگرام به هوش مصنوعی...")
chatbot = FAQChatbot()
print("✅ ربات تلگرام با موفقیت به هوش مصنوعی متصل شد و روشن است!")

def send_chat_action(chat_id, action="typing"):
    """نمایش وضعیت 'در حال تایپ...' در تلگرام هنگام پردازش پاسخ توسط هوش مصنوعی"""
    url = f"{BASE_URL}/sendChatAction"
    payload = {"chat_id": chat_id, "action": action}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def send_message(chat_id, text):
    """ارسال پیام متنی به کاربر در تلگرام"""
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ خطا در ارسال پیام به تلگرام: {e}")

def get_updates(offset=None):
    """دریافت آخرین پیام‌های دریافتی از سرور تلگرام (روش Long Polling)"""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=15)
        return response.json()
    except Exception:
        
        return None

def main():
    last_update_id = None
    print("🚀 ربات آنلاین است و بدون نیاز به هیچ وی‌پی‌ان منتظر پیام کاربران می‌باشد...")
    
    while True:
        try:
            updates = get_updates(offset=last_update_id)
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    last_update_id = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_text = update["message"]["text"]
                        
                        print(f"📩 سوال جدید در تلگرام از کاربر ({chat_id}): {user_text}")
                        
                        
                        if user_text == "/start":
                            welcome_msg = (
                                "سلام! 🎓\n"
                                "من دستیار هوشمند قوانین آموزشی و آیین‌نامه‌های دانشگاه هستم.\n\n"
                                "سوال خود را بپرسید (مثلاً: شرایط مشروطی چیست؟ یا یک کد پایتون بنویس)..."
                            )
                            send_message(chat_id, welcome_msg)
                        else:
                            
                            send_chat_action(chat_id, "typing")
                            
                            
                            answer = chatbot.ask(user_text)
                            
                            
                            send_message(chat_id, answer)
            
        except Exception as e:
            print(f"⚠️ خطای غیرمنتظره در سیستم: {e}")
            time.sleep(2)
            
        time.sleep(1)

if __name__ == "__main__":
    main()