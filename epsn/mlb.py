
import itertools
from sportsipy.mlb.teams import Teams as mlb_teams
from sportsipy.mlb.schedule import Schedule as mlb_schedule
from sportsipy.mlb.roster import Player as mlb_player
from tqdm import tqdm
import datetime

# load the project utils
from .utils import _convert_data_to_gml, __INIT_DATE__

current_year = datetime.datetime.now().year

class MLB:
  _cache = {}
  def __init__(self, year: int = 2021, level: str = 'team'):
    self.year = year
    self.level = level
    
    # create data and generate response
    mlb_year = __INIT_DATE__['mlb'].year
    if mlb_year <= self.year <= current_year:
      if MLB._cache.get((self.year, self.level)) is None:
        self.nodes, self.edges = self._establish_data()
        self.response = self._generate_response()
        MLB._cache[(self.year, self.level)] = self.response
      else:
        self.response = MLB._cache[(self.year, self.level)]
    else:
      self.response = {"api_code": 400, "result": f"ERROR: Wrong input year. Must be between {mlb_year} and {current_year}"}

  def _establish_data(self):
    if self.level.lower() == 'team':
      nodes, edges = self._prepare_game_data()
    elif self.level.lower() == 'player':
      nodes, edges = self._prepare_player_data()
    else:
      nodes, edges = None, None
    return nodes, edges

  def _prepare_game_data(self):
    nodes = []
    edges = []
    teams = mlb_teams(self.year)
    for team in tqdm(teams):
      abbr, name = team.abbreviation, team.abbreviation
      node = {"id": abbr, 'label': name}
      if node not in nodes:
        nodes.append(node)
      
      # schedules
      team_sched = mlb_schedule(abbr, year = self.year)
      for game in team_sched._games:
        # determine home and away teams
        if game.location == 'Away': 
          away_team = abbr
          home_team = game.opponent_abbr
        else:
          away_team = game.opponent_abbr
          home_team = abbr
        # get game result
        if game.result == 'Win':
          away_win = 1
          home_win = 0
        else:
          away_win = 0
          home_win = 1
        
        edge = {'source': away_team, 'target': home_team, 'source_win': away_win, 
                'target_win': home_win, 'game_num': game.game, 'year': self.year}
        edges.append(edge)
    return nodes, edges
  
  # collect player data
  def _prepare_player_data(self):
    nodes = {}
    edges = []
    teams = mlb_teams(year = self.year)
    for team in tqdm(teams):
      team_abbr = team.abbreviation
      team_sched = mlb_schedule(team_abbr, year = self.year)
      for game in team_sched._games:
        box = game.boxscore

        away_players = box.away_players
        home_players = box.home_players
        source_to_target_players = itertools.product(away_players, home_players)

        # establish home or waway and who won
        if game.location == 'Away': 
          away_team = team_abbr
          home_team = game.opponent_abbr
        else:
          away_team = game.opponent_abbr
          home_team = team_abbr
        
        if game.result == 'Win':
          away_win = 1
          home_win = 0
        else:
          away_win = 0
          home_win = 1
        
        # collect the players
        for away_player, home_player in tqdm(source_to_target_players):
          away_player_id = away_player.player_id
          home_player_id = home_player.player_id
          if nodes.get(away_player_id) is None:
            try:
              away_player_position = mlb_player(away_player_id).position
            except TypeError:
              away_player_position = ""
            nodes[away_player_id] = {'id': away_player_id, "name": away_player.name, 'position': away_player_position}

          if nodes.get(home_player_id) is None:
            try:
              home_player_position = mlb_player(home_player_id).position
            except TypeError:
              away_player_position = ""
            nodes[home_player_id] = {'id': home_player_id, "name": home_player.name, 'position': home_player_position} 

          edge = {'source': away_player_id, 'target': home_player_id, 'source_team': away_team, 'target_team': home_team, 'source_win': away_win, 
                  'target_win': home_win, 'game_num': game.game, 'year': self.year}
          edges.append(edge)

    return list(nodes.values()), edges

  def _generate_response(self):
    if self.nodes and self.edges:
      return _convert_data_to_gml(self.nodes, self.edges) 
    else:
      return {"api_code": 400, "result": f"Error: Specified level must be T(t)eam or P(p)layer not {self.level}"}