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

# 設定統一的產品商店連結
PRODUCT_URL = "https://www.nafulife.com/one-page-stores/6a3a237169122c9344d11cd3"

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
        reply_text = ""

        # 支援的所有關鍵字清單
        keywords = ["膠原", "瑩顧力", "唇膏", "沐浴", "洗顏", "洗臉", "咖啡", "精華"]

        # 檢查訊息中是否含有上述任一關鍵字
        for kw in keywords:
            if kw in user_message:
                reply_text = f"您好！想了解或購買商品，請點擊下方連結查看最新優惠：\n👉 {PRODUCT_URL}"
                break

        # 如果有匹配到關鍵字，發送回應
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
