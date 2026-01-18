import streamlit as st
import google.generativeai as genai
import google.generativeai.types as safety_types

st.title("🔧 系統診斷模式")

# 1. 檢查是否抓得到 API Key
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ 錯誤：找不到 API Key，請檢查 Streamlit Secrets 設定。")
    st.stop()
else:
    st.success(f"✅ API Key 讀取成功 (前五碼: {api_key[:5]}...)")

# 2. 設定 Key
genai.configure(api_key=api_key)

# 3. 嘗試列出所有可用模型
st.write("🔍 正在向 Google 查詢您的帳號可用模型...")

try:
    # 列出支援 generateContent 的模型
    model_list = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            model_list.append(m.name)
    
    if not model_list:
        st.error("❌ 錯誤：連線成功，但您的 API Key 權限似乎無法使用任何模型。")
        st.info("建議：請重新去 Google AI Studio 申請一個新的 API Key。")
    else:
        st.success(f"✅ 測試成功！您的帳號支援以下 {len(model_list)} 個模型：")
        # 顯示所有可用模型
        for model_name in model_list:
            st.code(model_name)
            
        st.info("請複製上方其中一個名稱 (例如 models/gemini-1.5-flash)，填回原本程式碼的 model_name 欄位。")

except Exception as e:
    st.error("❌ 發生嚴重錯誤 (通常是程式庫版本太舊导致)：")
    st.warning(f"錯誤訊息：{e}")
    st.markdown("---")
    st.subheader("💡 如何解決？")
    st.markdown("""
    如果這裡報錯，代表您的 `requirements.txt` 更新沒有成功。
    請確認 `requirements.txt` 內容必須包含版本號：
    **`google-generativeai>=0.7.2`**
    
    (修改完 requirements.txt 後，記得去 Streamlit 右上角選單按 **Reboot app**)
    """)