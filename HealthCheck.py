from os import stat
from attr import dataclass
import discord
from discord import embeds
from discord import message
from discord import channel
from discord import reaction
from discord.embeds import Embed
from discord import client
from discord.ext import commands,tasks
import sqlite3
import time
import os
import datetime
from discord.ext.commands.core import check_any
from discord.flags import MessageFlags
import requests
import datetime

basepath = os.path.split(os.path.realpath(__file__))[0]
bot = commands.Bot(command_prefix='//')
CheckFlag = False
CheckMessageID = 762792085916614678
CheckMessage = "お疲れ様でした♪"
ManageChannel = 702410476721668146
Savedate ="MM/DD"

def TaskClear():
        result=ConfigIO("remove")
        if result == True:
            CheckFlag = False
            CheckMessageID = None
        else:
            param = {"Content-Type":"application/json","content": "@everyone 【異常通知】\nTimeTaskManageの処理を正常に終了できませんでした。\nコンフィグファイルの削除失敗"}
            requests.post("https://discordapp.com/api/webhooks/762755573954772992/P3tF2WDxF03rYip9QyW3DNjGxFF5ZLRFE-aRVkNrNH6KTTPAy50OY-48cH1DZVZk8Z9N",data=param)

@tasks.loop(seconds=30)
async def TimeTaskManage():
    global CheckFlag
    global CheckMessageID

    if datetime.datetime.now().strftime('%H:%M') =="0000" and CheckFlag is True:
        TaskClear()

def ConfigIO(type,messageID=None):
    #type write,read,remove

    configpath = os.path.join(basepath,"HealthCheck-config.txt")

    if type =="write":
        with open(configpath,"w") as f:
            f.write(str(messageID))

    elif type == "read":
        try:
            with open(configpath) as f:
                return f.read()
        except:
            return None

    elif type == "remove":
        try:
            os.remove(configpath)
            return True
        except:
            return False


@bot.event
async def on_ready():
    global CheckMessageID
    #CheckMessageID= ConfigIO("read")
    print("BootSuccess")
    pass

@bot.event
async def on_raw_reaction_add(payload):
    if CheckFlag !=True or CheckMessageID != payload.message_id:
        return
    #DMではmemberがNone
    if payload.member.bot:
        return

    conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
    c = conn.cursor()
    c.execute("select userName,healthStatus from userList where userID == ?",(payload.member.id,))
    result = c.fetchall()
    c.close()

    if not bool(result):
        await payload.member.send("こんにちは!\n私は、部活動に参加してくれた皆さんの体調を確認しています♪\nまだ知らない方だったので情報の登録をお願いします。リアクションの付け直しもお願いします")
        embed = discord.Embed(title = "//add [学年] [クラスまたは所属分野] [お名前]",description="学年は数字で入力してください\nクラスは1年生の方は一桁の数字 2年生移行の方は[J,M,E,D,A]から入力してください")
        await payload.member.send(embed=embed)
    else:
        if result[0][1] != 0:
            await payload.member.send("既に体調は確認済みです! 変更したいときは一度リアクションを消してから付け直してください")
            return
        conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
        c = conn.cursor()
        embed = None
        if payload.emoji.name == "👌":
            c.execute("update userList set healthStatus = ? where userID = ?",(1,payload.member.id))
            #          update userList set userGrade = ?,    where userID = ?",(grade,affiliation,name,ctx.author.id)
            conn.commit()
            embed = discord.Embed(title = "体調良好♪ 確認しました！",description="//reason [連絡したい事] でadmin権限を持った人に、あなたの名前と体調を添えて連絡出来ます。")
        
        if payload.emoji.name == "😫":
            c.execute("update userList set healthStatus = ? where userID = ?",(2,payload.member.id))
            conn.commit()
            embed = discord.Embed(title = "体調不良で確認しました。お大事に…",description="//reason [連絡したい事] でadmin権限を持った人に、あなたの名前と体調を添えて連絡出来ます。")
        c.close()
        await payload.member.send(embed=embed)

        
    

@bot.event
async def on_raw_reaction_remove(payload):
    print(payload)
    if CheckFlag !=True or CheckMessageID != payload.message_id:
        return
    
    conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
    c = conn.cursor()
    c.execute("update userList set healthStatus = ? where userID = ?",(0,payload.user_id))
    conn.commit()
    c.close()
    user = bot.get_user(payload.user_id)
    await user.send("確認を取り消しました")


#メッセージを全取得してフィルター
@bot.event
async def on_message(message):

    await bot.process_commands(message)


@bot.command()
async def add(ctx,grade,affiliation,name):
    if not grade.isdecimal():
        await ctx.send("指定の方法に間違いがあります！")
        return
    if not affiliation.isalnum():
        await ctx.send("指定の方法に間違いがあります！")
        return
    if grade =="1" and affiliation.isalpha():
        await ctx.send("指定の方法に間違いがあります！")
        return

    await ctx.send("はい♪分かりました。しばらくたっても返事がない場合、登録に失敗しちゃったかもしれません。改めて送りなおして見てくださいね")

    conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
    c = conn.cursor()
    c.execute("select userName from userList where userID == ?",(ctx.author.id,))
    userID = c.fetchall()
    affiliation = affiliation.upper()
    if userID ==[]:
        c.execute("insert into userList(userID,userGrade,userAffiliation,userName,healthStatus) values(?,?,?,?,?)",(ctx.author.id,grade,affiliation,name,0))
        conn.commit()
        c.close()
    else:
        c.execute("update userList set userGrade = ?,userAffiliation = ?,userName = ? where userID = ?",(grade,affiliation,name,ctx.author.id))
        conn.commit()
        c.close()
        
    if grade =="1":
        embed = discord.Embed(title = grade+"-"+affiliation+":"+name+"さんで登録が完了しました♪",description="//addコマンドでそのまま修正できます。ご協力ありがとうございます！")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title = grade+affiliation+":"+name+"さんで登録が完了しました♪",description="//addコマンドでそのまま修正できます。ご協力ありがとうございます！")
        await ctx.send(embed=embed)



@bot.command()
async def call(ctx,channelName = None):
    global CheckFlag
    global CheckMessageID
    global Savedate
    await ctx.message.delete()
    msg = await ctx.send(CheckMessage)
    await msg.add_reaction("👌")
    await msg.add_reaction("😫")
    ConfigIO("write",msg.id)
    CheckMessageID = msg.id
    CheckFlag = True
    Savedate = str(datetime.datetime.now().strftime("%m-%d"))

@bot.command()
async def close(ctx):
    if CheckFlag == True:
        TaskClear()
        ConfigIO("remove")
        await ctx.send("分かりました♪確認を終了します")
    else:
        await ctx.send("まだ集計は行われていないみたいです…")
        return
    await ctx.send("集計中…")
    conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
    c = conn.cursor()

    outputUser =[]
    outputUser.append(Savedate)
    for i in [1,2,3,4,5]:
        c.execute("select userGrade,userAffiliation,userName,healthStatus from userList where userGrade == ?",(i,))
        result = c.fetchall()
        
        if len(result)!=0:
            for users in result[0]:
                print(users)
                status =""
                if users[3] == 1:
                    status = "良好"
                elif users[3] == 2:
                    status = "不良"

                user = str(users[0])+"-"+str(users[1])+":"+str(users[2])+" 体調:"+status
                print(user)
                outputUser.append(user)
    
    Filepath = os.path.join(basepath,"HealthCheck-helthList("+Savedate+").txt")
    with open(Filepath,mode="w") as f :
        f.write('\n'.join(outputUser))
    await ctx.send("集計完了♪")
    await ctx.send(file=discord.File(Filepath))




@bot.command()
async def reason(ctx,reasons):
    conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
    c = conn.cursor()
    c.execute("select userGrade,userAffiliation,userName,healthStatus from userList where userID == ?",(ctx.author.id,))
    result = c.fetchall()
    if not result:
        ctx.send("こんにちは!\n私は、部活動に参加してくれた皆さんの体調を確認しています♪\nまだ知らない方だったので情報の登録をお願いします。")
        embed = discord.Embed(title = "//add [学年] [クラスまたは所属分野] [お名前]",description="学年は数字で入力してください\nクラスは1年生の方は一桁の数字 2年生移行の方は[J,M,E,D,A]から入力してください")
        await ctx.send(embed=embed)
        return

    status = ""
    if result[0][3] == 0:
        status = "確認中"
    elif result[0][3] == 1:
        status = "良好"
    elif result[0][3] == 2:
        status = "不良"

    channel =bot.get_channel(ManageChannel)
    if result[0][1] == 1:
        
        embed =discord.Embed(title = "【連絡】From "+str(result[0][0])+"-"+str(result[0][1])+":"+str(result[0][2])+" 体調:"+status,description=reasons)
        await channel.send(embed=embed)
        await ctx.send("送信成功♪")
    else:
        embed =discord.Embed(title = "【連絡】From "+str(result[0][0])+str(result[0][1])+":"+str(result[0][2])+" 体調:"+status,description=reasons)
        await channel.send(embed=embed)
        await ctx.send("送信成功♪")

    
    

bot.remove_command('help')
@bot.command()
async def help(ctx):
    pass

@bot.command()
@commands.is_owner()
async def init(ctx):
    conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
    c = conn.cursor()
    #ユーザーID,学年,所属学科(またはクラス),名前,体調情報(0=未参加,1=良好,2=不調)
    c.execute("create table userList(userID int,userGrade int,userAffiliation txt,userName txt,healthStatus int)")
    conn.commit()
    conn.close()

@bot.command()
@commands.is_owner()
async def sh(ctx):
	await ctx.send("shutdown now...")
	await bot.logout()

TimeTaskManage.start()
bot.run("NzYyNzI4NDc2OTEzNDM0NjI1.X3tYPw.zdgbCMbAgDtxf3NZP5OHIGEGlkA")
