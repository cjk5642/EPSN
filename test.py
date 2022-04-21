from epsn.ncaaf import NCAAF
import networkx as nx

ncaaf = NCAAF(year = 2021)
gml = ncaaf.response['result']
graph = nx.parse_gml(gml)
print(nx.info(graph))