import discord
import genshin
import os
import asyncio

# GitHub Secretsから環境変数を読み込む
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
GENSHIN_UID = int(os.environ["GENSHIN_UID"])

HOYOLAB_COOKIES = {
    "ltuid_v2": os.environ["LTUID_V2"],
    "ltoken_v2": os.environ["LTOKEN_V2"],
}

async def main():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    gs_client = genshin.Client(HOYOLAB_COOKIES)

    async with client:
        await client.login(DISCORD_TOKEN)
        channel = await client.fetch_channel(CHANNEL_ID)
        
        try:
            # データの取得
            notes = await gs_client.get_genshin_notes(GENSHIN_UID)
            
            # --- 修正箇所 ---
            # デイリー依頼の完了数 (0-4)
            completed = notes.completed_commissions
            # キャサリンへの報告が完了しているか (True/False)
            claimed = notes.claimed_commission_reward
            # ----------------
            
            # デバッグ用：取得した値をログに出力（Actionsのログで確認できます）
            print(f"Daily Commissions: {completed}/4, Claimed: {claimed}")

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

        except AttributeError as e:
            # もしまた属性エラーが出た場合、中身を全部表示してデバッグしやすくする
            await channel.send(f"⚠️ プログラム修正が必要です。開発者ログを確認してください: {e}")
            print(f"Attributes available: {dir(notes)}") 
            
        except Exception as e:
            print(f"Error: {e}")
            await channel.send(f"⚠️ Bot実行エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())