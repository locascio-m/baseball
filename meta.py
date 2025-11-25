
def TeamInfo(team:str,info:str):
    if team == "ALL":
        keys = infoDict['TEAMS'].keys()
        if info == "CODES":
            values = [infoDict['TEAMS'][k]['index'] for k in keys]
            return dict(zip(values,keys))
        elif info == "":
            return list(keys)
        else:
            values = [infoDict['TEAMS'][k][info] for k in keys]
            return dict(zip(keys,values))
    else:
        return infoDict['TEAMS'][team][info]

def LeagueInfo(org:str):
    return list(dict.fromkeys([infoDict[org][key]['name'] for key in infoDict[org]]))


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

infoDict = {
    'TEAMS': {
        'TOR': {
            'fullName': "Toronto Blue Jays",
            'index': 141,
            'location': "Toronto",
            'name': "Blue Jays",
            'timeZone': "America/Toronto",
        },
        'NYY': {
            'fullName': "New York Yankees",
            'index': 147,
            'location': "New York",
            'name': "Yankees",
            'timeZone': "America/New_York",
        },
        'BOS': {
            'fullName': "Boston Red Sox",
            'index': 111,
            'location': "Boston",
            'name': "Red Sox",
            'timeZone': "America/New_York",
        },
        'TB': {
            'fullName': "Tampa Bay Rays",
            'index': 139,
            'location': "Tampa Bay",
            'name': "Rays",
            'timeZone': "America/New_York",
        },
        'BAL': {
            'fullName': "Baltimore Orioles",
            'index': 110,
            'location': "Baltimore",
            'name': "Orioles",
            'timeZone': "America/New_York",
        },
        'CLE': {
            'fullName': "Cleveland Guardians",
            'index': 114,
            'location': "Cleveland",
            'name': "Guardians",
            'timeZone': "America/Detroit",
        },
        'DET': {
            'fullName': "Detriot Tigers",
            'index': 116,
            'location': "Detroit",
            'name': "Tigers",
            'timeZone': "America/Detroit",
        },
        'KC': {
            'fullName': "Kansas City Royals",
            'index': 118,
            'location': "Kansas City",
            'name': "Royals",
            'timeZone': "America/Chicago",
        },
        'MIN': {
            'fullName': "Minnesota Twins",
            'index': 142,
            'location': "Minnesota",
            'name': "Twins",
            'timeZone': "America/Chicago",
        },
        'CWS': {
            'fullName': "Chicago White Sox",
            'index': 145,
            'location': "Chicago",
            'name': "White Sox",
            'timeZone': "America/Chicago",
        },
        'SEA': {
            'fullName': "Seattle Mariners",
            'index': 136,
            'location': "Seattle",
            'name': "Mariners",
            'timeZone': "America/Los_Angeles",
        },
        'HOU': {
            'fullName': "Houston Astros",
            'index': 117,
            'location': "Houston",
            'name': "Astros",
            'timeZone': "America/Chicago",
        },
        'TX': {
            'fullName': "Texas Rangers",
            'index': 140,
            'location': "Texas",
            'name': "Rangers",
            'timeZone': "America/Chicago",
        },
        'ATH': {
            'fullName': "Athletics",
            'index': 133,
            'location': "Athletics",
            'name': "Athletics",
            'timeZone': "America/Los_Angeles",
        },
        'LAA': {
            'fullName': "Los Angeles Angels",
            'index': 108,
            'location': "Los Angeles",
            'name': "Angels",
            'timeZone': "America/Los_Angeles",
        },
        'PHI': {
            'fullName': "Philadelphia Phillies",
            'index': 143,
            'location': "Philadelphia",
            'name': "Phillies",
            'timeZone': "America/New_York",
        },
        'NYM': {
            'fullName': "New York Mets",
            'index': 121,
            'location': "New York",
            'name': "Mets",
            'timeZone': "America/New_York",
        },
        'MIA': {
            'fullName': "Miami Marlins",
            'index': 146,
            'location': "Miami",
            'name': "Marlins",
            'timeZone': "America/New_York",
        },
        'ATL': {
            'fullName': "Atlanta Braves",
            'index': 144,
            'location': "Atlanta",
            'name': "Braves",
            'timeZone': "America/New_York",
        },
        'WSH': {
            'fullName': "Washington Nationals",
            'index': 120,
            'location': "Washington",
            'name': "Nationals",
            'timeZone': "America/New_York",
        },
        'MIL': {
            'fullName': "Milwaukee Brewers",
            'index': 158,
            'location': "Milwaukee",
            'name': "Brewers",
            'timeZone': "America/Chicago",
        },
        'CHC': {
            'fullName': "Chicago Cubs",
            'index': 112,
            'location': "Chicago",
            'name': "Cubs",
            'timeZone': "America/Chicago",
        },
        'CIN': {
            'fullName': "Cincinatti Reds",
            'index': 113,
            'location': "Cincinatti",
            'name': "Reds",
            'timeZone': "America/Detroit",
        },
        'STL': {
            'fullName': "St. Louis Cardinals",
            'index': 138,
            'location': "St. Louis",
            'name': "Cardinals",
            'timeZone': "America/Chicago",
        },
        'PIT': {
            'fullName': "Pittsburgh Pirates",
            'index': 134,
            'location': "Pittsburgh",
            'name': "Pirates",
            'timeZone': "America/New_York",
        },
        'LAD': {
            'fullName': "Los Angeles Dodgers",
            'index': 119,
            'location': "Los Angeles",
            'name': "Dodgers",
            'timeZone': "America/Los_Angeles",
        },
        'SD': {
            'fullName': "San Diego Padres",
            'index': 135,
            'location': "San Diego",
            'name': "Padres",
            'timeZone': "America/Los_Angeles",
        },
        'SF': {
            'fullName': "San Francisco Giants",
            'index': 137,
            'location': "San Francisco",
            'name': "Giants",
            'timeZone': "America/Los_Angeles",
        },
        'AZ': {
            'fullName': "Arizona Diamondbacks",
            'index': 109,
            'location': "Arizona",
            'name': "Diamondbacks",
            'timeZone': "America/Phoenix",
        },
        'COL': {
            'fullName': "Colorado Rockies",
            'index': 115,
            'location': "Colorado",
            'name': "Rockies",
            'timeZone': "America/Denver",
        },
    },
    'DIVISIONS': {
        'ALE': {
            'name': "East",
            'index': 201,
        },
        'ALC': {
            'name': "Central",
            'index': 202,
        },
        'ALW': {
            'name': "West",
            'index': 200,
        },
        'NLE': {
            'name': "East",
            'index': 204,
        },
        'NLC': {
            'name': "Central",
            'index': 205,
        },
        'NLW': {
            'name': "West",
            'index': 203,
        },
    },
    'LEAGUES': {
        'AL': {
            'name': "American League",
            'index': 103,
        },
        'NL': {
            'name': "National League",
            'index': 104,
        },
    }
}