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
                    "メンタルヘルスに関する、読者の心に深く刺さるX投稿文を1つ作成してください。\n"
                    "条件：\n"
                    "- 日本語で130〜140文字。140文字は絶対に超えない（Xの上限のため）。できる限り上限近くまで文字数を使い、内容を濃くする\n"
                    "- 語尾は「にゃ」「にゃ～」を使うゆるい猫キャラクター設定（ただし内容は軽すぎず、芯のある言葉にする）\n"
                    "- 読者が『これは自分のことだ』と感じる具体的な情景や感情から入り、共感→気づき→そっと背中を押す、の流れで構成する\n"
                    "- ありふれた励ましで終わらせず、ハッとさせる視点の転換や言い換えを必ず一つ入れる\n"
                    "- ハッシュタグは一切つけない（日常発信なので広告っぽくしない）\n"
                    "- 投稿文のみ出力し、説明や前置きは不要"
                ),
            }
        ],
    )
    return message.content[0].text.strip()

# 投稿
def post_tweet():
    # 140文字以内に収まる投稿文が得られるまで最大4回試す（超過時は作り直す）
    text = generate_post()
    for _ in range(3):
        if len(text) <= 140:
            break
        text = generate_post()
    text = text[:140]  # 最終保険：それでも超えていたら切り詰める
    response = client.create_tweet(text=text)
    print(f"投稿しました（{len(text)}文字）: {text}")
    return response

if __name__ == "__main__":
    post_tweet()
