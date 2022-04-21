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
    box = game.boxscore
    print(game.type)
    away_players = box.away_players
    home_players = box.home_players
    source_to_target_players = itertools.product(away_players, home_players)
    for away_player, home_player in source_to_target_players:
      away_player_id = away_player.player_id
      home_player_id = home_player.player_id
      print(away_player_id, home_player_id)
      print(ncaaf_player(away_player_id))
      break
    break
  break