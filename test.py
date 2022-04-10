from nfl import NFL
from utils import _return_graph
import networkx as nx

response = NFL(level = 'player').response['result']
graph = _return_graph(response)
print(nx.info(graph))