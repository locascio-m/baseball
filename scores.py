import pandas
from datetime import datetime, timedelta
from dateutil.tz import tzlocal

import api
import meta

def Scores(date:str):
    """
    TODO
    """
    # API Download
    apiData = api.MLBAPIHandler("scores "+date)
    df = pandas.json_normalize(apiData,['dates','games']).set_index('gamePk').sort_values(by='gameDate')
    df['teams.home.team.abbreviation'] = df['teams.home.team.id'].map(meta.TeamInfo("ALL","CODES"))
    df['gameTime'] = pandas.to_datetime(df['gameDate'],format='%Y-%m-%dT%H:%M:%SZ',utc=True).dt.tz_convert(tzlocal()).dt.strftime("%H:%M")
    # Format game status and score (if available)
    df = df.groupby('status.abstractGameCode').apply(_gameState)
    rowStr = " ".join([tableDict[key]['str'] for key in tableDict.keys()])
    home = df[[tableDict[x]['col'].format('home') for x in ['TEAM','SCORE','CODE']]].values.tolist()
    away = df[[tableDict[x]['col'].format('away') for x in ['TEAM','SCORE','CODE']]].values.tolist()
    print()
    for ii in range(len(home)):
        print(rowStr.format(*away[ii]))
        print(rowStr.format(*home[ii]))
        print()

def ScoresCheck(query:list[str]):
    """TODO"""
    if len(query) > 1:
        print("Too many dates given. Try again.")
        return 1, None
    if not query:
        date = "today"
    else:
        date = query[0]
    if (date == "today") or (date == "tonight"):
        date = datetime.now().date
    elif date == "yesterday":
        date = datetime.now().date - timedelta(days=1)
    elif date == "tomorrow":
        date = datetime.now().date + timedelta(days=1)
    else:
        if len(date) == 5:
            date = str(datetime.now().year) + "-" + date
        try:
            datetime.strptime(date,"%Y-%m-%d")
        except:
            print("Invalid date given. Please supply the date as YYYY-MM-DD or MM-DD.")
            return 2, None
    return 0, date

def _gameState(group):
    # TODO: fix function
    if group['status.abstractGameCode'].iloc[0] == 'P':
        group.loc[:,['teams.away.code','teams.home.score','teams.away.score']] = ' '
        group['teams.home.code'] = group['gameTime']
    elif group['status.abstractGameCode'].iloc[0] == 'F':
        c = group['teams.home.score'] > group['teams.away.score']
        group.loc[c,'teams.home.code'] = '<'
        group.loc[c,'teams.away.code'] = 'F'
        group.loc[~c,'teams.home.code'] = 'F'
        group.loc[~c,'teams.away.code'] = '<'
    return group

# Dictionary defining table fields and formatting
tableDict = {
    'TEAM': {
        'col': 'teams.{}.team.name',
        'str': '{:<22}',
    },
    'SCORE': {
        'col': 'teams.{}.score',
        'str': '{:>2}',
    },
    'CODE': {
        'col': 'teams.{}.code',
        'str': '{:<2}',
    },
}

# if __name__ == "__main__":
#     # Schedule("2025-06-17")
#     Scores("2026-03-27")