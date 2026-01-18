import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd
from io import StringIO

# --- 1. 設定頁面 ---
st.set_page_config(page_title="AI 智能知識庫", page_icon="📂")

# --- 2. 讀取 API Key ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ 請先在 Streamlit Secrets 設定 GOOGLE_API_KEY")
    st.stop()

# --- 3. 檔案處理函數 ---
def extract_text(uploaded_file):
    """根據檔案類型讀取文字內容"""
    text = ""
    try:
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif uploaded_file.name.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            text = df.to_string()
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            text = df.to_string()
    except Exception as e:
        return f"讀取錯誤: {str(e)}"
    return text

# --- 4. 側邊欄：上傳資料區 ---
with st.sidebar:
    st.header("📂 知識庫管理")
    uploaded_file = st.file_uploader("上傳 Q&A 文件", type=["pdf", "txt", "csv", "xlsx"])
    
    # 狀態指示
    if uploaded_file:
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            with st.spinner("正在讀取文件..."):
                extracted_text = extract_text(uploaded_file)
                st.session_state.knowledge_base = extracted_text
                st.session_state.last_uploaded = uploaded_file.name
            st.success(f"✅ 已讀取：{uploaded_file.name}")
    else:
        st.info("請上傳檔案以啟用問答功能")
        st.session_state.knowledge_base = ""

# --- 5. 主介面：聊天區 ---
st.title("🤖 智能 Q&A 助手")

# 檢查是否有知識庫
if not st.session_state.knowledge_base:
    st.warning("👈 請先在左側上傳您的 Q&A 資料 (支援 PDF, Excel, Txt)")
else:
    # 設定 AI 模型
    sys_instruction = f"""
    你是一個專業的客服助手。請根據以下提供的「知識庫內容」回答使用者的問題。
    
    規則：
    1. 答案必須來自知識庫，嚴禁瞎掰。
    2. 如果知識庫沒有提到，請回答「不好意思，文件中沒有相關資訊」。
    3. 若是 Excel 表格數據，請精準回答數值。

    知識庫內容：
    {st.session_state.knowledge_base}
    """
    
    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash-lite",
        system_instruction=sys_instruction
    )

    # 顯示聊天紀錄
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 接收輸入
    if prompt := st.chat_input("請輸入您的問題..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 呼叫 AI
        try:
            response = model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            answer = f"⚠️ 發生錯誤，詳細原因：{str(e)}"

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})