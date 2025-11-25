import pandas
from dateutil.tz import tzlocal

import api
import meta
import json

def Schedule(team:str):
    """
    TODO
    """
    # API Download
    apiData = api.MLBAPIHandler("schedule "+team)['dates']
    df = pandas.json_normalize(apiData,record_path='games',meta='date')
    # Format date and time
    df['date'] = df['date'].str[5:]
    df['gameTime'] = pandas.to_datetime(df['gameDate'],format='%Y-%m-%dT%H:%M:%SZ',utc=True)
    df['gameTime'] = df['gameTime'].dt.tz_convert(tzlocal()).dt.strftime("%H:%M")
    # Gather home/away and opponent
    df['home'] = (df['teams.home.team.id'] == meta.TeamInfo(team,'index'))
    df['opp'] = (df['teams.home.team.id'].mask(df['home'],df['teams.away.team.id'])).map(meta.TeamInfo("ALL","CODES"))
    # Set score for pending game as game time
    df.loc[df['status.abstractGameCode']=='P','score'] = df['gameTime']
    # Set score for finished games
    if 'teams.home.score' in df.columns:
        df['teamScore'] = df['teams.away.score'].mask(df['home'],df['teams.home.score'])
        df['oppScore'] = df['teams.home.score'].mask(df['home'],df['teams.away.score'])
        df['win'] = df.apply(lambda f: 'W' if f['teamScore']>f['oppScore'] else 'L',axis=1)
        df.loc[df['status.abstractGameCode']=='F','score'] = df['win'] + ' ' + df['teamScore'].astype(str) + '-' + df['oppScore'].astype(str)
    # Format home/away and opponent string
    df['game'] = df['home'].map(lambda f: '*' if f else '@').str.cat(df['opp'])
    # Organize for printing
    rowStr = "   ".join([tableDict[key]['str'] for key in tableDict.keys()])
    rows = df[[tableDict[x]['col'] for x in tableDict.keys()]].values.tolist()
    print()
    for row in rows:
        print(rowStr.format(*row))
    print()

def ScheduleCheck(query:list[str]):
    """TODO"""
    if not query:
        print(f"Enter 'schedule' alongside the name of a team: {meta.TeamInfo('ALL','')}")
        return 1, None
    if len(query) > 1:
        print("Too many teams given. Try again.")
        return 2, None
    team = query[0]
    if team not in meta.TeamInfo("ALL",""):
        print(f"The team '{team}' does not exist. Please choose from the following: {meta.TeamInfo('ALL','')}.")
        return 3, None
    else:
        return 0, team
    
# Dictionary defining table fields and formatting
tableDict = {
    'DATE': {
        'col': 'date',
        'str': '{:5}',
    },
    'GAME': {
        'col': 'game',
        'str': '{:<4}',
    },
    'SCORE': {
        'col': 'score',
        'str': '{:<7}',
    },
}