import discord
import configparser
import random
import mysql.connector
import asyncio
import requests
import youtube_dl
from discord.utils import get
config = configparser.ConfigParser(strict=False)
config.read('config.ini')
TOKEN = config['DEFAULT']['Token']
print(TOKEN)
client = discord.Client()
blacklist = []
adminlist = []
pointCooldown = []
pollActive = False
votes = {}
hasVoted = []
voiceObject = None
dic = {}
player = None
F = open("Blacklist.txt","r")
for Word in F:
    Word = Word.rstrip('\n')
    blacklist.append(Word)
F.close()
F = open("admins.txt","r")
for Word in F:
    Word = Word.rstrip('\n')
    adminlist.append(Word)
F.close()
'''
@client.event
async def on_member_join(member):
    sql = "INSERT INTO discordUserTbl (user_ID, points, warnings) VALUES ('" + str(member.id) + "'0,0)"
    cursor.execute(sql)
    mydb.commit()
'''
@client.event
async def on_message(message):
    global voiceObject
    global player
    isadmin = False
    for rank in message.author.roles:
        if rank.name in adminlist:
            print(rank.name)
            isadmin = True
    if message.author == client.user:
        return
    if isadmin == False:
        if(bool(config['DEFAULT']['Blacklist'])):
            if(await checkBlacklist(message)):
                return
    if message.content.lower().startswith('!test'):
        msg = 'Hello' + str(message.author)
        await client.send_message(message.channel, msg)
    elif message.content.lower().startswith('!blacklist_add'):
        if(isadmin):
            message = message.content
            message = message.replace(' ','')
            message = message[14:]
            blacklist.append(message)
            F = open("Blacklist.txt","a")
            F.write("\n" + message)
            F.close()
    elif message.content.lower().startswith('!blacklist_remove'):
        print("f")
    elif message.content.lower().startswith('!dean'):
        await client.send_message(message.channel, 'SAMMY!')
    elif message.content.lower().startswith('!mute'):
        if(isadmin):
            bagel = message.content
            bagel = bagel[6:]
            print(bagel)
            role = get(message.server.roles, name='mute')
            member =  message.server.get_member_named(bagel)
            await client.add_roles(member, role)
    elif message.content.lower().startswith('!unmute'):
        if(isadmin):
            bagel = message.content
            bagel = bagel[8:]
            role = get(message.server.roles, name='mute')
            member =  message.server.get_member_named(bagel)
            await client.remove_roles(member, role)
    elif message.content.lower().startswith('!poll'):
        if message.content.lower().startswith('!poll start'):
            if(isadmin):
                s = message.content[12:]
                time = s[:s.index(' ')]
                options = s[s.index(' ')+1:]
                options = options.split(',')
                await startPoll(int(time), options, message.channel)
        elif message.content.lower().startswith('!poll vote'):
            if str(message.author.id) not in hasVoted:
                value = message.content[11:]
                if value in dic:
                    dic[value] += 1
                    hasVoted.append(str(message.author.id))
                else:
                    await client.send_message(message.channel, value + ' is not an option')
            else:
                await client.send_message(message.channel, 'You have already voted')
        else:
            await client.send_message(message.channel, 'User !poll start option1,option2,etc. to start a poll and !poll vote. Use commas to separate options for poll')
    elif message.content.lower().startswith('!kick'):
        if(isadmin):
            bagel = message.content
            bagel = bagel[6:]
            member =  message.server.get_member_named(bagel)
            await client.kick(member)
    elif message.content.lower().startswith('!ban'):
        if(isadmin):
            bagel = message.content
            bagel = bagel[5:]
            member =  message.server.get_member_named(bagel)
            await client.ban(member)
    elif message.content.lower().startswith('!admin_add'):
        if(isadmin):
            message = message.content
            message = message[11:]
            adminlist.append(message)
            F = open("admins.txt","a")
            F.write("\n" + message)
            F.close()
    elif message.content.lower().startswith('!admin_remove'):
        if(isadmin):       
            message = message.content
            message = message[14:]
            if adminlist.count(message) > 0:
                adminlist.remove(message)
            F = open("admins.txt","w")
            for word in adminlist:
                F.write(word + "\n")
            F.close()
    elif message.content.lower().startswith('!gif'):
        if len(message.content.strip()) == 4:
            URL = "http://api.giphy.com/v1/gifs/random"
            PARAMS = {'api_key': 'JuO0eqPLAj46MV6PGfrdo7iymOWAGROd'}
            r = requests.get(url = URL, params = PARAMS)
            data = r.json()
            url = data['data']['embed_url']
        else:
            s = message.content[4:]
            URL = "http://api.giphy.com/v1/gifs/search"
            PARAMS = {'api_key': 'JuO0eqPLAj46MV6PGfrdo7iymOWAGROd', 'q':s, 'limit': 1}
            r = requests.get(url = URL, params = PARAMS)
            data = r.json()
            url = data['data'][0]['embed_url']        
        await client.send_message(message.channel, url)
    elif message.content.lower().startswith('!join'):
        
        ##client.voice_client_in(message.server).disconnect()
        s = message.content[6:]
        print(voiceObject)
        if voiceObject == None:
            for channel in message.server.channels:
                if channel.name == s:
                    voiceObject = await client.join_voice_channel(channel)
                    ##player = await vce.create_ytdl_player("https://www.youtube.com/watch?v=rY-FJvRqK0E")
                    ##player.start()
                    ##return
        else:
            for channel in message.server.channels:
                if channel.name == s:
                    await voiceObject.move_to(channel)
    elif message.content.lower().startswith('!play'):
        print(voiceObject)
        s = message.content[6:]
        #print(client.voice_clients)
        #for object in client.voice_clients:
        player = await voiceObject.create_ytdl_player(s)
        player.start()
    elif message.content.lower().startswith('!leave'):
        print(voiceObject)
        if voiceObject == None:
            await client.send_message(message.channel, 'Bot is not in a channel')
        else:
            player.stop()
            await voiceObject.disconnect()
            player = None
            voiceObject = None
    print('this isa test')
print('this is also a test')
async def createTimer(user):
    await asyncio.sleep(int(config['DEFAULT']['PointCooldown']))
    pointCooldown.remove(user)
async def startPoll(time, options, channel):
    global pollActive
    pollActive = True
    print(pollActive)
    for option in options:
        dic[option] = 0
    await asyncio.sleep(time)
    await stopPoll(channel)
async def stopPoll(channel):
    global dic
    global pollActive
    global hasVoted
    print(pollActive)
    if pollActive == False:
        await client.send_message(channel, 'No polls are currently active')
    else:
        max = 0
        keys = []
        for option in dic:
            if dic[option] > max:
                keys = [option]
                max = dic[option]
            elif dic[option] == max:
                keys.append(option)
        if(len(keys) > 1):
            s = ''
            for i in range(len(keys)):
                if i == len(keys)-1:
                    s += keys[i]
                else:
                    s += keys[i] + ' and '
            await client.send_message(channel, "It's a tie between " + s)
        else:
            await client.send_message(channel, keys[0] + ' has won')
        dic = {}
        hasVoted = []
        pollActive = False
async def checkBlacklist(message):
  for word in blacklist:
        if word in message.content.lower():
            await client.delete_message(message)
            user = message.server.get_member_named(str(message.author))
            await client.send_message(message.channel, str(user.mention) + " please do not use blacklisted words")
            return True
print('this is a test')
client.run(TOKEN)
