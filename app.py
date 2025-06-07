import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from crawler import get_horoscope_by_name
from message_generator import build_star_menu, build_horoscope_card, build_mode_menu

# ✅ 載入 .env 並設置 Gemini 模型
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# ✅ 初始化 LINE Bot
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

app = Flask(__name__)
user_state = {}

@app.route("/", methods=['GET'])
def home():
    return "Horoscope Bot is running."

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    print("🟡 收到 LINE 請求")
    print("🟡 Signature:", signature)
    print("🟡 Body:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ 簽名驗證失敗")
        abort(400)
    except Exception as e:
        print("❌ 發生例外錯誤：", str(e))
        abort(500)

    return 'OK'

def get_gpt_pairing(sign1, sign2, category):
    prompt = (
        f"請以星座專家的角度分析 {sign1} 和 {sign2} 在「{category}」方面的配對情形。"
        f"給出配對分數（0~100）與一句建議，請用繁體中文。格式如下：\n配對分數：xx分\n建議：xxxxx"
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini 回覆失敗：{e}"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    types = ['整體', '愛情', '事業', '財運']
    modes = ['配對', '今日運勢']
    signs = ['牡羊座', '金牛座', '雙子座', '巨蟹座', '獅子座', '處女座',
             '天秤座', '天蠍座', '射手座', '摩羯座', '水瓶座', '雙魚座']

    print(f"📝 收到來自 {user_id} 的訊息：{msg}")
    state = user_state.get(user_id, {})

    if msg in types:
        user_state[user_id] = {'category': msg}
        print(f"🧠 儲存 category: {msg}")
        line_bot_api.reply_message(event.reply_token, build_mode_menu())
        return

    if msg in modes and 'category' in state:
        user_state[user_id]['mode'] = msg
        print(f"🧠 儲存 mode: {msg}")
        line_bot_api.reply_message(event.reply_token, build_star_menu())
        return

    if msg in signs and 'mode' in state:
        mode = state['mode']
        if mode == '今日運勢':
            category = state['category']
            result = get_horoscope_by_name(msg, category)
            flex = build_horoscope_card(msg, category, result)
            print(f"📦 回傳 {msg} 的 {category} 運勢")
            line_bot_api.reply_message(event.reply_token, flex)
            user_state.pop(user_id, None)
            return

        elif mode == '配對':
            selected = state.get('selected_signs', [])
            selected.append(msg)
            user_state[user_id]['selected_signs'] = selected

            if len(selected) == 2:
                sign1, sign2 = selected
                category = state['category']
                print(f"🔮 執行配對：{sign1} + {sign2} / {category}")
                reply = get_gpt_pairing(sign1, sign2, category)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
                user_state.pop(user_id, None)
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請再選擇另一個星座"))
            return

    print("⚠️ 無效輸入，重新顯示選單")
    line_bot_api.reply_message(event.reply_token, build_mode_menu())

if __name__ == "__main__":
    print("🚀 啟動 Horoscope Bot Flask 伺服器中...")
    port = int(os.environ.get("PORT", 5000))  # Render 會給你一個 PORT
    app.run(debug=True, host="0.0.0.0", port=port)  # ✅ 正確：開放給 Render 外部監聽
