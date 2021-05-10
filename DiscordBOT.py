import discord
from discord.ext import commands
import subprocess
import ffmpeg
import re
from io import BytesIO
import csv
import pandas as pd
from gtts import gTTS
from discord.ext import commands
import ffmpeg
import time
from pydub import AudioSegment
voice_client = None
client = discord.Client()

if not discord.opus.is_loaded(): 
    discord.opus.load_opus("heroku-buildpack-libopus")

token = os.environ["DISCORD_BOT_TOKEN"]    
    
patternlist1 = ['w{3,}','ｗ{3,}']
word1 = ['わらわら','わらわら']

patternlist2 = ['ｗ']
word2 = ['わら']


patternlist = []
word = []
server = []

def update():
    global patternlist
    global word
    global server
    patternlist = []
    word = []  
    csv_file = open("pattern.csv", "r", encoding="utf-8_sig")
    f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    for row in f:
        for i in range(0,len(row)):
            if i == 0:
                print(row[i])

                patternlist.append(row[i])
            elif i == 1:
                print(row[i])
                word.append(row[i])
            elif i == 2:
                print(row[i])
                server.append(row[i])
                

               
update()



def remove_custom_emoji(text,sid):
    global patternlist
    global word
    global patternlist1
    global patternlist2
    global word1
    global word2
    global server
    txt = text
    for i in range(0,len(patternlist1)):    
        txt = re.sub(patternlist1[i],word1[i],txt)
    for i in range(0,len(patternlist)):
        if server[i] == str(sid):
            txt = re.sub(patternlist[i],word[i],txt)
    for i in range(0,len(patternlist)):
        if server[i] == str(sid):
            txt = txt.replace(patternlist[i],word[i]) 
    for i in range(0,len(patternlist2)):    
        txt = re.sub(patternlist2[i],word2[i],txt)
    txt = re.sub(r'^https?:\/\/.*[\r\n]*', "url" ,txt)
    pattern = r'<@![0-9]+>'
    txt = re.sub(pattern,'メンション',txt)
    pattern = r'<:[a-zA-Z0-9_]+:[0-9]+>'
    txt = re.sub(pattern,'絵文字',txt)
    return txt





@client.event
async def on_message(message: discord.Message):
    global patternlist
    global word
    serverid = message.guild.id
    print(serverid)
    if message.author.bot:
        return

    if message.content[0:4] == "!!aw":
        m = message.content[5:]       
        s = m.split(" ")
        df = pd.read_csv('pattern.csv')
        drop_index = df.index[df['before'] == s[0]]
        df = df.drop(drop_index)
        df.to_csv('pattern.csv', encoding='utf_8_sig',index=False)
        
        with open('pattern.csv', 'a',encoding="utf-8_sig") as f:
            writer = csv.writer(f)
            writer.writerow([s[0],s[1],serverid])
        
        update()

        await message.channel.send("このサーバーの辞書に登録しました。"+s[0]+"→"+s[1])
        
        
    if message.content[0:9] == "!!diclist":
        dl = "| 変換前 | 変換後 |"
        for i in range(0, len(patternlist)):
            dl += "\n"+"| "+patternlist[i]+" | "+ word[i] +" |"                   
        await message.channel.send(dl)
        
    elif message.content == "!!join":
        if message.author.voice is None:
            await message.channel.send("あなたはボイスチャンネルに接続していません。")
            return true
        # ボイスチャンネルに接続する
        await message.author.voice.channel.connect()
        await message.channel.send("接続しました。")
        


    elif message.content == "!!leave":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        # 切断する
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")

    elif message.content.startswith('!!'):
        pass

    else:
        if message.guild.voice_client:
            vocl = message.guild.voice_client
            while vocl.is_playing():
                time.sleep(0.01)
            mc = remove_custom_emoji(message.content,serverid)
            
            with open('output.mp3', 'wb') as f:
                i3 = 0
                for i in range(0,len(mc)):

                    m = re.match('[a-z|A-Z|\s]+',mc[i3:])
                    #[ぁ-ん|ァ-ン|一-龥|ー|ｱ-ﾝ| ﾞ|ｧ-ｮ]
                    #
                    #m1 = re.match('[ぁ-ん|ァ-ン|一-龥|ー|ｱ-ﾝ| ﾞ|ｧ-ｮ|\d|%|\s|ヶ|ａ-ｚ|ゔ|ヴ|→|←|↑|↓]+',mc[i3:])
                    m1 = re.match("[^a-zA-Z]+",mc[i3:])
                    if m!=None:
                        #print(inputText[i3:])
                        print(m.group())
                        tts_en = gTTS(text=m.group(), lang='en-us')
                        tts_en.write_to_fp(f)
                        i3 += len(m.group())




                    elif m1!=None:
                        

                        try:
                            print(m1.group())
                            tts_jp = gTTS(text=m1.group(), lang='ja')            
                            tts_jp.write_to_fp(f)
                            i3 += len(m1.group())
                        except AssertionError:
                            continue
                        
                    else:
                       i3 += 1
             
                       
                        
            source = discord.FFmpegPCMAudio("output.mp3")

                
            message.guild.voice_client.play(source)
        else:
            pass


client.run(token)
