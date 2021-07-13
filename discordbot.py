from discord.ext import commands
import os
import traceback

bot = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']


bot.run(token)


import time
import requests
import json
import copy
from datetime import datetime, timedelta, timezone

Hololive = {
    "UCDqI2jOz0weumE8s7paEk6g": [
        "ロボ子さん",
        "https://yt3.ggpht.com/ytc/AKedOLTVWKjrovP0tGtguup9TYZicykceA45olVmEr2kvQ=s88-c-k-c0x00ffffff-no-rj"
    ],
        "UC-hM6YJuNYVAmUWxeIr9FeA": [
        "さくらみこ",
        "https://yt3.ggpht.com/ytc/AKedOLRNGCUT1awYh91CbTr6r_v_6KspwpyAS4ZUxlucFQ=s88-c-k-c0x00ffffff-no-rj"
    ],
        "UC5CwaMl1eIgY8h02uZw7u8A": [
        "星街すいせい",
        "https://yt3.ggpht.com/ytc/AKedOLSAm13gTESsu39zgJ1TYb649BiGqYa_XCv5C6Lu=s88-c-k-c0x00ffffff-no-rj"
    ],
        "UCXTpFs_3PqI41qX2d9tL2Rw": [
        "紫咲シオン",
        "https://yt3.ggpht.com/ytc/AKedOLRJYi-cOhqB22oEjWfdz__fHcs9iGjwz5UkPzvd-w=s88-c-k-c0x00ffffff-no-rj"
    ],
        "UCvzGlP9oQwU--Y0r9id_jnA": [
        "大空スバル",
        "https://yt3.ggpht.com/ytc/AKedOLRaQJl61Pxhsnrzz50wirogPn18pPUYL0YFAauj=s88-c-k-c0x00ffffff-no-rj"
    ],
        "UCCzUftO8KOVkV4wQG1vkUvg": [
        "宝鐘マリン",
        "https://yt3.ggpht.com/ytc/AKedOLQFVN7wLaJFbdPU56qOkNlbkrMneYpTmGpneRig=s88-c-k-c0x00ffffff-no-rj"
    ],
        "UCZlDXzGoo7d44bwdNObFacg": [
        "天音かなた",
        "https://yt3.ggpht.com/ytc/AKedOLTgDWWow5gGLYfPKHxF8oNHegeUngIdT5HxDBo4=s88-c-k-c0x00ffffff-no-rj"
    ],

} #配信者のチャンネルID, 配信者名, アイコン画像のURLのリスト

webhook_url_Hololive = "https://discord.com/api/webhooks/864352021423456297/EmUNj_-207qUQZMuqGy8ctAMMMdzeeOarT6H6jjDdOLIPShEbVU0dN0x_6eiZH4Zb_SS" #ホロライブ配信開始
webhook_url_Hololive_yotei = "https://discord.com/api/webhooks/864352355528474664/pFehoGCIuP5Y6isyFQOMVVNlvslrPWWke1NKwQ3kgbJ0UVGIzoJj0pTPI97nFzo-UntN" #ホロライブ配信予定
broadcast_data = {} #配信予定のデータを格納

YOUTUBE_API_KEY = [] #複数のAPI(str型)をリストで管理

def dataformat_for_python(at_time): #datetime型への変換
    at_year = int(at_time[0:4])
    at_month = int(at_time[5:7])
    at_day = int(at_time[8:10])
    at_hour = int(at_time[11:13])
    at_minute = int(at_time[14:16])
    at_second = int(at_time[17:19])
    return datetime(at_year, at_month, at_day, at_hour, at_minute, at_second)

def replace_JST(s):
    a = s.split("-")
    u = a[2].split(" ")
    t = u[1].split(":")
    time = [int(a[0]), int(a[1]), int(u[0]), int(t[0]), int(t[1]), int(t[2])]
    if(time[3] >= 15):
      time[2] += 1
      time[3] = time[3] + 9 - 24
    else:
      time[3] += 9
    return (str(time[0]) + "/" + str(time[1]).zfill(2) + "/" + str(time[2]).zfill(2) + " " + str(time[3]).zfill(2) + "-" + str(time[4]).zfill(2) + "-" + str(time[5]).zfill(2))

def post_to_discord(userId, videoId):
    haishin_url = "https://www.youtube.com/watch?v=" + videoId #配信URL
    content = "配信中！\n" + haishin_url #Discordに投稿される文章
    main_content = {
        "username": Hololive[userId][0], #配信者名
        "avatar_url": Hololive[userId][1], #アイコン
        "content": content #文章
    }
    requests.post(webhook_url_Hololive, main_content) #Discordに送信
    broadcast_data.pop(videoId)

def get_information():
    tmp = copy.copy(broadcast_data)
    api_now = 0 #現在どのYouTube APIを使っているかを記録
    for idol in Hololive:
        api_link = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=" + idol + "&key=" + YOUTUBE_API_KEY[api_now] + "&eventType=upcoming&type=video"
        api_now = (api_now + 1) % len(YOUTUBE_API_KEY) #apiを1つずらす
        aaa = requests.get(api_link)
        v_data = json.loads(aaa.text)
        try:
            for item in v_data['items']:#各配信予定動画データに関して
                broadcast_data[item['id']['videoId']] = {'channelId':item['snippet']['channelId']} #channelIDを格納
            for video in broadcast_data:
                try:
                    a = broadcast_data[video]['starttime'] #既にbroadcast_dataにstarttimeがあるかチェック
                except KeyError:#なかったら
                    aaaa = requests.get("https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id=" + video + "&key=" + YOUTUBE_API_KEY[api_now])
                    api_now = (api_now + 1) % len(YOUTUBE_API_KEY) #apiを1つずらす
                    vd = json.loads(aaaa.text)
                    print(vd)
                    broadcast_data[video]['starttime'] = vd['items'][0]['liveStreamingDetails']['scheduledStartTime']
        except KeyError: #配信予定がなくて403が出た
            continue
    for vi in broadcast_data:
        if(not(vi in tmp)):
            print(broadcast_data[vi])
            try:
                post_broadcast_schedule(broadcast_data[vi]['channelId'], vi, broadcast_data[vi]['starttime'])
            except KeyError:
                continue

def check_schedule(now_time, broadcast_data):
    for bd in list(broadcast_data):
        try:
            # RFC 3339形式 => datetime
            sd_time = datetime.strptime(broadcast_data[bd]['starttime'], '%Y-%m-%dT%H:%M:%SZ') #配信スタート時間をdatetime型で保管
            sd_time += timedelta(hours=9)
            if(now_time >= sd_time):#今の方が配信開始時刻よりも後だったら
                post_to_discord(broadcast_data[bd]['channelId'], bd) #ツイート
        except KeyError:
            continue

def post_broadcast_schedule(userId, videoId, starttime):
    st = starttime.replace('T', ' ')
    sst = st.replace('Z', '')
    ssst = replace_JST(sst)
    haishin_url = "https://www.youtube.com/watch?v=" + videoId #配信URL
    content = ssst + "に配信予定！\n" + haishin_url #Discordに投稿される文章
    main_content = {
        "username": Hololive[userId][0], #配信者名
        "avatar_url": Hololive[userId][1], #アイコン
        "content": content #文章
    }
    requests.post(webhook_url_Hololive_yotei, main_content) #Discordに送信

while True:
    now_time = datetime.now() + timedelta(hours=9)
    if(((now_time.year > 2020) or ((now_time.year == 2020) and (now_time.month >= 6) and (now_time.day >= 22))) and (now_time.minute == 0) and (now_time.hour % 2 == 0)):
        get_information()
    check_schedule(now_time, broadcast_data)
    time.sleep(60)

