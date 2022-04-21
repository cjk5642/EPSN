from epsn.ncaab import NCAAB
import networkx as nx
import json
import os
import pandas as pd

if os.path.exists('test.json'):
    with open('test.json', 'r') as file:
        data = json.load(file)
else:        
    ncaab = NCAAB(year = 2021, level = 'player')
    data = ncaab.response
    with open("test.json", 'w') as file:
        json.dump(data, file)

gml = data['result']
graph = nx.parse_gml(gml, label = 'label')
print(nx.info(graph))
print(pd.Series([graph._node[node]['conference'] for node in graph.nodes]).value_counts())

