import discord
import asyncio
import datetime

client = discord.Client()


@client.event
async def on_ready():
    print("봇이 성공적으로 실행되었습니다.")
    game = discord.Game('⭐ 당신을 24시간 지켜보는중 🌟')
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    else:
        y = datetime.datetime.now().year
        m = datetime.datetime.now().month
        d = datetime.datetime.now().day
        h = datetime.datetime.now().hour
        min = datetime.datetime.now().minute
        bot_logs = '🚩 메세지 수정됌 '
        embed = discord.Embed(title='메시지 수정됨', colour=discord.Colour.orange())
        embed.add_field(name='유저', value=f'<@{before.author.id}>({before.author})', inline=False)
        embed.set_footer(text=f"유저 ID:{before.author.id} • 메시지 ID: {before.id}")
        embed.add_field(name='수정 전', value=before.content + "\u200b", inline=True)
        embed.add_field(name='수정 후', value=after.content + "\u200b", inline=True)
        embed.add_field(name='날짜', value=f"{y}-{m}-{d} {h}:{min}", inline=False)
        await client.get_channel(int(bot_logs)).send(embed=embed)
        
access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
