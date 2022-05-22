from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    FollowEvent, MessageEvent, 
    TextMessage, TextSendMessage, TemplateSendMessage, 
    CarouselTemplate, 
    CarouselColumn, 
    PostbackAction, URIAction
)

app = Flask (__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linefresh.sqlite3'
db = SQLAlchemy(app)

line_bot_api = LineBotApi('516KsFfnTZ7zAfSfGUJhTYt4T2PBnRThlzS5LZ5DApqHpHV/eb4ODPT5aXcWiKkpkwVvXBU/c66yG7WGF/2m1HTRZdXIOZiVF1LXBBMEyGulfhuyYXRIMTkWvXA8H0NJM1/rF2P/ILtBkEjKrloqywdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('4506bcd2d49c87a004060cae9d223e7e')

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    userid = db.Column(db.String, nullable = False, unique = True)

    def __init__(self, userid):
        self.userid = userid

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    # Add to database
    user = get_user(event.source.user_id)
    # Reply
    username = line_bot_api.get_profile(user.userid).display_name
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"歡迎加入！{username}")
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # Add to database
    user = get_user(event.source.user_id)
    # Reply
    message_text = event.message.text
    if message_text == '20010713':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{user.userid}")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

def get_user(userid):
    user = Users.query.filter_by(userid=userid).first()
    if user is None:
        user = Users(userid)
        db.session.add(user)
        db.session.commit()
        print(f"Add user: {user.userid}")
    return user

# def get_all_user():
#     users = Users.query.all()
#     result = ""
#     for user in users:
#         result += f"user: {user.userid} \n"
#     return result

# @app.route("/<string:userid>")
# def test(userid):
#     user = get_user(userid)
#     return f"{user.userid}"

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
    