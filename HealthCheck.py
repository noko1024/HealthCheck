from attr import dataclass
import discord
from discord import embeds
from discord import message
from discord.embeds import Embed
from discord.ext import commands,tasks
import sqlite3
import time
import os
import datetime
import requests

basepath = os.path.split(os.path.realpath(__file__))[0]
bot = commands.Bot(command_prefix='//')
CheckFlag = False
CheckMessageID = 762792085916614678
CheckMessage = "@everyone\お疲れ様でした♪"

@tasks.loop(seconds=30)
async def TimeTaskManage():
    global CheckFlag
    if datetime.datetime.now().strftime('%H:%M') =="0000" and CheckFlag is True:
        result=ConfigIO("remove")
        if result == True:
            CheckFlag = False
        else:
            param = {"Content-Type":"application/json","content": "@everyone 【異常通知】\nTimeTaskManageの処理を正常に終了できませんでした。\nコンフィグファイルの削除失敗"}
            requests.post("https://discordapp.com/api/webhooks/762755573954772992/P3tF2WDxF03rYip9QyW3DNjGxFF5ZLRFE-aRVkNrNH6KTTPAy50OY-48cH1DZVZk8Z9N",data=param)

def ConfigIO(type,messageID=None):
    #type write,read,remove

    configpath = os.path.join(basepath,"HealthCheck-config.txt")

    if type =="write":
        with open(configpath,"w") as f:
            f.write(messageID)

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
    c.execute("select userName from userList where userID == ?",(payload.member.id,))
    userID = c.fetchall()
    conn.close()
    if userID ==[]:
        await payload.member.send("こんにちは!\n私は、部活動に参加してくれた皆さんの体調を確認しています♪\nまだ知らない方だったので情報の登録をお願いします。リアクションの付け直しもお願いします")
        embed = discord.Embed(title = "//add [学年] [クラスまたは所属分野] [お名前]",description="学年は数字で入力してください\nクラスは1年生の方は一桁の数字 2年生移行の方は[J,M,E,D,A]から入力してください")
        await payload.member.send(embed=embed)
    else:
        pass
    

@bot.event
async def on_raw_reaction_remove(payload):
    if CheckFlag !=True or CheckMessageID != payload.message_id:
        return
    if payload.member.bot:
        return


#メッセージを全取得してフィルター
@bot.event
async def on_message(message):
    global CheckMessageID
    global CheckFlag

    if message.author.id == 762728476913434625:
        if message.content.startswith(CheckMessage):
            CheckMessageID = message.id
            CheckFlag = True

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
        c.execute("insert into userList(userID,userGrade,userAffiliation,userName) values(?,?,?,?)",(ctx.author.id,grade,affiliation,name))
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
async def call(ctx):
    await ctx.send(CheckMessage)

@bot.command()
async def replay(ctx,re):
    await ctx.send()

bot.remove_command('help')
@bot.command()
async def help(ctx):
    pass

@bot.command()
@commands.is_owner()
async def init(ctx):
    conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
    c = conn.cursor()
    c.execute("create table userList(userID int,userGrade int,userAffiliation txt,userName txt)")
    conn.commit()
    conn.close()

@bot.command()
@commands.is_owner()
async def sh(ctx):
	await ctx.send("shutdown now...")
	await bot.logout()

TimeTaskManage.start()
bot.run("NzYyNzI4NDc2OTEzNDM0NjI1.X3tYPw.zdgbCMbAgDtxf3NZP5OHIGEGlkA")
