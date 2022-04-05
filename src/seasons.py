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