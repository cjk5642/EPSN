
import itertools
from sportsipy.ncaab.teams import Teams as ncaab_teams
from sportsipy.ncaab.schedule import Schedule as ncaab_schedule
from sportsipy.ncaab.roster import Player as ncaab_player
from tqdm import tqdm
import datetime

# load the project utils
from epsn.utils import _convert_data_to_gml, __INIT_DATE__

current_year = datetime.datetime.now().year

class NCAAB:
  _cache = {}
  def __init__(self, year: int = 2021, level: str = 'team'):
    self.year = year
    self.level = level
    
    # create data and generate response
    ncaab_year = __INIT_DATE__['ncaab'].year
    if ncaab_year <= self.year <= current_year-1:
      if NCAAB._cache.get((self.year, self.level)) is None:
        self.nodes, self.edges = self._establish_data()
        self.response = self._generate_response()
        NCAAB._cache[(self.year, self.level)] = self.response
      else:
        self.response = NCAAB._cache[(self.year, self.level)]
    else:
      self.response = {"api_code": 400, "result": f"ERROR: Wrong input year. Must be between {ncaab_year} and {current_year}"}

  def _establish_data(self):
    if self.level.lower() == 'team':
      nodes, edges = self._prepare_game_data()
    elif self.level.lower() == 'player':
      nodes, edges = None, None #self._prepare_player_data()
    else:
      nodes, edges = None, None
    return nodes, edges

  def _prepare_game_data(self):
    nodes = {}
    edges = []
    teams = ncaab_teams(self.year)
    for team in tqdm(teams):
      abbr, name, conf = team.abbreviation, team.name, team.conference.lower()
      
      # schedules
      games = team.schedule
      for game in games:
        # determine home and away teams
        if game.location == 'Away': 
          away_team = abbr.lower()
          home_team = game.opponent_abbr.lower()
          away_team_name = name
          home_team_name = game.opponent_name
          away_team_conf = conf
          home_team_conf = game.opponent_conference

        else:
          away_team = game.opponent_abbr.lower()
          home_team = abbr.lower()
          away_team_name = game.opponent_name
          home_team_name = name
          away_team_conf = game.opponent_conference
          home_team_conf = conf

        # ensure all nodes are defined
        away_node = {"id": away_team, 'label': away_team_name, 'conference': away_team_conf}
        if nodes.get(away_team) is None:
          nodes[away_team] = away_node

        home_node = {"id": home_team, 'label': home_team_name, 'conference': home_team_conf}
        if nodes.get(home_team) is None:
          nodes[home_team] = home_node

        # get game result
        if game.result.lower() == 'win':
          away_win = 1
          home_win = 0
        else:
          away_win = 0
          home_win = 1

        if conf == game.opponent_conference.lower():
            conf_game = 1
        else:
            conf_game = 0
        
        edge = {'source': away_team, 
                'target': home_team, 
                'source_win': away_win, 
                'target_win': home_win, 
                'source_conference': away_team_conf,
                'target_conference': home_team_conf,
                'week': game.game,
                "conference_game": conf_game, 
                'year': self.year, 
                'season_type': game.type}
        edges.append(edge)

    return list(nodes.values()), edges
  
  # collect player data
  def _prepare_player_data(self):
    nodes = {}
    edges = []
    teams = ncaab_teams(year = self.year)
    for team in tqdm(teams):
      abbr, conf = team.abbreviation, team.conference.lower()

      # schedules
      games = team.schedule
      for game in tqdm(games):
        box = game.boxscore
        away_players = box.away_players
        home_players = box.home_players
        source_to_target_players = itertools.product(away_players, home_players)

        # determine home and away teams
        if game.location == 'Away': 
          away_team = abbr
          home_team = game.opponent_abbr
          away_team_conf = conf
          home_team_conf = game.opponent_conference

        else:
          away_team = game.opponent_abbr
          home_team = abbr
          away_team_conf = game.opponent_conference
          home_team_conf = conf
        
        # get game result
        if game.result.lower() == 'win':
          away_win = 1
          home_win = 0
        else:
          away_win = 0
          home_win = 1
        
        # check if the two conferences of the teams are the same
        if conf == game.opponent_conference.lower():
            conf_game = 1
        else:
            conf_game = 0
        
        # collect the players
        for away_player, home_player in source_to_target_players:
          away_player_id = away_player.player_id
          home_player_id = home_player.player_id
          if nodes.get(away_player_id) is None:
            away_player_instance = ncaab_player(away_player_id)
            try:
              away_player_position = away_player_instance.position
            except TypeError:
              away_player_position = ""
            try:
              away_player_class = away_player_instance.year
            except TypeError:
              away_player_class = ""

            nodes[away_player_id] = {'id': away_player_id, "name": away_player.name, 'position': away_player_position, 'class': away_player_class}

          # check if the home player id is in the nodes
          if nodes.get(home_player_id) is None:
            home_player_instance = ncaab_player(home_player_id)
            try:
              home_player_position = home_player_instance.position
            except TypeError:
              home_player_position = ""
            try:
              home_player_class = home_player_instance.year
            except TypeError:
              home_player_class = ""
            nodes[home_player_id] = {'id': home_player_id, "name": home_player.name, 'position': home_player_position, 'class': home_player_class} 

          edge = {'source': away_player_id, 
                  'target': home_player_id, 
                  'source_team': away_team, 
                  'target_team': home_team, 
                  'source_win': away_win, 
                  'target_win': home_win, 
                  'source_conference': away_team_conf,
                  'target_conference': home_team_conf,
                  'week': game.game,
                  "conference_game": conf_game, 
                  'year': self.year,
                  'season_type': game.type
                  }
          edges.append(edge)

    return list(nodes.values()), edges

  def _generate_response(self):
    if self.nodes and self.edges:
      return _convert_data_to_gml(self.nodes, self.edges) 
    else:
      return {"api_code": 400, "result": f"Error: Specified level must be T(t)eam or P(p)layer not {self.level}"}