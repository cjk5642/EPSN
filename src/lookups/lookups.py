import pandas as pd
import datetime
import os
import numpy as np
from collections import defaultdict
import sys
import itertools
import json
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from error import SportNotAllowedError

class CollectSeasons:
  seasons = None

  def __init__(self):
    self.json_path = os.path.join(os.getcwd(), "data", "seasons.json")
    self.__INIT_DATE__ = {'mlb': datetime.datetime(1876, 4, 22), 
                          'nba': datetime.datetime(1946, 11, 1), 
                          'ncaaf': datetime.datetime(2000, 8, 26),  
                          'nfl': datetime.datetime(1970, 9, 18), 
                          'nhl': datetime.datetime(1918, 12, 21),
                          'ncaab': datetime.datetime(1947, 1, 1)}
    self.__SPORTS__ = {'nhl': 'https://www.hockey-reference.com/', 
              'mlb': 'https://www.baseball-reference.com/', 
              'nfl': 'https://www.pro-football-reference.com/', 
              'nba': 'https://www.basketball-reference.com/',
              'ncaaf': 'https://www.sports-reference.com/cfb/',
              'ncaab': 'https://www.sports-reference.com/cbb/'}

    # establish seasons and output years
    if CollectSeasons.seasons is None:
      CollectSeasons.seasons = self._collect_seasons()
    
    # jsonify seasons
    self._create_season_json()

  def _collect_seasons(self) -> None:
    sports = {sport: self._collect_seasons_helper(sport) for sport in tqdm(list(self.__SPORTS__.keys()))}
    return sports

  def _create_season_link(self, sport: str) -> str:
    # collect the urls for each sport
    if sport in ['nhl', 'mlb', 'nba']:
      season_link = self.__SPORTS__[sport] + 'leagues/'
    elif sport in ['nfl', 'ncaaf']:
      season_link = self.__SPORTS__[sport] + 'years/'
    else:
      season_link = self.__SPORTS__[sport] + 'seasons/'
    return season_link

  def _collect_seasons_helper(self, sport: str) -> dict: 
    # extract link by sport
    season_link = self._create_season_link(sport)
    
    # collect the reponse and parse the data to fit the data we want and save the data
    if sport in ['nhl', 'nba']:
      response = pd.read_html(season_link)[0]
      response.columns = response.columns.droplevel()
      response[['Year', 'End Year']] = response['Season'].str.split('-', expand = True)
      response['Year'] = response['Year'].astype(int)
      response = response[response['Year'] >= self.__INIT_DATE__[sport].year].reset_index(drop = True)

    elif sport in ['nfl', 'ncaaf']:
      response = pd.read_html(season_link)[0]
      response = response[response['Year'] >= self.__INIT_DATE__[sport].year].reset_index(drop = True)

    elif sport == 'mlb':
      response = pd.read_html(season_link)[1]
      response['Year'] = response['Year'].ffill()
      response['Year'] = response['Year'].astype(int)
      response = response[response['Year'] >= self.__INIT_DATE__[sport].year].reset_index(drop = True)

    elif sport == 'ncaab':
      response = pd.read_html(season_link)[0]
      response['Season'] = response['Season'].apply(lambda x: x.rstrip(' Summary'))
      response[['Year', 'End Year']] = response['Season'].str.split('-', expand = True)
      response = response[response['Year'] != 'Season'].reset_index(drop = True)
      response['Year'] = response['Year'].astype(int)
      response = response[response['Year'] >= self.__INIT_DATE__[sport].year].reset_index(drop = True)
    
    else:
      raise SportNotAllowedError(sport)
    
    min_year = int(response['Year'].min())
    max_year = int(response['Year'].max())
    r = dict(min_year = min_year, max_year = max_year, season_link = season_link)
    return r

  def _create_season_json(self) -> None:
    if not os.path.exists(self.json_path):
      with open(self.json_path, 'w') as file:
        json.dump(CollectSeasons.seasons, file)
    return None

class CollectTeamsBySeason:
  sports_team_by_season = None

  def __init__(self, collectseasons):
    self.teambysport_path = os.path.join(os.getcwd(), "data", "teams.json")
    self.seasons = collectseasons.seasons
    self.sports = list(self.seasons.keys())
    CollectTeamsBySeason.sports_team_by_season = {sport: None for sport in self.sports}

    # collect sports teams
    if not os.path.exists(self.teambysport_path):
      for sport in self.sports:
        if CollectTeamsBySeason.sports_team_by_season[sport] is None:
          print(f"Working on {sport}...")
          CollectTeamsBySeason.sports_team_by_season[sport] = self._collect_team_by_season(sport)
          self._create_team_json()
    else:
      with open(self.teambysport_path, 'r') as file:
        CollectTeamsBySeason.sports_team_by_season = json.load(file)

  def _extract_team_links_helper(self, teams, base_link: str):
    team_end_links = {}
    if teams is not None:
      if 'pro' in base_link:
        teams = teams.find_all(attrs = {'data-stat': 'team'})
      elif "sports-reference" in base_link:
        teams = teams.find_all(attrs = {'data-stat': 'school_name'})
      else:
        teams = teams.find_all(attrs = {'data-stat': 'team_name'})
      for t in teams:
        t_find = t.find('a')
        if t_find is None:
          continue
        link = f"{base_link}{t_find['href']}"
        team_end_links[t_find.text] = link
    return team_end_links

  def _extract_team_links(self, sport:str, year: str, link: str) -> dict:
    # collect the mlb
    if sport in ['mlb']:
      url = f"{link}/majors/{year}.shtml"
      soup = BeautifulSoup(requests.get(url).content, 'html.parser')
      teams = soup.find(id=re.compile('teams_standard_batting+'))
      team_end_links = self._extract_team_links_helper(teams, base_link = "https://www.baseball-reference.com")
    
    # collect the nhl
    if sport in ['nhl']:
      url = f"{link}/NHL_{year+1}.html"
      soup = BeautifulSoup(requests.get(url).content, 'html.parser')
      teams = soup.find(id=re.compile("standings+"))
      team_end_links = self._extract_team_links_helper(teams, base_link = "https://www.hockey-reference.com")
    
    # collect the nfl
    if sport in ['nfl']:
      url = f"{link}{year}"
      soup = BeautifulSoup(requests.get(url).content, 'html.parser')
      teams = soup.find(id=re.compile("AFC|NFC"))
      team_end_links = self._extract_team_links_helper(teams, base_link = "https://www.pro-football-reference.com")

    # collect the ncaaf and ncaab
    if sport in ['ncaaf', 'ncaab']:
      url = f"{link}{year}.html"
      soup = BeautifulSoup(requests.get(url).content, 'html.parser')
      conferences = [c.find('a')['href'] for c in soup.find_all(attrs = {'data-stat': 'conf_name'}) if c.find('a') is not None]
      team_end_links = {}
      for c in conferences:
        conf_url = f"https://www.sports-reference.com{c}"
        conf_soup = BeautifulSoup(requests.get(conf_url).content, 'html.parser')
        teams = conf_soup.find(id = 'standings')
        team_data = self._extract_team_links_helper(teams, base_link = "https://www.sports-reference.com")
        team_end_links.update(team_data)

    if sport in ['nba']:
      if 1969 >= year >= 1949:
        url = f"{link}NBA_{year+1}.html"
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        teams = soup.find(id=re.compile("divs_standings_"))      
      elif 2014 >= year > 1969:
        url = f"{link}NBA_{year+1}.html"
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        teams = soup.find(id=re.compile("divs_standings_+"))
      elif year >= 2014:
        url = f"{link}NBA_{year+1}.html"
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        teams = soup.find(id=re.compile("confs_standings_+"))
      else:
        url = f"{link}BAA_{year+1}.html"
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        teams = soup.find(id = 'divs_standings_')        
      team_end_links = self._extract_team_links_helper(teams, base_link = "https://www.basketball-reference.com")
    return team_end_links

  def _collect_team_by_season(self, sport: str) -> None:
    min_year = self.seasons[sport]['min_year']
    max_year = self.seasons[sport]['max_year']
    season_years = range(min_year, max_year+1)
    link = self.seasons[sport]['season_link']
    sport_data = {year:self._extract_team_links(sport, year, link) for year in tqdm(season_years)}
    return sport_data

  def _create_team_json(self) -> None:
    with open(self.teambysport_path, 'w') as file:
      json.dump(CollectTeamsBySeason.sports_team_by_season, file)
    return None

class SportSchedules:
  def __init__(self):
    self.schedule_path = self._establish_schedules_dir()
    self.collectseasons = CollectSeasons()
    self.sports = { "NFL": NFLSchedules(self.collectseasons), 
                    "MLB": MLBSchedules(self.collectseasons)}

  def _establish_schedules_dir(self) -> None:
    schedule_path = os.path.join(os.getcwd(), "data", "schedules")
    if not os.path.isdir(schedule_path):
      os.makedirs(schedule_path)
    return schedule_path

  def collect_sport_schedules(self):
    sport_schedules = {}
    for sport, sportinstance in self.sports.items():
        sport_path = os.path.join(self.schedule_path, f"{sport}_schedules.json")
        sport_schedule = sportinstance.schedule
        sport_schedules[sport] = sport_schedule
        with open(sport_path, 'w') as file:
            json.dump(sport_schedule, file)
    return sport_schedules

class NFLSchedules:
  schedule = None
  def __init__(self, collectseasons):
    self.seasons = collectseasons.seasons
    if NFLSchedules.schedule is None:
      NFLSchedules.schedule = self._collect_schedule()

  def _collect_schedule(self) -> dict:
    print("Working on NFL Schedules")
    frames = []
    nfl_seasons = self.seasons['nfl']
    year_range = range(nfl_seasons['min_year'], nfl_seasons['max_year'])
    for year in tqdm(year_range):
      url = f"https://www.pro-football-reference.com/years/{year}/games.htm"
      page = pd.read_html(url)[0]
      page['year'] = year
      page = page[['Week', 'year']].drop_duplicates()
      page = page[page['Week'] != 'Week'].dropna().reset_index(drop = True).reset_index()
      frames.append(page)
    schedule = pd.concat(frames, axis = 0, ignore_index = True)
    schedule['type_week'] = schedule['Week'].apply(lambda x: 'regular' if x.isnumeric() else 'post')
    schedule = schedule.rename({'index': 'week_num'}, axis = 1)
    schedule['week_num'] += 1

    schedule_json = {}
    for year in year_range:
      data = {}
      temp = schedule[schedule['year'] == year]
      data['regular'] = list(map(str, temp.loc[temp['type_week'] == 'regular', 'week_num'].values))
      data['post'] = list(map(str, temp.loc[temp['type_week'] == 'post', 'week_num'].values))
      data['name'] = list(map(str, temp['Week'].values))
      schedule_json[year] = data

    return schedule_json

class MLBSchedules:
  schedule = None
  def __init__(self, collectseasons):
    self.seasons = collectseasons.seasons

    #if MLBSchedules.schedule is None:
    #  MLBSchedules.schedule = self._collect_schedule()

  def _collect_schedule(self):
    print("Working on MLB Schedules...")
    mlb_seasons = self.seasons['mlb']
    year_range = range(mlb_seasons['min_year'], mlb_seasons['max_year'])
    data_split = ['regular', 'post']
    collections = {}
    for year in tqdm(year_range):
      url = f"https://www.baseball-reference.com/leagues/majors/{year}-schedule.shtml"
      response = BeautifulSoup(requests.get(url).content, 'html.parser')
      splits = response.find_all("div", attrs = {"class": 'section_content'})[:-1]
      if len(splits) == 2:
        split_data = dict(zip(data_split, splits))
        for ds in data_split:
          all_h3 = split_data[ds].find_all('h3')
          all_h3 = list(map(lambda x: x.text, all_h3))
          if 'Today' not in all_h3[0] or 'Today' not in all_h3[-1]:
            split_range = [pd.to_datetime(all_h3[0]), pd.to_datetime(all_h3[-1])]
          else:
            split_range = []
          split_data[ds] = split_range
        collections[year] = split_data
      else:
        split_data = {'regular': splits[0], 'post': []}
        all_h3 = split_data['regular'].find_all('h3')
        all_h3 = list(map(lambda x: x.text, all_h3))
        split_range = [pd.to_datetime(all_h3[0]), pd.to_datetime(all_h3[-1])]
        split_data['regular'] = split_range
        collections[year] = split_data
      
    return collections

class NBASchedules:
  pass

class NHLSchedules:
  pass

class NCAAFSchedules:
  pass

class NCAABSchedules:
  pass

ss = SportSchedules()
ss.collect_sport_schedules()