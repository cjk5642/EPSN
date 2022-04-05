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

class SportSchedules:
    """
    Add method to save the schedule as one giant schedule.json instead of multiple sport json
    """
    def __init__(self):
        self.schedule_path = self._establish_schedules_dir()
        self.collectseasons = CollectSeasons()
        self.sports = { "NFL": NFLSchedules(self.collectseasons, self.schedule_path), 
                        "MLB": MLBSchedules(self.collectseasons, self.schedule_path)}

    def _establish_schedules_dir(self) -> None:
        schedule_path = os.path.join(os.getcwd(), "data", "schedules")
        if not os.path.isdir(schedule_path):
            os.makedirs(schedule_path)
        return schedule_path

    def collect_sport_schedules(self):
        sport_schedules = {sport: sportinstance.schedule for sport, sportinstance in self.sports.items()}
        return sport_schedules

class NFLSchedules:
    schedule = None
    def __init__(self, collectseasons, schedule_dir: str):
        self.nfl_path = os.path.join(schedule_dir, 'NFL_schedules.json')
        self.seasons = collectseasons.seasons
        if NFLSchedules.schedule is None:
            NFLSchedules.schedule = self._collect_schedule()

    def _collect_schedule(self) -> dict:
        # just load file if it exists
        if os.path.exists(self.nfl_path):
            with open(self.nfl_path, 'r') as file:
                return json.load(file)

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
        
        # save the file
        with open(self.nfl_path, 'w') as file:
            json.dump(schedule_json, file)

        return schedule_json

class MLBSchedules:
    schedule = None
    def __init__(self, collectseasons, schedule_dir: str):
        self.seasons = collectseasons.seasons
        self.mlb_path = os.path.join(schedule_dir, 'MLB_schedules.json')

        if MLBSchedules.schedule is None:
            MLBSchedules.schedule = self._collect_schedule()

    def _collect_schedule(self):
        # chack if file exists
        if os.path.exists(self.mlb_path):
            with open(self.mlb_path, 'r') as file:
                return json.load(file)

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
                    split_data[ds] = list(map(str, split_range))
            else:
                split_data = {'regular': splits[0], 'post': []}
                all_h3 = split_data['regular'].find_all('h3')
                all_h3 = list(map(lambda x: x.text, all_h3))
                split_data['regular'] = list(map(str, [pd.to_datetime(all_h3[0]), pd.to_datetime(all_h3[-1])]))
            collections[year] = split_data      
        
        # save the file
        with open(self.mlb_path, 'w') as file:
            json.dump(collections, file)

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