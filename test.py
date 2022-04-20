import itertools
from sportsipy.ncaaf.teams import Teams as ncaaf_teams
from sportsipy.ncaaf.schedule import Schedule as ncaaf_schedule
from sportsipy.ncaaf.roster import Player as ncaaf_player
from tqdm import tqdm
import datetime

year = 2020
teams = ncaaf_teams(year = year)
for team in teams:
  print(team.abbreviation, team.name, team.conference)
  games = team.schedule
  for game in games:
    print(game.opponent_abbr, 
    game.opponent_name, 
    game.opponent_conference.lower(), game.opponent_rank, game.rank)

    break
  break