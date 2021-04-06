# pelibot.py
import discord
import json
import asyncio
import aiohttp
import requests
from prettytable import PrettyTable
from fuzzywuzzy import process
from disctoken import botToken
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class MyClient(discord.Client):
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())
        self.playerIDs = {}
        self.skcID = 503665006961754113
        self.gamedayID = 787145727846776872
        self.botspamID = 503665658374914069
        self.serverID = 503662263337484310
        self.gamedayRoleID = 828414595680829480
        self.lastRoleID = 825195355670708264
        self.pelsTeamID = '1610612740'
        self.initDict()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    # logic for replying starts here. Can invoke async func from here to keep code clean.
    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!next'):
            # await message.reply('Hello!', mention_author=True)
            # make request for schedule and reply with the next game details.
            year = 2020
            url = "http://data.nba.net/prod/v1/{}/teams/{}/schedule.json".format(year, self.pelsTeamId)
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            statResponse = await session.get(url)
            statBlob = await statResponse.json()
            await session.close()
            data = statBlob['league']['standard'][int(data['league']['lastStandardGamePlayedIndex'])+1]
            # starttime as easter time string
            st = data['startTimeEastern']
            gamecode = data['gameUrlCode'].split('/')
            date = datetime.strptime(gamecode[0], '20%y%m%d')
            opp_tricode = gamecode[1][:3] if gamecode[1][-3:] == 'NOP' else gamecode[1][-3:]
            t = PrettyTable(['OPP', 'DATE', 'TIME'])
            t.add_row([opp_tricode, '{} {}/{}'.format(date.strftime('%a'), date.month, date.day), st])
            embedVar = discord.Embed(title="Next Scheduled Game", description=str(t), color=0x00ff00)
            await message.channel.send(embed=embedVar)
        if message.content.startswith('pb.testping'):
            gamedayRole = message.guild.get_role(self.gamedayRoleID)
            url = 'http://data.nba.net/prod/v1/2020/teams/1610612740/schedule.json'
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            scheduleResponse = await session.get(url)
            scheduleBlob = await scheduleResponse.json()
            await session.close()
            lastPlayed = scheduleBlob['league']['lastStandardGamePlayedIndex']
            game = scheduleBlob['league']['standard'][lastPlayed+1]
            teams = game['gameUrlCode'].split('/')[1]
            if game["isHomeTeam"]:
                atvs =' vs. '
                otherTeamID = game['vTeam']['teamId']
                otherTeamName = teams[0:3]
            else:
                atvs = ' at '
                otherTeamID = game['hTeam']['teamId']
                otherTeamName = teams[3:]

            url = 'http://data.nba.net/prod/v1/current/standings_all.json'
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            standingsResponse = await session.get(url)
            standingsBlob = await standingsResponse.json()
            await session.close()

            teams = standingsBlob['league']['standard']['teams']
            for team in teams:
                if team['teamId'] == self.pelsTeamID:
                    pelsRecord = '('+team['win'] + '-' + team['loss']+')'
                elif team['teamId'] == otherTeamID:
                    otherRecord = '('+team['win'] + '-' + team['loss']+')'
            gameTime = str(int(game["startTimeEastern"].split(':')[0]) - 1)+':'+game['startTimeEastern'].split(':')[1][0:2]+' PM CT'
            if gameTime[0] == '0':
                gameTime = '12' + gameTime[1:]
            embedVar = discord.Embed(title = 'NOP '+pelsRecord + atvs\
                + otherTeamName+ ' '+ otherRecord, description='Today\'s game tips off at '+gameTime, color=0x85714d)
            pelsLogo = discord.File("images/pelslogo.png", filename="pelslogo.png")
            embedVar.set_thumbnail(url="attachment://pelslogo.png")
            await message.channel.send(files=[pelsLogo], embed=embedVar)
            return

        if message.content.startswith('!hello'):
            await message.reply('<:smilezion:608069015646240799>', mention_author=True)
            return
        
        if message.content.startswith('pb.ban'):
            await message.channel.send('<:ban:821817534386536458>')

        if message.content.startswith('pb.last') and message.channel.id == self.botspamID:
            channel = self.get_channel(self.botspamID) # channel ID goes here. this one is botspam.
            await asyncio.sleep(10)
            await channel.set_permissions(channel.guild.default_role, send_messages=False)
            await asyncio.sleep(2)
            lastMessageID = channel.last_message_id
            lastMessage = await channel.fetch_message(lastMessageID)
            lastName = lastMessage.author.mention
            embedVar = discord.Embed(description=channel.mention+' has been locked!', color=0x00ff00)
            await channel.send(embed=embedVar)
            await channel.send(lastName+' got last!')
            embedVar = discord.Embed(description='Go on over to '+self.get_channel(self.skcID).mention, color=0x00ff00)
            await channel.send(embed=embedVar)
            await channel.set_permissions(channel.guild.default_role, send_messages=True)
            #lastRole = message.guild.get_role(825195355670708264)
            #lastMember = lastRole.members[0]
            #await lastMember.remove_roles(lastRole)
            #await lastMessage.author.add_roles(lastRole)
            #await asyncio.sleep(5)
            #await lastMessage.author.remove_roles(lastRole)

        if message.content.startswith('pb.roster'):
            headers = {
                'Host': 'stats.nba.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'x-nba-stats-origin': 'stats',
                'x-nba-stats-token': 'true',
                'Connection': 'keep-alive',
                'Referer': 'https://stats.nba.com/',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
            }
            url = 'https://stats.nba.com/stats/commonteamroster?Season=2020-21&TeamID=1610612740&LeagueID=00'
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            rosterResponse = await session.get(url, headers=headers)
            rosterBlob = await rosterResponse.json()
            await session.close()
            t = PrettyTable(['Name', 'Number', 'Position', 'Height', 'Weight'])
            for player in rosterBlob['resultSets'][0]['rowSet']:
                t.add_row([player[3], '#'+player[5], player[6], player[7], player[8]])
            img = Image.new("RGB", (1, 1), (255, 255, 255))
            d1 = ImageDraw.Draw(img)
            myFont = ImageFont.truetype("fonts/Menlo-Regular.ttf", 12)
            width, height = d1.textsize(t.get_string(border=False), font=myFont)
            img = Image.new("RGB", (width+5, height+5), (255, 255, 255))
            d1 = ImageDraw.Draw(img)
            d1.text((0, 0), t.get_string(border=False), font=myFont, fill =(0, 0, 0))
            img.save("images/rosterText.png")
            file1 = discord.File("images/rosterText.png", filename="rosterText.png")
            file2 = discord.File("images/pelslogo.png", filename="pelslogo.png")
            embed = discord.Embed(title="New Orleans Pelicans \n2020-2021", color=0x85714d)
            embed.set_image(url="attachment://rosterText.png")
            embed.set_thumbnail(url="attachment://pelslogo.png")
            await message.channel.send(files=[file1, file2], embed=embed)
            return

        if message.content.startswith('pb.stats'):
            playerName = message.content.split(" ", 1)[1]
            playerKey = process.extractOne(playerName, self.playerIDs.keys())[0]
            playerID = self.playerIDs[playerKey]
            url = 'http://data.nba.net/prod/v1/2020/players/' + str(playerID) + '_profile.json'
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            statResponse = await session.get(url)
            statBlob = await statResponse.json()
            await session.close()
            stats = statBlob['league']['standard']['stats']['latest']
            t = PrettyTable(['NAME', 'PPG', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'TOV'])
            prettyName = playerKey.split()
            t.add_row([prettyName[0]+' '+prettyName[1][0]+'.', stats['ppg'], stats['fgp'], stats['tpp'], stats['ftp'], stats['rpg'], stats['apg'],\
                stats['spg'], stats['bpg'], stats['topg']])
            img = Image.new("RGB", (1, 1), (255, 255, 255))
            d1 = ImageDraw.Draw(img)
            myFont = ImageFont.truetype("fonts/Menlo-Regular.ttf", 12)
            width, height = d1.textsize(t.get_string(border=False), font=myFont)
            img = Image.new("RGB", (width+5, height+5), (255, 255, 255))
            d1 = ImageDraw.Draw(img)
            d1.text((0, 0), t.get_string(border=False), font=myFont, fill =(0, 0, 0))
            img.save("images/statsText.png")
            file1 = discord.File("images/statsText.png", filename="statsText.png")
            #file2 = discord.File("images/pelslogo.png", filename="pelslogo.png")
            embed = discord.Embed(title=playerKey+"\n2020-21 Stats", color=0x85714d)
            embed.set_thumbnail(url="https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/"+str(playerID)+".png")
            embed.set_image(url="attachment://statsText.png")
            await message.channel.send(files=[file1], embed=embed)
            return

    async def populateDict(self):
        headers = {
            'Host': 'stats.nba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Connection': 'keep-alive',
            'Referer': 'https://stats.nba.com/',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        url = 'https://stats.nba.com/stats/commonteamroster?Season=2020-21&TeamID=1610612740&LeagueID=00'
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        rosterResponse = await session.get(url, headers=headers)
        rosterBlob = await rosterResponse.json()
        await session.close()
        for player in rosterBlob['resultSets'][0]['rowSet']:
            self.playerIDs[player[3]] = player[13]
        return
    
    def initDict(self):
        headers = {
            'Host': 'stats.nba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Connection': 'keep-alive',
            'Referer': 'https://stats.nba.com/',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        url = 'https://stats.nba.com/stats/commonteamroster?Season=2020-21&TeamID=1610612740&LeagueID=00'
        session = requests.Session()
        session.verify = False
        rosterResponse = session.get(url, headers=headers)
        rosterBlob = rosterResponse.json()
        for player in rosterBlob['resultSets'][0]['rowSet']:
            self.playerIDs[player[3]] = player[13]
        return

    # example background task
    async def my_background_task(self):
        await self.wait_until_ready() # task doesnt start until init finishes
        channel = self.get_channel(self.gamedayID) # channel ID goes here. this one is botspam.
        while not self.is_closed():
            url = 'http://data.nba.net/prod/v1/2020/teams/1610612740/schedule.json'
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            scheduleResponse = await session.get(url)
            scheduleBlob = await scheduleResponse.json()
            await session.close()
            lastPlayed = scheduleBlob['league']['lastStandardGamePlayedIndex']
            game = scheduleBlob['league']['standard'][lastPlayed+1]
            date_time_obj = datetime.strptime(game['startTimeUTC'], '%Y-%m-%dT%H:%M:%S.%fZ')
            timeDiff = date_time_obj - datetime.utcnow()
            if timeDiff.seconds < 5400 and timeDiff.days == 0:
                await channel.set_permissions(channel.guild.default_role, send_messages=True)
                embedVar = discord.Embed(description=channel.mention+' has been unlocked!', color=0x00ff00)
                await channel.send(embed=embedVar)
                teams = game['gameUrlCode'].split('/')[1]
                if game["isHomeTeam"]:
                    atvs =' vs. '
                    otherTeamID = game['vTeam']['teamId']
                    otherTeamName = teams[0:3]
                else:
                    atvs = ' at '
                    otherTeamID = game['hTeam']['teamId']
                    otherTeamName = teams[3:]

                url = 'http://data.nba.net/prod/v1/current/standings_all.json'
                session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
                standingsResponse = await session.get(url)
                standingsBlob = await standingsResponse.json()
                await session.close()

                teams = standingsBlob['league']['standard']['teams']
                for team in teams:
                    if team['teamId'] == self.pelsTeamID:
                        pelsRecord = '('+team['win'] + '-' + team['loss']+')'
                    elif team['teamId'] == otherTeamID:
                        otherRecord = '('+team['win'] + '-' + team['loss']+')'
                gameTime = str(int(game["startTimeEastern"].split(':')[0]) - 1)+':'+game['startTimeEastern'].split(':')[1][0:2]+' PM CT'
                if gameTime[0] == '0':
                    gameTime = '12' + gameTime[1:]
                embedVar = discord.Embed(title = 'NOP '+pelsRecord + atvs\
                    + otherTeamName+ ' '+ otherRecord, description='Today\'s game tips off at '+gameTime, color=0x85714d)
                pelsLogo = discord.File("images/pelslogo.png", filename="pelslogo.png")
                embedVar.set_thumbnail(url="attachment://pelslogo.png")
                await channel.send(files=[pelsLogo], embed=embedVar)
                await asyncio.sleep(10800) # 3 hours
                gameEnd = False
                while gameEnd == False:
                    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
                    scheduleResponse = await session.get(url)
                    scheduleBlob = await scheduleResponse.json()
                    await session.close()
                    if scheduleBlob['league']['lastStandardGamePlayedIndex'] != lastPlayed:
                        gameEnd = True
                    else:
                        await asyncio.sleep(120)
                await channel.set_permissions(channel.guild.default_role, send_messages=False)
                await asyncio.sleep(2)
                lastMessageID = channel.last_message_id
                lastMessage = await channel.fetch_message(lastMessageID)
                lastName = lastMessage.author.mention
                embedVar = discord.Embed(description=channel.mention+' has been locked!', color=0x00ff00)
                await channel.send(embed=embedVar)
                await channel.send(lastName+' got last!')
                embedVar = discord.Embed(description='Go on over to '+self.get_channel(self.skcID).mention, color=0x00ff00)
                await channel.send(embed=embedVar)
                lastRole = channel.guild.get_role(self.lastRoleID)
                lastMember = lastRole.members[0]
                await lastMember.remove_roles(lastRole)
                await lastMessage.author.add_roles(lastRole)
                
            await asyncio.sleep(60) # task runs every minute
intents = discord.Intents.default()
intents.members = True
client = MyClient(intents = intents)
client.run(botToken)
