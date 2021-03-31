import aiohttp
import asyncio
from prettytable import PrettyTable

async def requesthing():
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
    statResponse = await session.get(url, headers=headers)
    statBlob = await statResponse.json()
    await session.close()
    t = PrettyTable(['Name', 'Number', 'Position', 'Height', 'Weight'])
    for player in statBlob['resultSets'][0]['rowSet']:
        t.add_row([player[3], '#'+player[5], player[6], player[7], player[8]])
    print(str(t))

if __name__ == "__main__":
    asyncio.run(requesthing())