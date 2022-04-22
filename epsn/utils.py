import networkx as nx
from itertools import cycle
import json
import datetime

__INIT_DATE__ = { 'mlb': datetime.datetime(1876, 4, 22), 
                  'nba': datetime.datetime(1946, 11, 1), 
                  'ncaaf': datetime.datetime(2000, 8, 26),  
                  'nfl': datetime.datetime(1970, 9, 18), 
                  'nhl': datetime.datetime(1918, 12, 21),
                  'ncaab': datetime.datetime(1947, 1, 1)}

def _convert_data_to_gml_helper(nodes: list, edges: list) -> str:
  header = f"graph[\n\tmultigraph 1\n\tdirected 1"
  for n in nodes:
    header += "\n\tnode["
    for k, v in n.items():
      if isinstance(v, str) or isinstance(v, bool):
        line = f"\n\t {k} \"{v}\""
      else:
        line = f"\n\t {k} {v}"
      header += line
    header += "\n\t]"
  for e in edges:
    header += "\n\tedge["
    for k, v in e.items():
      if isinstance(v, str) or isinstance(v, bool):
        line = f"\n\t {k} \"{v}\""
      else:
        line = f"\n\t {k} {v}"   
      header += line
    header += "\n\t]"
  header += '\n]'
  return header

def _convert_data_to_gml(nodes: list, edges: list):
  # check if nodes and edges contain list of lists
  gml = _convert_data_to_gml_helper(nodes, edges)
  response = {"api_code": 200, "result": gml}
  return response

def _return_graph(gml: str):
  return nx.parse_gml(gml, label = 'id')

def _replicate_and_zip(data: list, team: str):
  zip_list = list(zip(data, cycle([team])))
  return zip_list