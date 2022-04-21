
import itertools
from sportsipy.ncaaf.teams import Teams as ncaaf_teams
from sportsipy.ncaaf.schedule import Schedule as ncaaf_schedule
from sportsipy.ncaaf.roster import Player as ncaaf_player
from tqdm import tqdm
import datetime

# load the project utils
from utils import _convert_data_to_gml, __INIT_DATE__

current_year = datetime.datetime.now().year

class NCAAF:
  _cache = {}
  def __init__(self, year: int = 2021, level: str = 'team'):
    self.year = year
    self.level = level
    
    # create data and generate response
    ncaaf_year = __INIT_DATE__['ncaaf'].year
    if ncaaf_year <= self.year <= current_year-1:
      if NCAAF._cache.get((self.year, self.level)) is None:
        self.nodes, self.edges = self._establish_data()
        self.response = self._generate_response()
        NCAAF._cache[(self.year, self.level)] = self.response
      else:
        self.response = NCAAF._cache[(self.year, self.level)]
    else:
      self.response = {"api_code": 400, "result": f"ERROR: Wrong input year. Must be between {ncaaf_year} and {current_year}"}

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
    teams = ncaaf_teams(self.year)
    for team in tqdm(teams):
      abbr, name, conf = team.abbreviation, team.name, team.conference.lower()
      node = {"id": abbr, 'label': name, 'conference': conf}
      if node not in nodes:
        nodes.append(node)
      
      # schedules
      games = team.schedule
      for game in games:
        # determine home and away teams
        if game.location == 'Away': 
          away_team = abbr
          home_team = game.opponent_abbr
          away_team_rank = game.rank
          home_team_rank = game.opponent_rank
          away_team_conf = conf
          home_team_conf = game.opponent_conference

        else:
          away_team = game.opponent_abbr
          home_team = abbr
          away_team_rank = game.opponent_rank
          home_team_rank = game.rank
          away_team_conf = game.opponent_conference
          home_team_conf = conf

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
                "source_rank": away_team_rank, 
                "target_rank": home_team_rank,
                'source_conference': away_team_conf,
                'target_conference': home_team_conf,
                'week': game.game,
                "conference_game": conf_game, 
                'year': self.year}
        edges.append(edge)

    return nodes, edges
  
  # collect player data
  def _prepare_player_data(self):
    nodes = {}
    edges = []
    teams = ncaaf_teams(year = self.year)
    for team in tqdm(teams):
      abbr, conf = team.abbreviation, team.conference.lower()

      # schedules
      games = team.schedule
      for game in games:
        box = game.boxscore
        away_players = box.away_players
        home_players = box.home_players
        source_to_target_players = itertools.product(away_players, home_players)

        # determine home and away teams
        if game.location == 'Away': 
          away_team = abbr
          home_team = game.opponent_abbr
          away_team_rank = game.rank
          home_team_rank = game.opponent_rank
          away_team_conf = conf
          home_team_conf = game.opponent_conference

        else:
          away_team = game.opponent_abbr
          home_team = abbr
          away_team_rank = game.opponent_rank
          home_team_rank = game.rank
          away_team_conf = game.opponent_conference
          home_team_conf = conf

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
        
        # collect the players
        for away_player, home_player in tqdm(source_to_target_players):
          away_player_id = away_player.player_id
          home_player_id = home_player.player_id
          if nodes.get(away_player_id) is None:
            away_player_instance = ncaaf_player(away_player_id)
            try:
              away_player_position = away_player_instance.position
            except TypeError:
              away_player_position = ""
            try:
              away_player_class = away_player_instance.year
            except TypeError:
              away_player_class = ""

            nodes[away_player_id] = {'id': away_player_id, "name": away_player.name, 'position': away_player_position, 'class': away_player_class}

          if nodes.get(home_player_id) is None:
            home_player_instance = ncaaf_player(home_player_id)
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
                  "source_rank": away_team_rank, 
                  "target_rank": home_team_rank,
                  'source_conference': away_team_conf,
                  'target_conference': home_team_conf,
                  'week': game.game,
                  "conference_game": conf_game, 
                  'year': self.year
                  }
          edges.append(edge)

    return list(nodes.values()), edges

  def _generate_response(self):
    if self.nodes and self.edges:
      return _convert_data_to_gml(self.nodes, self.edges) 
    else:
      return {"api_code": 400, "result": f"Error: Specified level must be T(t)eam or P(p)layer not {self.level}"}