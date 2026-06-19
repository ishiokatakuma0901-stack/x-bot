import tweepy
import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

# X API認証
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# Claude APIで投稿文を生成
def generate_post():
    claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    "メンタルヘルスに関する短いX投稿文を1つ作成してください。\n"
                    "条件：\n"
                    "- 140文字以内（日本語）\n"
                    "- 語尾は「にゃ」「にゃ～」を使うゆるいキャラクター設定\n"
                    "- 共感・気づき・励ましのどれか1つをテーマにする\n"
                    "- ハッシュタグは一切つけない（日常発信なので広告っぽくしない）\n"
                    "- 投稿文のみ出力し、説明や前置きは不要"
                ),
            }
        ],
    )
    return message.content[0].text

# 投稿
def post_tweet():
    text = generate_post()
    response = client.create_tweet(text=text)
    print(f"投稿しました: {text}")
    return response

if __name__ == "__main__":
    post_tweet()
