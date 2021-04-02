# pelibot.py
import discord
import json
import asyncio
import aiohttp
import requests
from prettytable import PrettyTable
from fuzzywuzzy import process
from disctoken import botToken

class MyClient(discord.Client):
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())
		self.initDict()
		self.teamId = '1610612740'
        
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
			url = "http://data.nba.net/prod/v1/{}/teams/{}/schedule.jsob".format(year, self.teamId)
			session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
			statResponse = await session.get(url)
			statBlob = await statResponse.json()
            await session.close()
			data = ['league']['standard'][int(data['league']['lastStandardGamePlayedIndex'])+1]
            st = datetime.datetime(data['startTimeEastern'])
            gamecode = data['gameUrlCode'].split('/')
            date = datetime.datetime.strptime(gamecode[0], '20%y%m%d')
            opp_tricode = gamecode[1][:3] if gamecode[1][-3:] == 'NOP' else gamecode[1][-3:]
            t = PrettyTable(['OPP', 'DATE', 'TIME'])
            t.add_row([opp_tricode, '{} {}/{}'.format(date.strftime('%a'), data[1],date[2]), st])
            embedVar = discord.Embed(title="Next Scheduled Game", description=str(t), color=0x00ff00)
            await message.channel.send(embed=embedVar)
            return
  
    # example background task
    async def my_background_task(self):
        await self.wait_until_ready() # task doesnt start until init finishes
        channel = self.get_channel(503665006961754113) # channel ID goes here. this one is smoothie king center. TODO add to a dict or something
        while not self.is_closed():
            counter += 1
            await channel.send('testing background task')
            await asyncio.sleep(3600) # task runs every hour

client = MyClient()
client.run('token')
