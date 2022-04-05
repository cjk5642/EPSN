import networkx as nx
from itertools import cycle
import json

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

def _convert_data_to_gml(output_path: str, nodes: list or list[list], edges: list or list[list], year: int or list[int]):
  # check if nodes and edges contain list of lists
  if not isinstance(nodes[0], list) and not isinstance(edges[0], list) and not isinstance(year, list):
    header = _convert_data_to_gml_helper(nodes, edges)
    data = {f"{year}": header}
  else:
    headers = [_convert_data_to_gml_helper(n, e) for n, e in zip(nodes, edges)]
    data = {f"{year}": gml for year, gml in zip(year, headers)}
  with open(output_path, 'w') as file:
    json.dump(data, file)

def _return_graph(path_to_gml: str):
  graph = {}
  with open(path_to_gml, 'r') as file:
    graphs = json.load(file)

  for k, v in graphs.items():
    graph[k] = nx.parse_gml(v, label = 'id')
  
  return graph

def _replicate_and_zip(data: list, team: str):
  zip_list = list(zip(data, cycle([team])))
  return zip_list