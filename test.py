from epsn.ncaaf import NCAAF
import networkx as nx

ncaaf = NCAAF(year = 2021, level = 'player')
gml = ncaaf.response['result']
graph = nx.parse_gml(gml, label = 'id')
print(nx.info(graph))