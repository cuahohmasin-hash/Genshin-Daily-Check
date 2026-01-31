import discord
import genshin
import os
import asyncio
import datetime

# GitHub Secretsから環境変数を読み込む
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
GENSHIN_UID = int(os.environ["GENSHIN_UID"])

HOYOLAB_COOKIES = {
    "ltuid_v2": os.environ["LTUID_V2"],
    "ltoken_v2": os.environ["LTOKEN_V2"],
}

# ================= 設定エリア =================
# 樹脂通知の範囲（この範囲内の時だけ通知することで「1回だけ」を実現）
# 1時間ごとのチェックなら、上限は [閾値 + 10] くらいが適切です
RESIN_THRESHOLD_MIN = 180
RESIN_THRESHOLD_MAX = 200
# ============================================

async def main():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    gs_client = genshin.Client(HOYOLAB_COOKIES)

    # 現在時刻（JST）を取得
    JST = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(JST)
    current_hour = now.hour

    async with client:
        await client.login(DISCORD_TOKEN)
        channel = await client.fetch_channel(CHANNEL_ID)
        
        try:
            # データの取得
            notes = await gs_client.get_genshin_notes(GENSHIN_UID)
            
            # 通知用メッセージリスト
            messages = []
            
            # -------------------------------------------------
            # 1. デイリー依頼チェック (夜12時の回だけ実行)
            # -------------------------------------------------
            if current_hour == 0:
                completed = notes.completed_commissions
                claimed = notes.claimed_commission_reward
                
                print(f"[Daily Check] Completed: {completed}/4, Claimed: {claimed}")

                if completed < 4:
                    messages.append(
                        f"⚠️ **デイリー未達成** ({completed}/4)\n"
                        f"日付が変わりました。朝5時までに消化してください！"
                    )
                elif not claimed:
                    messages.append(
                        f"⚠️ **報酬未受取**\n"
                        f"キャサリンへの報告がまだです！"
                    )
            else:
                print(f"[Daily Check] 現在は{current_hour}時のためスキップします。")

            # -------------------------------------------------
            # 2. 樹脂（天然樹脂）チェック (毎時間実行)
            # -------------------------------------------------
            current_resin = notes.current_resin
            max_resin = notes.max_resin
            print(f"[Resin Check] Current: {current_resin}")

            # 樹脂が閾値の範囲内（例: 180〜191）にある時だけ通知
            # これにより「超えた瞬間」付近のみ通知し、溢れたまま放置しても連投されない
            if RESIN_THRESHOLD_MIN <= current_resin < RESIN_THRESHOLD_MAX:
                messages.append(
                    f"🌙 **樹脂が{RESIN_THRESHOLD_MIN}を超えました** ({current_resin}/{max_resin})\n"
                    f"あふれる前に消費してください！"
                )
            elif current_resin >= RESIN_THRESHOLD_MAX:
                print("樹脂は閾値を超えていますが、通知済みとみなしてスキップします。")

            # -------------------------------------------------
            # 通知送信処理
            # -------------------------------------------------
            if messages:
                content = f"<@{os.environ['USER_ID']}>\n" + "\n".join(messages)
                await channel.send(content)

        except Exception as e:
            print(f"Error: {e}")
            # エラー通知はウザくないようにコンソールログだけにするか、
            # 致命的な場合のみ通知するなど調整可能です
            pass

if __name__ == "__main__":
    asyncio.run(main())
