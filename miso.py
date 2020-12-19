import discord
import asyncio
import sqlite3
import os

client = discord.Client()

### 배너 카테고리에 역할설정 ! ! ! ###

category_id = 788964037194154004 #배너채널 생성되는 카테고리 ID
banner_role = 'BANNER MANAGER ' #배너역할 이름
logchannel_id = 788639202056863755  #개설 로그채널 ID
webhookcnl_id = 788639202056863755  #받아온 웹훅 보내주는 채널ID

@client.event
async def on_ready():
    db = sqlite3.connect('main2.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main2(
        author TEXT,
        author_id TEXT,
        channel TEXT,
        channel_id TEXT,
        status TEXT,
        log_id TEXT,
        hookchannel_id TEXT
        )
    ''')
    print("배너 봇이 성공적으로 실행되었습니다.")
    print(client.user.name)
    game = discord.Game('모든 직원한테 배너문의는 밴 입니다 저한테 해주세요 ;banner [ 배너명 ] ')
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_message(message):
    if message.content.startswith(';banner'):
        channelname = message.content[4:]
        bannerrole = discord.utils.get(message.guild.roles, name=banner_role)

        # 배너 역할 보유 여부 확인
        if bannerrole in message.author.roles:
            await message.channel.send('<:close:788701545764093983>  : 죄송합니다 이미 배너 역할을 가지고 있어 처리도중 역할 지급도중 에러가 발생하였습니다  ')
            return

        # 채널개설 및 배너역할 추가
        crcn = await message.guild.create_text_channel(name=channelname,
                                                       category=message.guild.get_channel(category_id))
        await message.author.add_roles(bannerrole)

        # 해당 채널에 웹훅 만들기
        web = await crcn.create_webhook(name=message.author, reason='배너봇 자동개설')

        # 배너채널에 태그
        await client.get_channel(int(crcn.id)).send(f'<@{message.author.id}>')

        # 웹훅 전송하고 웹훅 받는 채널생성
        overwrites = {
            message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            message.author: discord.PermissionOverwrite(read_messages=True)
        }

        webhookchannel = await message.guild.create_text_channel(name=message.author.name, overwrites=overwrites)

        cnl = client.get_channel(int(webhookchannel.id))

        hookbed = discord.Embed(title="저희는 모두 완료했습니다 [ 3 / 3 ] ", description='본인 서버에서 yisegen 제작을 하십시오. 그리고 서버 배너 역할 아이디와 서버링크를 알려주세요 ! 
                                , colour=discord.Colour.blue())
        hookbed.add_field(name='서버주소', value=web.url)
        infobed = discord.Embed(title='명령어', description='**;맞배너 [서버주소] [ 서버 배너를 입력할 수 있는 역할 ID ]**')
        await cnl.send(f'{message.author.mention}')
        await cnl.send(embed=hookbed)
        await cnl.send(embed=infobed)

        # 완료 알림 임베드 전송
        embed = discord.Embed(title='채널개설됨/역할지급됨', description=f'<#{crcn.id}>', colour=discord.Colour.green())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.set_footer(text='[ ! ] 장난 개설시 영구차단')
        await message.channel.send(embed=embed)
        await message.channel.send(f'<#{webhookchannel.id}> **를 확인해주세요**')

        # 프롬포트 로그 기록
        print(f"{message.author}({message.author.id}) 님이 배너를 생성하였습니다. 배너이름:  {crcn}")

        # 채널 로그 기록
        logbed1 = discord.Embed(colour=discord.Colour.red(), timestamp=message.created_at)
        logbed1.add_field(name='개설자', value=f"{message.author}({message.author.id})", inline=False)
        logbed1.add_field(name='배너명', value=f"<#{crcn.id}>", inline=False)
        logbed1.add_field(name='상태', value='미전송')
        firstlog = await client.get_channel(int(logchannel_id)).send(embed=logbed1)

        # sqlite 데이터베이스
        """
        file name == main2.sqlite
        """

        db = sqlite3.connect('main2.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT channel_id FROM main2 WHERE author_id = {message.author.id}')
        result = cursor.fetchone()
        if result is None:
            sql = (
                'INSERT INTO main2(author, author_id, channel, channel_id, status, log_id, hookchannel_id) VALUES(?,?,?,?,?,?,?)')
            val = (str(message.author), str(message.author.id), str(crcn), str(crcn.id), str('NO'), str(firstlog.id),
                   str(webhookchannel.id))
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    # 디엠
    if message.content.startswith(';맞배너'):
        # 띄어쓰기 구분
        learn = message.content.split(" ")
        invite = learn[1]
        hook = learn[2]

        # 임베드 내용 지정 채널로 전송
        dmembed = discord.Embed(title='맞배너 알림', description="\u200b", colour=discord.Colour.blurple(),
                                timestamp=message.created_at)
        dmembed.add_field(name='전송자', value=f"{message.author}({message.author.id})", inline=False)
        dmembed.add_field(name='서버주소', value=invite, inline=False)
        dmembed.add_field(name='웹훅링크', value=hook, inline=False)
        hooklog = await client.get_channel(int(webhookcnl_id)).send(embed=dmembed)
        await message.channel.send('👌')
        await hooklog.add_reaction('✅')

        db = sqlite3.connect('main2.sqlite')
        cursor = db.cursor()
        cursor2 = db.cursor()
        cursor.execute(f'SELECT status FROM main2 WHERE author_id = {message.author.id}')
        result2 = cursor.fetchone()
        if result2 is not None:
            sql = ('UPDATE main2 SET status = ? WHERE author_id = ?')
            val = (str('YES'), message.author.id)
        cursor.execute(sql, val)
        db.commit()

        cursor.execute(f"SELECT log_id FROM main2 WHERE author_id = {message.author.id}")
        a = str(cursor.fetchall())
        b = a.replace("[", "").replace("]", "").replace("'", "").replace("(", "").replace(")", "").replace(",", "")

        channel = client.get_channel(logchannel_id)
        msg = await channel.fetch_message(b)

        cursor2.execute(f"SELECT channel_id FROM main2 WHERE author_id = {message.author.id}")
        c = str(cursor2.fetchall())
        d = c.replace("[", "").replace("]", "").replace("'", "").replace("(", "").replace(")", "").replace(",", "")

        logbed2 = discord.Embed(colour=discord.Colour.green(), timestamp=message.created_at)
        logbed2.add_field(name='개설자', value=f"{message.author}({message.author.id})", inline=False)
        logbed2.add_field(name='배너명', value=f"<#{d}>", inline=False)
        logbed2.add_field(name='상태', value='전송')
        await msg.edit(embed=logbed2)
        cursor.close()
        db.close()

        embed = discord.Embed(description="")
        embed.set_author(name='감사합니다. 5초뒤 채널이 삭제됍니다',
                         icon_url='https://cdn.discordapp.com/attachments/721338948382752810/783923268780032041/aebe49a5b658b59d.gif')
        await message.channel.send(embed=embed)
        await asyncio.sleep(5)
        await message.channel.delete()


access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
