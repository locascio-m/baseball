import requests
from datetime import datetime

import meta

# https://statsapi.mlb.com/api/v1/teams/stats?group=hitting&sportIds=1
# game play by play: 'game/{game_id}/playByPlay'
# game line score: 'game/{game_id}/linescore'
# game box score: 'game/{game_id}/boxscore'
# stat types: https://statsapi.mlb.com/api/v1/statTypes
# stat groups: hitting, pitching, fielding, catching, running (https://statsapi.mlb.com/api/v1/statGroups)
# example: https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&teamId=119
# 'teams/{team_id}/stats'
# roster: 'teams/{team_id}/roster
# roster types: 40man, 
# https://statsapi.mlb.com/api/v1/standingsTypes
# New stats via roster:
# https://statsapi.mlb.com/api/v1/teams/137/roster?rosterType=fullSeason&hydrate=person(stats(group=[hitting,pitching,fielding],type=[season],sportId=1))
# https://statsapi.mlb.com/api/v1/teams/137/roster?rosterType=Active&hydrate=person(stats(group=[hitting],type=[season],sportId=1)) 
# https://statsapi.mlb.com/api/v1/teams/111/roster?rosterType=Active&season=2023&hydrate=person(stats(group=[pitching],type=[vsTeamTotal],opposingTeamId=147,season=2023,sportId=1))
# https://statsapi.mlb.com/api/v1/standings?standingsType=regularSeason&hydrate=standings(leagueId=103)'
# team schedule
# https://statsapi.mlb.com/api/v1/schedule?teamId={}&sportId=1&startDate=2026-01-01&endDate=2026-12-31

# TODO: reorganize how index is stored and read
# indexDict = {
#     'AL': 103,
#     'NL': 104,
#     'DIVISIONS': {
#         'ALE': 201,
#         'ALC': 202,
#         'ALW': 200,
#         'NLE': 204,
#         'NLC': 205,
#         'NLW': 203,
#     },
#     'TEAMS': {
#         'TOR': 141,
#         'NYY': 147,
#         'BOS': 111, 
#         'TB':  139,
#         'BAL': 110,
#         'CLE': 114,
#         'DET': 116,
#         'KC':  118,
#         'MIN': 142,
#         'CWS': 145,
#         'SEA': 136,
#         'HOU': 117,
#         'TEX': 140,
#         'ATH': 133,
#         'LAA': 108,
#         'PHI': 143,
#         'NYM': 121,
#         'MIA': 146,
#         'ATL': 144,
#         'WSH': 120,
#         'MIL': 158,
#         'CHC': 112,
#         'CIN': 113,
#         'STL': 138,
#         'PIT': 134,
#         'LAD': 119,
#         'SD':  135,
#         'SF':  137,
#         'AZ':  109,
#         'COL': 115,
#     },
# }
# nameDict = {
#     'LEAGUES': [
#         "American League",
#         "National League",
#     ],
#     'DIVISIONS': [
#         "East",
#         "Central",
#         "West",
#     ],
#     'TEAMS': {
#         'TOR': 'Toronto Blue Jays',
#         'NYY': 'New York Yankees',
#         'BOS': 'Boston Red Sox', 
#         'TB':  'Tampa Bay Rays',
#         'BAL': 'Baltimore Orioles',
#         'CLE': 'Cleveland Guardians',
#         'DET': 'Detriot Tigers',
#         'KC':  'Kansas City Royals',
#         'MIN': 'Minnesota Twins',
#         'CWS': 'Chicago White Sox',
#         'SEA': 'Seattle Mariners',
#         'HOU': 'Houston Astros',
#         'TEX': 'Texas Rangers',
#         'ATH': 'Las Vegas Athletics',
#         'LAA': 'Los Angeles Angels',
#         'PHI': 'Philadelphia Phillies',
#         'NYM': 'New York Mets',
#         'MIA': 'Miami Marlins',
#         'ATL': 'Atlanta Braves',
#         'WSH': 'Washington Nationals',
#         'MIL': 'Milwaukee Brewers',
#         'CHC': 'Chicago Cubs',
#         'CIN': 'Cincinatti Reds',
#         'STL': 'St. Louis Cardinals',
#         'PIT': 'Pittsburgh Pirates',
#         'LAD': 'Los Angeles Dodgers',
#         'SD':  'San Diego Padres',
#         'SF':  'San Francisco Giants',
#         'AZ':  'Arizona Diamondbacks',
#         'COL': 'Colorado Rockies',
#     }
# }

urlDict = {
    'standings': 'https://statsapi.mlb.com/api/v1/standings',
    'roster': 'https://statsapi.mlb.com/api/v1/teams/{}/roster',
    'schedule': 'https://statsapi.mlb.com/api/v1/schedule',
    # 'statisticsMLB': 'https://statsapi.mlb.com/api/v1/teams/stats?group={}&sportId=1',
    # 'statisticsTEAM': 'https://statsapi.mlb.com/api/v1/teams/{}/roster'
}

urlParams = {
    "standings": {
        "leagueId": "103,104",
        # "season": datetime.now().year,
        "standingsType": "regularSeason",
        "hydrate": "team(division)",
        "fields": "records,teamRecords,team,id,league,division,name,abbreviation,nameShort,streak,streakCode,wins,losses,gamesPlayed,divisionRank,wildCardRank,runsScored,runsAllowed,type"
    },
    "statisticsTEAM": {
        "rosterType": "fullSeason",
        # "season": datetime.now().year,
        "hydrate": "person(stats(group={},type=season,sportId=1))",
    },
    "roster": {
        "rosterType": "40man",
        # "rosterTypes": "40man,coach",
        # "rosterType": "coach",
        "hydrate": "person(stats)",
        "fields": "roster,jerseyNumber,person,id,fullName,firstName,lastName,birthDate,currentAge,height,weight,batSide,pitchHand,code,position,abbreviation,type"
    },
    "staff": {
        "rosterType": "coach",
        # "fields": "roster,jerseyNumber,person,id,fullName,firstName,lastName,birthDate,currentAge,height,weight,batSide,pitchHand,code,position,abbreviation,type"
    },
    "schedule": {
        "sportId": 1,
        "gameTypes": "R",
        "teamId": "{}",
        "startDate": "{}-01-01",
        "endDate": "{}-12-31"
        # "fields": "dates,games,gameDate,gamePk,status,statusCode,codedGameState,abstractGameState,abstractGameCode,teams,away,home,team,id,name,leagueRecord,wins,losses,score,venue,name"
    },
    "scores": {
        # "date": "2025-06-20",
        # "date": datetime.now().date,
        "sportId": 1,
        "fields": "dates,games,gameDate,gamePk,status,statusCode,codedGameState,abstractGameState,abstractGameCode,teams,away,home,team,id,name,leagueRecord,wins,losses,score,venue,name"
    }
}

def MLBAPIHandler(query):
    query = query.split()
    if query[0] == 'standings':
        url = urlDict['standings']
        params = urlParams['standings']
    elif query[0] == 'statistics':
        url = urlDict['roster'].format(meta.TeamInfo(query[1],'index'))
        params = dict(urlParams['statisticsTEAM'])
        params['hydrate'] = params['hydrate'].format(query[2])
    elif query[0] == 'roster':
        url = urlDict['roster'].format(meta.TeamInfo(query[1],'index'))
        params = urlParams['roster']
    elif query[0] == 'staff':
        url = urlDict['roster'].format(meta.TeamInfo(query[1],'index'))
        params = urlParams['staff']
    elif query[0] == 'scores':
        url = urlDict['schedule']
        params = dict(urlParams['scores'])
        params['date'] = query[1]
    elif query[0] == 'schedule':
        url = urlDict['schedule']
        params = dict(urlParams['schedule'])
        params['teamId'] = params['teamId'].format(meta.TeamInfo(query[1],'index'))
        params['startDate'] = params['startDate'].format(datetime.now().year)
        params['endDate'] = params['endDate'].format(datetime.now().year)
    else:
        KeyError(f'API request not formatted correctly: {query}')
    # response = requests.get(url)
    response = requests.get(url,params=params)
    if response.status_code != 200:
        raise APIError(f'Error fetching data: {response.status_code}')
    data = response.json()
    return data

# def MLBIndex(name):
#     if name in indexDict:
#         return indexDict[name]
#     elif name in indexDict['TEAMS']:
#         return indexDict['TEAMS'][name]
#     elif name in indexDict['DIVISIONS']:
#         return indexDict['DIVISIONS'][name]
#     elif name == "CODES":
#         return {v:k for k,v in indexDict['TEAMS'].items()}
#     else:
#         KeyError('MLB Numeric Index not found')

# def MLBNames(name):
#     if name in nameDict:
#         return nameDict[name]
#     elif name in nameDict['TEAMS']:
#         return nameDict['TEAMS'][name]
#     else:
#         KeyError('MLB Name not found')

class APIError(Exception):
    """
    TODO
    """
    pass
