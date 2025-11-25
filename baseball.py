from standings import Standings, StandingsCheck
from stats import Statistics, StatisticsCheck
from roster import Roster, RosterCheck
from scores import Scores, ScoresCheck
from schedule import Schedule, ScheduleCheck

def Help():
    print()
    print("This program can output data from the current MLB season:")
    print("  -- leaguewide 'scores' for a given day.")
    print("  -- division or wild card 'standings'.")
    print("  -- player 'statistics' for hitting, pitching, and fielding.")
    print("  -- team 'roster' or 'schedule'.")
    print()

if __name__ == "__main__":
    print("Welcome to the Michael's Baseball Program.")
    while True:
        arg = input().split()
        # Quit program
        if arg[0] == 'exit' or arg[0] == 'quit':
            break
        # Help message
        if arg[0] == 'help':
            Help()
        # Standings
        if 'standings' in arg:
            arg.remove('standings')
            i, s = StandingsCheck(arg)
            if i == 0:
                Standings(s)
        # Statistics
        if ('statistics' in arg) or ('stats' in arg):
            arg = [x for x in arg if x not in ['statistics','stats']]
            i, s = StatisticsCheck(arg)
            if i == 0:
                Statistics(s)            
        # Roster
        if 'roster' in arg:
            arg.remove('roster')
            i, s = RosterCheck(arg)
            if i == 0:
                Roster(s)            
        # Scores
        if 'scores' in arg:
            arg.remove('scores')
            i, s = ScoresCheck(arg)
            if i == 0:
                Scores(s)
        # Schedule
        if 'schedule' in arg:
            arg.remove('schedule')
            i, s = ScheduleCheck(arg)
            if i == 0:
                Schedule(s)
        continue