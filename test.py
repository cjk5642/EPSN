"""
from mlb import MLB
import networkx as nx
m = MLB()
response = m.response['result']
graph = nx.parse_gml(response, label = 'id')
print(nx.info(graph))
"""
from sportsipy.nba.teams import Teams 
teams = Teams(2020)
for team in teams:
    print(team.name, team.abbreviation)
    break