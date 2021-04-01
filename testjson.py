import aiohttp
import asyncio
from datetime import datetime, timezone
from prettytable import PrettyTable

async def requestroster():
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

async def requeststats():
    playerID = 1629627
    url = 'http://data.nba.net/prod/v1/2020/players/' + str(playerID) + '_profile.json'
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    statResponse = await session.get(url)
    statBlob = await statResponse.json()
    await session.close()
    stats = statBlob['league']['standard']['stats']['latest']
    t = PrettyTable(['NAME', 'PPG', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'TOV'])
    #for player in statBlob['resultSets'][0]['rowSet']:
    t.add_row(['Zion Williamson', stats['ppg'], stats['fgp'], stats['tpp'], stats['ftp'], stats['rpg'], stats['apg'],\
        stats['spg'], stats['bpg'], stats['topg']])
    print(str(t))

async def requestschedule():
    url = 'http://data.nba.net/prod/v1/2020/teams/1610612740/schedule.json'
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    scheduleResponse = await session.get(url)
    scheduleBlob = await scheduleResponse.json()
    await session.close()
    lastPlayed = scheduleBlob['league']['lastStandardGamePlayedIndex']
    game = scheduleBlob['league']['standard'][lastPlayed+1]
    print(game['gameUrlCode'])
    print(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z')
    #print(datetime.fromtimestamp(game['gameUrlCode'], tz=timezone.utc))
    #print datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]
    date_time_obj = datetime.strptime(game['startTimeUTC'], '%Y-%m-%dT%H:%M:%S.%fZ')
    print("hello")
    print(game['startTimeUTC'])
    print(datetime.utcnow())
    print(date_time_obj)
    timeDiff = date_time_obj - datetime.utcnow()
    print(timeDiff.seconds - 10800)

if __name__ == "__main__":
    asyncio.run(requestschedule())