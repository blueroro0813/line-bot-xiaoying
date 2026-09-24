import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 從雲端環境變數讀取金鑰
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 統一產品商店連結
PRODUCT_URL = "https://www.nafulife.com/one-page-stores/6a3a237169122c9344d11cd3"

# 1. 晶瑩PLUS快充膠原飲說明
COLLAGEN_USAGE = (
    "🥤 晶瑩PLUS快充膠原飲 食用說明：\n"
    "✔ 日常保養：每天1包\n"
    "✔ 加強保養：每天2包\n\n"
    "💡 建議時間：早上空腹 或 睡前飲用\n"
    "幫助身體吸收利用，養成每天保養習慣✨\n\n"
    "👩‍🦰 建議適用對象：\n"
    "・想加強日常保養者\n"
    "・注重水潤與美麗保養者\n"
    "・熬夜、作息不規律者\n"
    "・外食族、保養不足者"
)

# 2. 瑩顧力PLUS複方膠囊說明
GULI_USAGE = (
    "🦵 瑩顧力PLUS複方膠囊 食用說明：\n"
    "✔ 日常保養：一天1顆\n\n"
    "💡 建議時間：飯前搭配冷開水食用即可\n"
    "若怕刺激胃，也可以餐間或飯後食用 😊\n\n"
    "🦵 建議適用對象：\n"
    "・久站久坐族\n"
    "・常運動、爬山族群\n"
    "・銀髮日常保養\n"
    "・想維持靈活行動力者\n"
    "・常感覺卡卡、不順暢者 ✨"
)

# 3. 客服轉接文字
SERVICE_TEXT = (
    "👩‍💼 如須轉接專人或聯繫客服，請參考以下方式：\n\n"
    "📞 客服電話：02-2651-1893\n"
    "🕒 營業時間：10:00 - 16:00\n\n"
    "💬 如需專人文字服務，請在群組中直接標記：\n"
    "👉 @Twbio 小瑩客戶小幫手"
)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text.strip()

    # 必須包含呼叫詞「小瑩」才觸發回應
    if "小瑩" in user_message:
        # 取得詢問者的名字
        user_name = "您"
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                if event.source.type == "group":
                    profile = line_bot_api.get_group_member_profile(event.source.group_id, event.source.user_id)
                    user_name = profile.display_name
                else:
                    profile = line_bot_api.get_profile(event.source.user_id)
                    user_name = profile.display_name
        except Exception:
            pass

        reply_text = ""

        # 1. 客服 / 轉接專人判斷
        if any(kw in user_message for kw in ["客服", "專人", "轉接", "真人", "電話", "聯絡", "小幫手"]):
            reply_text = f"{user_name} {SERVICE_TEXT}"

        # 2. 膠原蛋白判斷
        elif "膠原" in user_message:
            reply_text = f"{user_name} 您好！【晶瑩PLUS快充膠原飲】詳細資訊如下：\n\n{COLLAGEN_USAGE}\n\n🛒 最新優惠購買連結：\n👉 {PRODUCT_URL}"

        # 3. 瑩顧力判斷（含同音錯字「瑩骨力」、「骨力」）
        elif any(kw in user_message for kw in ["瑩顧力", "顧力", "瑩骨力", "骨力", "卡卡", "靈活"]):
            reply_text = f"{user_name} 您好！【瑩顧力PLUS複方膠囊】詳細資訊如下：\n\n{GULI_USAGE}\n\n🛒 最新優惠購買連結：\n👉 {PRODUCT_URL}"

        # 4. 其他商品關鍵字（預設給購買連結）
        elif any(kw in user_message for kw in ["唇膏", "沐浴", "洗顏", "洗臉", "咖啡", "精華"]):
            reply_text = f"{user_name} 您好！想了解或購買商品，請點擊下方連結查看最新優惠：\n👉 {PRODUCT_URL}"

        # 發送普通文字回覆
        if reply_text:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )

if __name__ == "__main__":
    app.run(port=5000)
