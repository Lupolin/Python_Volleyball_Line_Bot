from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, PushMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)

# 設定LINE BOT的Channel Access Token和Channel Secret
configuration = Configuration(access_token='wPdIYnEJbWi8GA1xBFzbm/gGVmUAQqbsuwr7giFN6uxxiciXGoqV2shl874I0YGhOkRUVQ9KFdGUjq3zoooSi5p1uAF8GIT8THBJaGcbHSbwmyFnYHq/+VeN9f0wz71y9zU1LuVlgieLOn4rh6ABTAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1c32b782382c378cc6644bad4c5a3c6a')

# 用來存儲用戶ID的集合
user_ids = set()

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature 頭部的值
    signature = request.headers['X-Line-Signature']

    # 將請求主體作為文本獲取
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 webhook 主體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(200)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id  # 自動抓取用戶ID
    user_ids.add(user_id)  # 將用戶ID加入集合中

    # User輸入內容，系統回覆設定：
    # with ApiClient(configuration) as api_client:
    #     line_bot_api = MessagingApi(api_client)
    #     line_bot_api.reply_message_with_http_info(
    #         ReplyMessageRequest(
    #             reply_token=event.reply_token,
    #             messages=[TextMessage(text="已收到你的消息!")]
    #         )
    #     )

# 定時任務函數
def send_scheduled_message():
    message_text = """本週練習資訊
教練： @鴻明   / @陳昆樂Roy   
帶球人員： @根  / @詹詠智   
球車：柏臨

如需請假，請在記事本上回報，謝謝！"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        for user_id in user_ids:  # 向所有已知的user_id發送消息
            line_bot_api.push_message_with_http_info(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=message_text)]
                )
            )

# 啟動定時任務
scheduler = BackgroundScheduler()
scheduler.add_job(send_scheduled_message, 'interval', hours=1)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)
