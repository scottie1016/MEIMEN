import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import PyPDF2

# --- 1. 設定頁面 ---
st.set_page_config(page_title="AI 智能小幫手", page_icon="🤖")

# --- 2. 讀取 API Key ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ 請先在 Streamlit Secrets 設定 GOOGLE_API_KEY")
    st.stop()

# --- 3. 自動讀取 GitHub 上的知識庫檔案 ---
@st.cache_resource # 使用快取，避免每次有人問問題都要重新讀取檔案，速度會變快
def load_knowledge():
    """
    自動偵測並讀取目錄下的 knowledge 檔案
    優先順序: Excel -> Text -> PDF
    """
    text = ""
    try:
        if os.path.exists("knowledge.xlsx"):
            df = pd.read_excel("knowledge.xlsx")
            text = df.to_string()
        elif os.path.exists("knowledge.csv"):
            df = pd.read_csv("knowledge.csv")
            text = df.to_string()
        elif os.path.exists("knowledge.txt"):
            with open("knowledge.txt", "r", encoding="utf-8") as f:
                text = f.read()
        elif os.path.exists("knowledge.pdf"):
            reader = PyPDF2.PdfReader("knowledge.pdf")
            for page in reader.pages:
                text += page.extract_text() + "\n"
        else:
            return None # 找不到檔案
    except Exception as e:
        return f"Error: {str(e)}"
    return text

# 執行讀取
knowledge_base = load_knowledge()

# --- 4. 介面邏輯判斷 ---
if not knowledge_base:
    st.error("⚠️ 系統偵測不到知識庫檔案！")
    st.info("管理者請注意：請確保您已將 'knowledge.xlsx' 或 'knowledge.txt' 上傳至 GitHub 專案中。")
    st.stop()
elif knowledge_base.startswith("Error"):
    st.error(f"⚠️ 讀取檔案失敗：{knowledge_base}")
    st.stop()

# --- 5. 設定 AI 模型 ---
sys_instruction = f"""
你是一個親切的 AI 助手。請「嚴格根據」以下的資料內容回答使用者的問題。

規則：
1. 若答案在資料中，請清楚回答。
2. 若資料中沒有提到，請回答：「不好意思，這超出我的服務範圍，或資料庫中無相關資訊。」
3. 語氣保持禮貌、客觀。

資料內容：
{knowledge_base}
"""

# 嘗試建立模型 (這裡保留你之前測試成功的模型名稱)
# 如果你之前用 models/gemini-1.5-flash 成功，請保持不動
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash-lite", 
    system_instruction=sys_instruction
)

# --- 6. 聊天介面 (使用者只看得到這個) ---
st.title("🤖 專屬 AI 客服")
st.caption("您好，我是您的智能小幫手，請問有什麼想了解的嗎？")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("輸入您的問題..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = "⚠️ 系統連線忙碌中，請稍後再試。"

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})