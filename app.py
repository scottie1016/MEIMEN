import streamlit as st
import google.generativeai as genai

# --- 1. 設定頁面配置 ---
st.set_page_config(page_title="我的 Q&A 助手", page_icon="🤖")

# --- 2. 讀取 API Key (從 Streamlit Secrets 安全讀取) ---
# 注意：本機測試時，若沒有設定 secrets，會報錯。建議直接部署到 Streamlit Cloud 設定。
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("找不到 API Key，請檢查 Streamlit 的 Secrets 設定。")
    st.stop()

# --- 3. 定義你的 Q&A 資料 (知識庫) ---
# 技巧：如果是簡單的問答，直接貼在這裡最快。
# 如果資料超過 50 題，建議另外用讀取 txt 檔案的方式。
qa_knowledge_base = """
Q: 公司的營業時間是幾點？
A: 我們週一至週五早上 9:00 到下午 6:00 營業，國定假日休息。

Q: 商品可以退貨嗎？
A: 是的，購買後 7 天內保持包裝完整皆可退貨。請聯繫客服信箱 service@example.com。

Q: 你們有提供海外運送嗎？
A: 目前僅提供台灣本島與離島的運送服務，海外暫未開放。

(請在此處繼續貼上您收集好的 Q&A...)
"""

# --- 4. 設定 AI 模型與系統指令 ---
# 使用 gemini-1.5-flash，速度快且免費額度高
sys_instruction = f"""
你是一個專業的問答助手。你的任務是「嚴格根據」以下的資料庫回答使用者的問題。

規則：
1. 只能使用資料庫內的資訊，不要自己編造或聯網搜尋。
2. 如果使用者的問題在資料庫中找不到答案，請直接回答：「不好意思，目前的資料庫中沒有相關資訊，建議您直接聯繫人工客服。」
3. 回答要親切、簡潔。

資料庫內容：
{qa_knowledge_base}
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=sys_instruction
)

# --- 5. 建立聊天介面 ---
st.title("🤖 專屬 Q&A 知識庫")
st.caption("請輸入問題，我會根據已有的資料庫回答您。")

# 初始化聊天紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示過去的對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 接收使用者輸入
if prompt := st.chat_input("請問有什麼我可以幫您的？"):
    # 1. 顯示使用者問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 呼叫 Gemini 生成回答
    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = "系統忙碌中，請稍後再試。"
    
    # 3. 顯示 AI 回答
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})