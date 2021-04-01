# pelibot.py
import discord
import asyncio
import aiohttp
from prettytable import PrettyTable
from fuzzywuzzy import process

class MyClient(discord.Client):
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())
        self.playerIDs = {}
        await self.populateDict()
        
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

        if message.content.startswith('!hello'):
            await message.reply('Hello!', mention_author=True)
            return
          
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
            embedVar = discord.Embed(title="Player Stats", description=str(t), color=0x00ff00)
            await message.channel.send(embed=embedVar)
            return

        if message.content.startswith('pb.stats'):
            playerName = message.content.split(" ", 1)[1]
            playerKey = process.extractOne(playerName, playerIDs.keys())[0]
            playerID = self.playerIDs[playerKey]
            url = 'http://data.nba.net/prod/v1/2020/players/' + str(playerID) + '_profile.json'
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
            statResponse = await session.get(url)
            statBlob = await statResponse.json()
            await session.close()
            stats = statBlob['league']['standard']['stats']['latest']
            t = PrettyTable(['NAME', 'PPG', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'TOV'])
            t.add_row([playerKey, stats['ppg'], stats['fgp'], stats['tpp'], stats['ftp'], stats['rpg'], stats['apg'],\
                stats['spg'], stats['bpg'], stats['topg']])
            embedVar = discord.Embed(title="Player Stats", description=str(t), color=0x00ff00)
            await message.channel.send(embed=embedVar)
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

    # example background task
    async def my_background_task(self):
        await self.wait_until_ready() # task doesnt start until init finishes
        channel = self.get_channel(503665006961754113) # channel ID goes here. this one is smoothie king center. TODO add to a dict or something
        while not self.is_closed():
            await channel.send('testing background task')
            await asyncio.sleep(3600) # task runs every hour

client = MyClient()
client.run('token')
