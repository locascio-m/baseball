import pandas

import api
import meta

def Roster(team:str):
    """
    TODO
    """
    # API Download (coaches) TODO: sort coaches
    apiData = api.MLBAPIHandler(' '.join(['staff',team]))['roster']
    dfc = pandas.json_normalize(apiData).set_index('person.id')[['jerseyNumber','job','jobId','person.fullName']].astype(str)
    dfc = dfc.loc[dfc['job'].isin(staff_list),['person.fullName','job']]
    # API Download (roster)
    apiData = api.MLBAPIHandler(' '.join(['roster',team]))['roster']
    df = pandas.json_normalize(apiData).set_index('person.id').astype(str)
    df['jerseyNumber'] = [int(s) if s else pandas.NA for s in df['jerseyNumber']]
    df = df.sort_values(by=['position.type','jerseyNumber'],ascending=[True,True]).astype(str)
    # Clean up data
    df['jerseyNumber'] = df['jerseyNumber'].str.replace('<NA>','-')
    df['person.batThrow'] = df['person.batSide.code'] + '/' + df['person.pitchHand.code']
    df['person.height'] = df['person.height'].str.replace(" ", "")
    # Format and print rows
    fields_player = list(tableDict['players'].keys())
    fields_staff = list(tableDict['staff'].keys())
    print()
    print(meta.TeamInfo(team,'fullName').upper())
    staff = dfc[[tableDict['staff'][key]['col'] for key in fields_staff]]
    rows = [[*staff.values.tolist()[i]] for i in range(len(staff))]
    rowStr = "  ".join([tableDict['staff'][key]['str'] for key in fields_staff])
    for row in rows:
        print(rowStr.format(*row))
    print()
    for position in ["CATCHER","INFIELDER","OUTFIELDER","PITCHER"]:
        roster = df.loc[df['position.type'] == position.capitalize(),[tableDict['players'][key]['col'] for key in fields_player]]
        rows = [[*roster.values.tolist()[i]] for i in range(len(roster))]
        rowStr = "  ".join([tableDict['players'][key]['str'] for key in fields_player])
        print(position+"S"+rowStr.format(*fields_player)[len(position)+1:])
        for row in rows:
            print(rowStr.format(*row))
        print()
    return 0

def RosterCheck(query:list[str]):
    """TODO"""
    if not query:
        print(f"Enter 'roster' alongside the name of a team: {meta.TeamInfo('ALL','')}")
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
    "players": {
        '#': {
            'col': 'jerseyNumber',
            'str': '{:>2}',
        },
        'N': {
            'col': 'person.lastName',
            'str': '{:<15}',
        },
        'B/T': {
            'col': 'person.batThrow',
            'str': '{:>3}',
        },
        'HT': {
            'col': 'person.height',
            'str': '{:>5}',
        },
        'WT': {
            'col': 'person.weight',
            'str': '{:>3}',
        },
        'YR': {
            'col': 'person.currentAge',
            'str': '{:>2}',
        },
    },
    "staff": {
        'J': {
            'col': 'job',
            'str': '{:<16}',
        },
        'N': {
            'col': 'person.fullName',
            'str': '{:>22}',
        },
    },
}
# List of primary staff roles
staff_list = [
    "Manager",
    "Bench Coach",
    "Hitting Coach",
    "Pitching Coach",
    "Bullpen Coach",
    "Third Base Coach",
    "First Base Coach",
]