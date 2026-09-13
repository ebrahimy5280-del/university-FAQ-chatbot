import os
import json
import streamlit as st
from datetime import datetime
from rag_engine import FAQChatbot


st.set_page_config(
    page_title="پورتال هوشمند دانشگاه",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


custom_css = """
<style>
    
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');

    
    html, body, p, h1, h2, h3, h4, h5, h6, label, textarea, input, button, .stMarkdown {
        font-family: 'Vazirmatn', sans-serif !important;
    }

    
    [data-testid="stHeader"],
    [data-testid="stSidebarHeader"] {
        direction: ltr !important;
        text-align: left !important;
    }

    [data-testid="stSidebarHeader"] * {
        direction: ltr !important;
    }

    
    h1, .stApp h1, p, label, .stMarkdown, .stCaption {
        direction: rtl !important;
        text-align: right !important;
    }

    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        text-align: center !important;
        direction: rtl !important;
    }


    [data-testid="stSidebarUserContent"] {
        direction: rtl !important;
        text-align: right !important;
    }

    
    .stChatMessage {
        direction: rtl !important;
        text-align: right !important;
    }

    .stChatMessage p, .stChatMessage div {
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 1.15rem !important;  
        line-height: 1.9 !important;    
        direction: rtl !important;
        text-align: right !important;
    }

    
    .stChatInput textarea {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 1.1rem !important;
    }

    
    .stButton>button {
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "سلام! من دستیار هوشمند قوانین آموزشی دانشگاه هستم. چه سوالی داری؟"}
    ]


def auto_save_chat():
    """ذخیره‌سازی خودکار چت در پوشه chat_logs"""
    os.makedirs("chat_logs", exist_ok=True)
    filepath = f"chat_logs/chat_{st.session_state.session_id}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)

def get_saved_chats_list():
    """دریافت لیست چت‌های ذخیره‌شده همراه با عنوان و اولین سوال"""
    if not os.path.exists("chat_logs"):
        return []
    
    files = [f for f in os.listdir("chat_logs") if f.endswith(".json")]
    files.sort(reverse=True)
    
    chats = []
    for file in files:
        filepath = os.path.join("chat_logs", file)
        session_id = file.replace("chat_", "").replace(".json", "")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                messages = json.load(f)
            
            first_question = "گفتگوی جدید"
            for msg in messages:
                if msg["role"] == "user":
                    first_question = msg["content"][:25] + "..." if len(msg["content"]) > 25 else msg["content"]
                    break
            
            title = f"📅 {session_id.split('_')[0]} | {first_question}"
            chats.append({"file": file, "session_id": session_id, "title": title, "messages": messages})
        except Exception:
            pass
            
    return chats


with st.sidebar:
    st.title("🎓 پورتال جامع دانشگاه")
    
    
    if st.button("➕ چت جدید (شروع گفتگو تازه)", use_container_width=True, type="primary"):
        st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        st.session_state.messages = [
            {"role": "assistant", "content": "سلام! من دستیار هوشمند شما هستم. چه سوالی داری؟"}
        ]
        st.rerun()

    st.markdown("---")
    
    
    st.subheader("📜 چت‌های قبلی شما")
    saved_chats = get_saved_chats_list()
    
    if saved_chats:
        chat_options = {c["title"]: c for c in saved_chats}
        
        selected_title = st.selectbox(
            "یک چت را انتخاب کنید:",
            options=["-- انتخاب چت --"] + list(chat_options.keys()),
            key="chat_selector"
        )
        
        if selected_title != "-- انتخاب چت --":
            selected_chat = chat_options[selected_title]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📂 باز کردن", use_container_width=True):
                    st.session_state.messages = selected_chat["messages"]
                    st.session_state.session_id = selected_chat["session_id"]
                    st.rerun()
                    
            with col2:
                if st.button("🗑️ حذف چت", use_container_width=True):
                    filepath = os.path.join("chat_logs", selected_chat["file"])
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    
                    if st.session_state.session_id == selected_chat["session_id"]:
                        st.session_state.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        st.session_state.messages = [
                            {"role": "assistant", "content": "سلام! من دستیار هوشمند شما هستم. چه سوالی داری؟"}
                        ]
                    st.toast("🗑️ چت با موفقیت حذف شد.")
                    st.rerun()
    else:
        st.info("هنوز چتی ذخیره نشده است.")

    st.markdown("---")
    
    
    st.subheader("📱 سایر پلتفرم‌ها")
    st.link_button("✈️ ورود به ربات تلگرام", "https://t.me/Diaco_Uni_FAQ_Bot", use_container_width=True)
    st.markdown("🆔 آیدی جهت سرچ در تلگرام: **`@Diaco_Uni_FAQ_Bot`**")
    
    st.markdown("---")
    st.link_button("🔗 مستندات API", "http://localhost:8000/docs", use_container_width=True)


st.title("💬 دستیار هوشمند قوانین آموزشی دانشگاه")
st.caption("پاسخگویی آنی به سوالات آیین‌نامه طبق استانداردهای رسمی وزارت علوم")

@st.cache_resource
def load_chatbot():
    return FAQChatbot()

try:
    chatbot = load_chatbot()
except Exception as e:
    st.error(f"خطا در راه‌اندازی هوش مصنوعی: {e}")
    st.stop()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if user_input := st.chat_input("سوال خود را بنویسید (مثلاً: شرایط مشروطی یا حذف اضطراری چیست؟)..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("در حال کاوش در آیین‌نامه‌ها..."):
            response = chatbot.ask(user_input)
            st.write(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    auto_save_chat()