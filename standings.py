import pandas

import api
import meta

def Standings(form:str):
    """
    TODO
    """
    # API Download TODO: clinch indicator/eliminationNumber, splitRecords
    apiData = api.MLBAPIHandler("standings")
    df = pandas.json_normalize(
        apiData,
        ['records','teamRecords'],
    ).set_index('team.id')
    # Organize split records
    dfr = pandas.json_normalize(
        apiData,
        ['records','teamRecords','records','splitRecords'],
        [['records','teamRecords','team']],
    )
    dfr['team.id'] = [d['id'] for d in dfr['records.teamRecords.team']]
    dfr = dfr.loc[dfr['type'].isin(splitRecords),:].drop(columns=['records.teamRecords.team'])
    dfr = dfr.groupby('team.id').apply(lambda f: f.set_index('type').astype(str),include_groups=False)
    dfr = (dfr['wins']+"-"+dfr['losses']).unstack()
    df = df.join(dfr).drop(columns=['records.splitRecords','records.divisionRecords','records.overallRecords','records.leagueRecords','records.expectedRecords'])
    # Calculate other basic statistics
    df['winningPercentage'] = (df['wins'] / df[['wins','losses']].sum(axis=1)).map(lambda x: f"{x:.3f}".lstrip('0'))
    df['runDifferential'] = (df['runsScored'] - df['runsAllowed']).map(lambda x: f"{x:+d}")
    # Calculate division games back
    df['divisionRank'] = df['divisionRank'].astype(int)
    df['gamesBack'] = df.groupby('team.division.abbreviation',group_keys=False).apply(lambda f: (f.loc[f['divisionRank'].idxmin(),'wins'] - f['wins'])/2 + (f['losses'] - f.loc[f['divisionRank'].idxmin(),'losses'])/2,include_groups=False).astype(str)
    df.loc[df['divisionRank']==1,'gamesBack'] = '-'
    # Calculate wild card games back
    c = df.loc[df['wildCardRank'].isna()].sort_values(by=['team.league.name','winningPercentage'],ascending=[True,False]).index
    df.loc[c,'wildCardRank'] = [-3,-2,-1,-3,-2,-1]
    df['wildCardRank'] = df['wildCardRank'].astype(int)
    c = df['wildCardRank']>0
    df.loc[c,'wildCardGamesBack'] = df.groupby('team.league.name',group_keys=False).apply(lambda f: (f.loc[f['wildCardRank']==3,'wins'].values - f['wins'])/2 + (f['losses'] - f.loc[f['wildCardRank']==3,'losses'].values)/2,include_groups=False).map(lambda x: f"{x:.1f}" if x >=0 else f"{-x:+.1f}")
    df.loc[~c,'wildCardGamesBack'] = 'NaN'
    df.loc[df['wildCardRank']==3,'wildCardGamesBack'] = '-'
    # Organize fields for printing
    fields = list(tableDict.keys())
    rowStr = "  ".join([tableDict[key]['str'] for key in fields])
    # Print by league and either by division or by wild card position
    print()
    for league in meta.LeagueInfo("LEAGUES"):
        print(league.upper())
        match form:
            case "division":
                tableDict['GB']['col'] = 'gamesBack'
                for division in meta.LeagueInfo("DIVISIONS"):
                    print(division.upper()+rowStr.format(*fields)[len(division):])
                    standings = df.loc[(df['team.league.name']==league)&(df['team.division.name']==" ".join([league,division])),[tableDict[key]['col'] for key in fields]].astype(str)
                    rows = [[*standings.values.tolist()[i]] for i in range(len(standings))]
                    for row in rows:
                        print(rowStr.format(*row))
                    print()
            case "wildcard":
                tableDict['GB']['col'] = 'wildCardGamesBack'
                nd = len(meta.LeagueInfo("DIVISIONS"))
                standings = df.loc[df['team.league.name']==league].sort_values(by='wildCardRank',ascending=True)[[tableDict[key]['col'] for key in fields]].astype(str)
                d = standings.iloc[:nd].index
                standings.loc[d,'wildCardGamesBack'] = df.loc[d,'team.division.abbreviation'].str[-1]
                rows = [[*standings.values.tolist()[i]] for i in range(len(standings))]
                print("LEADERS"+rowStr.format(*['DIV' if s == 'GB' else s for s in fields])[7:])
                for row in rows[:nd]:
                    print(rowStr.format(*row))
                print()
                print("WILD CARD"+rowStr.format(*fields)[9:])
                for row in rows[nd:]:
                    print(rowStr.format(*row))
                print()
    return 0

def StandingsCheck(query:list[str]):
    """TODO"""
    if ("division" in query) or ("divisional" in query) or (not query):
        return 0, "division"
    elif ("wildcard" in query) or ("wild" in query and "card" in query):
        return 0, "wildcard"
    else:
        print("Standings format is not valid. Try either 'division' or 'wildcard'.")
        return 1, None

# Dictionary defining table fields and formatting
tableDict = {
    'T': {
        'col': 'team.name',
        'str': '{:<22}',
    },
    'W': {
        'col': 'wins',
        'str': '{:>3}',
    },
    'L': {
        'col': 'losses',
        'str': '{:>3}',
    },
    'PCT': {
        'col': 'winningPercentage',
        'str': '{:>4}',
    },
    'GB': {
        'col': '',
        'str': '{:>4}',
    },
    'L10': {
        'col': 'lastTen',
        'str': '{:>4}',
    },
    'STRK': {
        'col': 'streak.streakCode',
        'str': '{:>4}',
    },
    'RS': {
        'col': 'runsScored',
        'str': '{:>5}',
    },
    'RA': {
        'col': 'runsAllowed',
        'str': '{:>4}',
    },
    'DIFF': {
        'col': 'runDifferential',
        'str': '{:>4}',
    },
}
# List of split record types
splitRecords = ['home','away','left','right','lastTen','winners']