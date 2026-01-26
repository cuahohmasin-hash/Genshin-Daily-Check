import discord
import genshin
import os
import asyncio

# GitHub Secretsから環境変数を読み込む設定
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
GENSHIN_UID = int(os.environ["GENSHIN_UID"])

# CookieはJSON形式ではなく、個別の環境変数として渡すのが楽です
HOYOLAB_COOKIES = {
    "ltuid_v2": os.environ["LTUID_V2"],
    "ltoken_v2": os.environ["LTOKEN_V2"],
}

async def main():
    # Discordクライアントの準備
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    
    # 原神クライアントの準備
    gs_client = genshin.Client(HOYOLAB_COOKIES)

    async with client:
        # ログイン処理
        await client.login(DISCORD_TOKEN)
        
        # チャンネル取得
        channel = await client.fetch_channel(CHANNEL_ID)
        
        try:
            # データの取得
            notes = await gs_client.get_genshin_notes(GENSHIN_UID)
            completed = notes.completed_commission_count
            claimed = notes.is_extra_task_reward_received
            
            # 条件判定
            if completed < 4:
                await channel.send(
                    f"<@{os.environ['USER_ID']}> ⚠️ **デイリー未達成** ({completed}/4)\n"
                    f"日付が変わりました。朝5時までに消化してください！"
                )
            elif not claimed:
                await channel.send(
                    f"<@{os.environ['USER_ID']}> ⚠️ **報酬未受取**\n"
                    f"デイリーは終わっていますが、キャサリンへの報告がまだです！"
                )
            else:
                print("デイリー完了済み。通知なし。")

        except Exception as e:
            print(f"Error: {e}")
            # エラー時は自分にメンションで知らせると便利
            await channel.send(f"⚠️ Bot実行エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())