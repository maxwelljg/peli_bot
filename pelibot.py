# pelibot.py
import discord
import asyncio
import aiohttp

class MyClient(discord.Client):
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())
        
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
            url = 'https://stats.nba.com'
            session = aiohttp.ClientSession()
            statResponse = await session.get(url, headers=headers)
            statBlob = await statResponse.json()
            session.close()
    
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
