import os

import tweepy
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-8"

# ── X API認証（v2でテキスト投稿）──
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ① 今バズっているメンタル系の切り口をWeb検索でリサーチ
def research_trends():
    messages = [{
        "role": "user",
        "content": (
            "日本のX（旧Twitter）で今、メンタルヘルス・自己肯定感・HSP・生きづらさ・人間関係の悩み系の投稿のうち、"
            "リポストやいいね・保存が伸びている『切り口・テーマ・言い回しの型』の傾向を調べてください。\n"
            "最近反応が良い投稿の型（書き出し／共感のさせ方／締めの一言）を3〜5個、簡潔な箇条書きでまとめてください。"
        ),
    }]
    tools = [{"type": "web_search_20260209", "name": "web_search"}]
    resp = None
    for _ in range(5):
        resp = claude.messages.create(
            model=MODEL, max_tokens=1500, tools=tools, messages=messages
        )
        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            continue
        break
    return "\n".join(b.text for b in resp.content if b.type == "text").strip()


# ② リサーチを踏まえて、刺さるテキスト投稿を生成
def generate_post(trends):
    resp = claude.messages.create(
        model=MODEL,
        max_tokens=400,
        system="あなたはフォロワーとエンゲージメントを伸ばすのが得意な、メンタルヘルス系Xアカウント運用のプロです。",
        messages=[{
            "role": "user",
            "content": (
                "以下は今バズっているメンタル系投稿の傾向リサーチです。\n\n"
                f"=== リサーチ ===\n{trends}\n=== ここまで ===\n\n"
                "この傾向を踏まえ、思わず保存・リポストしたくなる、心に深く刺さるメンタルヘルスのX投稿文を1つ作ってください。\n"
                "条件：\n"
                "- 改行を含めて日本語で130〜140文字。改行も1文字として数え、改行込みで140文字を絶対に超えない（Xの上限のため）。できる限り上限近くまで使い内容を濃くする\n"
                "- 読みやすいように、意味のまとまりごとに適度な改行を入れ、2〜3つの短いブロックに分ける（一文に詰め込まない）\n"
                "- 語尾は「にゃ」「にゃ〜」を使うゆるい猫キャラ設定。ただし内容は軽すぎず、芯のある言葉にする\n"
                "- 読者が『これは自分のことだ』と感じる具体的な情景や感情から入り、共感→気づき→そっと背中を押す、の流れで構成する\n"
                "- ありふれた励ましで終わらせず、ハッとする視点の転換を必ず一つ入れる\n"
                "- ハッシュタグ・絵文字は使わない\n"
                "- 投稿文のみ出力し、説明や前置き・かぎ括弧は一切不要"
            ),
        }],
    )
    return next((b.text for b in resp.content if b.type == "text"), "").strip()


def post_tweet():
    trends = research_trends()
    # 140文字以内に収まる投稿文が得られるまで最大4回試す（超過時は作り直す）
    text = generate_post(trends)
    for _ in range(3):
        if len(text) <= 140:
            break
        text = generate_post(trends)
    text = text[:140]  # 最終保険：それでも超えていたら切り詰める
    client.create_tweet(text=text)
    print(f"投稿しました（{len(text)}文字）:\n{text}")
    return text


if __name__ == "__main__":
    post_tweet()
