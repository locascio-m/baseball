import pandas

import api
import meta

def Statistics(teamGroup:str,help=False):
    """
    TODO
    """
    team, group = teamGroup.split()
    # API Download
    apiData = api.MLBAPIHandler(' '.join(['statistics',team,group]))['roster']
    # Fill in missing stats data (to enable json_normalize)
    for i, d in enumerate(apiData):
        if 'stats' not in d['person']:
            apiData[i]['person']['stats'] = [{'splits': [{}]}]
    df = pandas.json_normalize(
        apiData,
        ['person','stats','splits'],
        meta = [
            ['person','id'],
            ['person','lastName'],
            ['position'],
            ['jerseyNumber'],
        ],
    )
    df['person.position'] = [d['abbreviation'] for d in df['position']]
    # Filter for desired statistics with this team
    df = df.loc[df['team.id']==meta.TeamInfo(team,'index'),apiDict['all']+apiDict[group]].set_index('person.id')
    match group:
        case "hitting":
            # Sort by PA
            df = df.loc[df['stat.plateAppearances']>=9,:].sort_values(by='stat.plateAppearances',ascending=False)
            # Convert all basic stats to integers
            df[apiDict[group]] = df[apiDict[group]].astype(int)
            # Define new earned bat metric
            df['stat.earnedBats'] = df[['stat.atBats','stat.baseOnBalls','stat.sacFlies']].sum(axis=1)
            # Calculate advanced stats and format as strings
            dfx = pandas.DataFrame()
            dfx['stat.onBasePercentage'] = (df['stat.hits'] + df['stat.baseOnBalls']) / df['stat.earnedBats']
            dfx['stat.totalBasePercentage'] = (df['stat.totalBases'] + df['stat.baseOnBalls']) / df['stat.earnedBats']
            dfx['stat.runsBattedPercentage'] = df['stat.rbi'] / df['stat.earnedBats']
            dfx['stat.strikeOutPercentage'] = df['stat.strikeOuts'] / df['stat.earnedBats']
            dfx['stat.leftOnBasePercentage'] = df['stat.leftOnBase'] / df['stat.earnedBats']
            dfx = dfx.map(lambda x: f"{x:.3f}".lstrip('0'))
            df = df.join(dfx)
        case "pitching":
            # Sort by BF and classify starters and relievers
            df = df.loc[(df['person.position']=='P') & (df['stat.outs']>=9),:].sort_values(by='stat.battersFaced',ascending=False)
            df['person.position'] = df.apply(lambda f: 'SP' if f['stat.gamesStarted'] > f['stat.gamesFinished'] else 'RP',axis=1)
            # Convert all basic stats to integers
            df[apiDict[group]] = df[apiDict[group]].astype(int)
            # Define new pitched bats metric
            df['stat.pitchedOuts'] =  df[['stat.strikeOuts','stat.groundOuts','stat.airOuts',]].sum(axis=1)
            df['stat.pitchedBats'] = df[['stat.pitchedOuts','stat.hits','stat.baseOnBalls','stat.hitByPitch']].sum(axis=1)
            # Calculate basic stats
            df['stat.inningsPitched'] = df['stat.outs'].astype(int).map(lambda x: '.'.join(str(i) for i in divmod(x,3)))
            df['stat.allSaves'] = df['stat.saves'] + df['stat.holds']
            df['stat.leftOnBase'] = df[['stat.hits','stat.baseOnBalls','stat.hitByPitch']].sum(axis=1) - df['stat.runs']
            # Calculate advanced stats and format as strings
            dfx = pandas.DataFrame()
            dfx['stat.strikeRate'] = df['stat.strikes'] / df['stat.numberOfPitches']
            dfx['stat.strikeOutPercentage'] = df['stat.strikeOuts'] / df['stat.pitchedBats']
            dfx['stat.groundOutPercentage'] = df['stat.groundOuts'] / df['stat.pitchedBats']
            dfx['stat.airOutPercentage'] = df['stat.airOuts'] / df['stat.pitchedBats']
            dfx['stat.baseOnBallsPercentage'] = df[['stat.baseOnBalls','stat.hitByPitch']].sum(axis=1) / df['stat.pitchedBats']
            dfx['stat.totalBasePercentage'] = df[['stat.totalBases','stat.baseOnBalls','stat.hitByPitch']].sum(axis=1) / df['stat.pitchedBats']
            dfx['stat.earnedRunRate'] = 3 * df['stat.earnedRuns'] / df['stat.outs']
            dfx['stat.failedAppearanceRate'] = df[['stat.blownSaves','stat.losses']].sum(axis=1)/df['stat.gamesPitched']
            dfx = dfx.map(lambda x: f"{x:.3f}".lstrip('0'))
            dfx['stat.leftOnBaseRate'] = (3 * df['stat.leftOnBase'] / df['stat.outs']).map(lambda x: f"{x:.2f}")
            df = df.join(dfx)
        case "fielding":
            # Extract pitching and catching stats
            dfp = df.loc[(df['person.position']=='P') & (~pandas.isna(df['stat.wildPitches'])),['stat.wildPitches','stat.pickoffs']].astype(int)
            dfc = df.loc[(df['person.position']!='P') & (~pandas.isna(df['stat.passedBall'])),['stat.passedBall','stat.caughtStealing','stat.stolenBases','stat.pickoffs']].astype(int).rename(columns={'stat.passedBall': 'stat.wildPitches'})
            df = df.drop(columns=apiDict['pitchingCatching'])
            # Filter by chances
            df = df.loc[df['stat.chances']>1,:]
            # Collect metadata from each player in separate dataframe (excluding person.id index)
            df_meta = df[apiDict['all'][1:]].astype(str).drop_duplicates()
            # Sum each player's fielding statistics across all positions TODO: fix how this lambda is implemented
            df['stat.outs'] = df['stat.innings'].map(lambda x: 3*int(str(x).partition('.')[0])+int(str(x).partition('.')[2]))
            df = df.groupby('person.id')[[f for f in apiDict[group] if f not in apiDict['pitchingCatching']]+['stat.outs']].agg(lambda x: x.sum() if pandas.api.types.is_numeric_dtype(x) else '/'.join(x))
            df_meta['person.position'] = df['position.abbreviation'].map(lambda f: '/'.join((f.split('/')[:2]+['UT'])) if len(f.split('/'))>3 else f).astype(str)
            df = df_meta.join(df.drop(columns=['position.abbreviation','stat.innings']).astype(int))
            df['stat.innings'] = df['stat.outs'].astype(int).map(lambda x: '.'.join(str(i) for i in divmod(x,3)))
            # Sort by innings fielded
            df = df.sort_values(by='stat.outs',ascending=False)
            # Calculate advanced statistics
            df['stat.fieldingPercentage'] = (df[['stat.putOuts','stat.assists']].sum(axis=1) / df['stat.chances']).map(lambda x: f"{x:.3f}")
            df['stat.fieldingRate'] = (3*df[['stat.putOuts','stat.assists']].sum(axis=1) / df['stat.outs']).map(lambda x: f"{x:.2f}")
            dfc['stat.caughtStealingPercentage'] = (dfc['stat.caughtStealing']/dfc[['stat.stolenBases','stat.caughtStealing']].sum(axis=1)).map(lambda x: f"{x:.3f}".lstrip('0') if not pandas.isna(x) else '-')
            # Format as strings and join fielding stats with pitcher and catcher stats
            df = df.astype(str).join(pandas.merge(dfp.astype(str),dfc.astype(str),how='outer',on=['person.id','stat.wildPitches','stat.pickoffs'])).fillna('-')
    # Customize fields depending on type of standings
    fields_all = list(tableDict["all"].keys())
    fields_group = list(tableDict[group].keys())
    statistics = df[[tableDict["all"][key]['col'] for key in fields_all]+[tableDict[group][key]['col'] for key in fields_group]].astype(str)
    rows = [[*statistics.values.tolist()[i]] for i in range(len(statistics))]
    # Format and print rows
    rowStr = "  ".join([tableDict["all"][key]['str'] for key in fields_all]+[tableDict[group][key]['str'] for key in fields_group])
    print()
    print(meta.TeamInfo(team,'fullName').upper())
    print(group.upper()+rowStr.format(*(fields_all+fields_group))[len(group):])
    for row in rows:
        print(rowStr.format(*row))
    print()
    return 0

def StatisticsCheck(query:list[str]):
    """TODO"""
    group = [x for x in query if x in list(tableDict.keys())[1:]]
    if not group:
        print(f"Incorrect statistics type provided. Please enter 'statistics' along with one of the following: {list(tableDict.keys())[1:]}.")
        return 1, None
    elif len(group) > 1:
        print("Too many statistics types were provided. Try again.")
        return 2, None
    group = group[0]
    query.remove(group)
    if not query:
        print(f"Enter 'statistics' and statistics type alongside the name of a team: {meta.TeamInfo('ALL','')}")
        return 6, None
    elif query[0] == "help":
        print(f"Output {group} statistics for each player over the current season.")
        fields = list(tableDict[group].keys())
        info = [tableDict[group][f]['help'] for f in fields]
        for f in range(len(fields)):
            print("    -- " + fields[f] + " " + info[f])
        print()
        return 3, None
    if len(query) > 1:
        print("Too many teams given. Try again.")
        return 4, None
    team = query[0]
    if team not in meta.TeamInfo("ALL",""):
        print(f"The team '{team}' does not exist. Please choose from the following: {meta.TeamInfo('ALL','')}.")
        return 5, None
    else:
        return 0, team + " " + group

# Dictionary mapping our dataframe columms to MLB API fields
apiDict = {
    'all': [
        'person.id',
        'person.lastName',
        'person.position',
        'jerseyNumber',
    ],
    'hitting': [
        'stat.gamesPlayed',
        'stat.plateAppearances',
        'stat.atBats',
        'stat.hits',
        'stat.homeRuns',
        'stat.totalBases',
        'stat.baseOnBalls',
        'stat.strikeOuts',
        'stat.sacFlies',
        'stat.rbi',
        'stat.leftOnBase',
        'stat.stolenBases',
        'stat.runs',
    ],
    'pitching': [
        'stat.gamesPitched',
        'stat.gamesStarted',
        'stat.gamesFinished',
        'stat.battersFaced',
        'stat.outs',
        'stat.strikeOuts',
        'stat.groundOuts',
        'stat.airOuts',
        'stat.hits',
        'stat.totalBases',
        'stat.baseOnBalls',
        'stat.hitByPitch',
        'stat.numberOfPitches',
        'stat.strikes',
        'stat.runs',
        'stat.earnedRuns',
        'stat.wins',
        'stat.losses',
        'stat.saves',
        'stat.holds',
        'stat.blownSaves',
    ],
    'fielding': [
        'position.abbreviation',
        'stat.assists',
        'stat.putOuts',
        'stat.errors',
        'stat.chances',
        'stat.doublePlays',
        'stat.innings',
        'stat.caughtStealing',
        'stat.stolenBases',
        'stat.passedBall',
        'stat.wildPitches',
        'stat.pickoffs',
    ],
    'pitchingCatching': [
        'stat.wildPitches',
        'stat.passedBall',
        'stat.caughtStealing',
        'stat.stolenBases',
        'stat.pickoffs',
    ],
}
# Dictionary defining table fields and formatting
tableDict = {
    "all": {
        '#': {
            'col': 'jerseyNumber',
            'str': '{:>2}',
        },
        'N': {
            'col': 'person.lastName',
            'str': '{:<15}',
        },
    },
    "hitting": {
        'POS': {
            'col': 'person.position',
            'str': '{:>3}',
            'help': "(Primary Position)",
        },
        'H': {
            'col': 'stat.hits',
            'str': '{:>5}',
            'help': "(Hits): count of times player reached base on a ball in play that did not result in an out or error",
        },
        'TB': {
            'col': 'stat.totalBases',
            'str': '{:>3}',
            'help': "(Total Bases): hit count weighted by the number of bases resulting from each hit",
        },
        'BB': {
            'col': 'stat.baseOnBalls',
            'str': '{:>3}',
            'help': "(Base-on-Balls): count of times player was awarded a base after collecting four balls in a plate appearance",
        },
        'R': {
            'col': 'stat.runs',
            'str': '{:>3}',
            'help': "(Runs): count of times player scored a run by crossing home plate",
        },
        'RBI': {
            'col': 'stat.rbi',
            'str': '{:>3}',
            'help': "(Runs-Batted-In): count of times player's plate appearance resulted in a run being scored, neglecting defensive errors",
        },
        'HR': {
            'col': 'stat.homeRuns',
            'str': '{:>2}',
            'help': "(Home Runs): count of times player hit for four bases in one plate appearance",
        },
        'SB': {
            'col': 'stat.stolenBases',
            'str': '{:>2}',
            'help': "(Stolen Bases): count of times player advanced a base as a runner without the ball being put into play",
        },
        'OBP': {
            'col': 'stat.onBasePercentage',
            'str': '{:>5}',
            'help': "(On-Base Percentage): ratio of player's earned on-base count (hits and walks) to their earned plate appearances (excluding errors and sacrifice bunts)",
        },
        'TBP': {
            'col': 'stat.totalBasePercentage',
            'str': '{:>4}',
            'help': "(Total Base Percentage): ratio of player's earned total base count (hits and walks) to their earned plate appearances",
        },
        'RBP': {
            'col': 'stat.runsBattedPercentage',
            'str': '{:>4}',
            'help': "(Runs-Batted Percentage): ratio of player's runs-batted-in to their earned plate appearances",
        },
        'SOP': {
            'col': 'stat.strikeOutPercentage',
            'str': '{:>4}',
            'help': "(Strikeout Percentage): ratio of player's strikeouts to their earned plate appearances",
        },
        'LBP': {
            'col': 'stat.leftOnBasePercentage',
            'str': '{:>4}',
            'help': "(Left-on-Base Percentage): ratio of baserunners left-on-base (on-base during the batter's plate appearance that did not score) to earned plate appearances",
        },
        'PA': {
            'col': 'stat.plateAppearances',
            'str': '{:>4}',
            'help': "(Plate Appearances): count of total plate appearances",
        },
        'G': {
            'col': 'stat.gamesPlayed',
            'str': '{:>3}',
            'help': "(Games Played): count of individual games played",
        },
    },
    "pitching": {
        'POS': {
            'col': 'person.position',
            'str': '{:>3}',
            'help': "(Primary Position)",
        },
        'PO': {
            'col': 'stat.pitchedOuts',
            'str': '{:>3}',
            'help': "(Pitched Outs): count of times player recorded an out as a result of their pitching (strike, ground, air)",
        },
        'SO': {
            'col': 'stat.strikeOuts',
            'str': '{:>3}',
            'help': "(Strikeouts): count of times player recorded a strikeout",
        },
        'LOB': {
            'col': 'stat.leftOnBase',
            'str': '{:>3}',
            'help': "(Left-on-Base): count of baserunners left-on-base at the end of an inning",
        },
        'STR': {
            'col': 'stat.strikeRate',
            'str': '{:>5}',
            'help': "(Strike Rate): ratio of pitched strikes to total pitches",
        },
        'SOP': {
            'col': 'stat.strikeOutPercentage',
            'str': '{:>4}',
            'help': "(Strikeout Percentage): ratio of strikeouts to count of pitched plate appearances (plate appearances excluding fielding errors and sacrifice bunts)",
        },
        'GOP': {
            'col': 'stat.groundOutPercentage',
            'str': '{:>4}',
            'help': "(Groundout Percentage): ratio of groundouts (excluding sacrifice bunts) to count of pitched plate appearances",
        },
        'AOP': {
            'col': 'stat.airOutPercentage',
            'str': '{:>4}',
            'help': "(Airout Percentage): ratio of airouts (flyouts and lineouts) to count of pitched plate appearances",
        },
        'BBP': {
            'col': 'stat.baseOnBallsPercentage',
            'str': '{:>4}',
            'help': "(Base-on-Balls Percentage): ratio of bases awarded via four balls to count of pitched plate appearances",
        },
        'TBP': {
            'col': 'stat.totalBasePercentage',
            'str': '{:>4}',
            'help': "(Total Bases Percentage): ratio of earned total bases surrendered to count of pitched plate appearances",
        },
        'LOR': {
            'col': 'stat.leftOnBaseRate',
            'str': '{:>4}',
            'help': "(Left-on-Base Rate): ratio of left-on-base count to innings pitched",
        },
        'ERR': {
            'col': 'stat.earnedRunRate',
            'str': '{:>4}',
            'help': "(Earned Run Rate): ratio of earned run count to innings pitched",
        },
        'W': {
            'col': 'stat.wins',
            'str': '{:>3}',
            'help': "(Wins): count of game appearances resulting in a win (team leading at time of substitution and goes on to win game, minimum five innings pitched)",
        },
        'HS': {
            'col': 'stat.allSaves',
            'str': '{:>2}',
            'help': "(Holds/Saves): count of game appearances resulting in a hold or save (appears in relief when leading by no more than three runs and maintains lead)",
        },
        'FAR': {
            'col': 'stat.failedAppearanceRate',
            'str': '{:>4}',
            'help': "(Failed Appearance Rate): ratio of failed appearances (a loss or a blown save) to individual appearances",
        }, 
        'BF': {
            'col': 'stat.battersFaced',
            'str': '{:>3}',
            'help': "(Batters Faced): count of total batter plate appearances",
        },
        'IP': {
            'col': 'stat.inningsPitched',
            'str': '{:>5}',
            'help': "(Innings Pitched): total innings pitched (one inning is equivalent to recording three outs)",
        },
    },
    'fielding': {
        'POS': {
            'col': 'person.position',
            'str': '{:>9}',
            'help': "(Positions Fielded): primary fielding position followed by up to two secondary positions (including UT for utility)",
        },
        'PO': {
            'col': 'stat.putOuts',
            'str': '{:>4}',
            'help': "(Put-Outs): count of outs recorded by the player against a batter or baserunner",
        },
        'A': {
            'col': 'stat.assists',
            'str': '{:>3}',
            'help': "(Assists): count of outs recorded in which the player threw or deflected the ball to contribute to a put-out",
        },
        'DP': {
            'col': 'stat.doublePlays',
            'str': '{:>2}',
            'help': "(Double Plays): count of double plays in which the player contributed a put-out or assist",
        },
        'CS': {
            'col': 'stat.caughtStealing',
            'str': '{:>2}',
            'help': "(Caught Stealing): for catchers only; count of baserunners thrown out when attempting to steal a base",
        },
        'E': {
            'col': 'stat.errors',
            'str': '{:>2}',
            'help': "(Errors): count of times in which the player fails to record an out on a routine play under ordinary effort",
        },
        'PE': {
            'col': 'stat.wildPitches',
            'str': '{:>2}',
            'help': "(Pitched Errors): for pitchers and catchers only; count of passed balls (pitchers) and wild pitches (catchers)",
        },
        'FP': {
            'col': 'stat.fieldingPercentage',
            'str': '{:>6}',
            'help': "(Fielding Percentage): ratio of put-outs and assists to chances (sum of put-outs, assists, and errors)",
        },
        'FR': {
            'col': 'stat.fieldingRate',
            'str': '{:>4}',
            'help': "(Fielding Rate): ratio of put-outs and assists to innings fielded",
        },
        'CSP': {
            'col': 'stat.caughtStealingPercentage',
            'str': '{:>4}',
            'help': "(Caught Stealing Percentage): for catchers only; ratio of baserunners caught stealing to base stealing attempts",
        },
        'IF': {
            'col': 'stat.innings',
            'str': '{:>7}',
            'help': "(Innings Fielded): total innings fielded (one inning is equivalent to recording three outs)",
        },
    },
}