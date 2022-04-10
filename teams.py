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
from seasons import CollectSeasons

class CollectTeamsBySeason:
    sports_team_by_season = None
    def __init__(self, collectseasons = CollectSeasons()):
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