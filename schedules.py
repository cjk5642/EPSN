import pandas as pd
import os
import json
import requests
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
        self.sports = { "nfl": NFLSchedules(self.collectseasons, self.schedule_path), 
                        "mlb": MLBSchedules(self.collectseasons, self.schedule_path),
                        "nba": NBASchedules(self.collectseasons, self.schedule_path)}

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
                        split_range = [pd.to_datetime(all_h3[0]).date(), pd.to_datetime(all_h3[-1]).date()]
                    else:
                        split_range = []
                    split_data[ds] = list(map(str, split_range))
            else:
                split_data = {'regular': splits[0], 'post': []}
                all_h3 = split_data['regular'].find_all('h3')
                all_h3 = list(map(lambda x: x.text, all_h3))
                split_data['regular'] = list(map(str, [pd.to_datetime(all_h3[0]).date(), pd.to_datetime(all_h3[-1]).date()]))
            collections[year] = split_data      
        
        # save the file
        with open(self.mlb_path, 'w') as file:
            json.dump(collections, file)

        return collections

class NBASchedules:
    schedule = None
    def __init__(self, collectseasons, schedule_dir: str):
        self.seasons = collectseasons.seasons
        self.nba_path = os.path.join(schedule_dir, 'NBA_schedules.json')

        if NBASchedules.schedule is None:
            NBASchedules.schedule = self._collect_schedule()

    def _collect_schedule(self):
        # chack if file exists
        if os.path.exists(self.nba_path):
            with open(self.nba_path, 'r') as file:
                return json.load(file)

        print("Working on NBA Schedules...")
        nba_seasons = self.seasons['nba']
        year_range = range(nba_seasons['min_year'], nba_seasons['max_year'])
        BAA_years = [1946, 1947, 1948]
        collections = {}
        for year in tqdm(year_range):
            split_data = {}
            # collect the regular season
            if year in BAA_years:
                regularseason_url = f"https://www.basketball-reference.com/leagues/BAA_{year+1}_games.html"
                postseason_url = f"https://www.basketball-reference.com/playoffs/BAA_{year+1}.html"
            else:
                regularseason_url = f"https://www.basketball-reference.com/leagues/NBA_{year+1}_games.html"
                postseason_url = f"https://www.basketball-reference.com/playoffs/NBA_{year+1}.html"
            response = BeautifulSoup(requests.get(regularseason_url).content, 'html.parser')
            filter_header = response.find('div', attrs = {'class': 'filter'})
            links = ["https://www.basketball-reference.com" + a['href'] for a in filter_header.find_all('a')]
            first = str(pd.to_datetime(pd.read_html(links[0])[0].iloc[0, 0]).date())
            last = str(pd.to_datetime(pd.read_html(links[-1])[0].iloc[-1, 0]).date())
            split_data['regular'] = [first, last]

            #extract the postseason dates
            playoffTable = pd.read_html(postseason_url)[0].iloc[:, 1]
            dates = pd.Series([pd.to_datetime(pt + f", {year+1}").date() for pt in list(playoffTable) if isinstance(pt, str) and "@" not in pt and pt[-1].isdigit()])
            split_data['post'] = [str(dates.min()), str(dates.max())]
            collections[year] = split_data
            
        # save the file
        with open(self.nba_path, 'w') as file:
            json.dump(collections, file)

        return None

class NHLSchedules:
    pass

class NCAAFSchedules:
    pass

class NCAABSchedules:
    pass

ss = SportSchedules()
ss.collect_sport_schedules()