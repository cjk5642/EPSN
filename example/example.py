"""
Adapted from NetworkX example:
https://networkx.org/documentation/stable/auto_examples/drawing/plot_labels_and_colors.html
"""


import sys
import os
sys.path.insert(0, os.getcwd())

from epsn.nfl import NFL
import networkx as nx
import matplotlib.pyplot as plt

def fix_labels(label):
    splits = label.split(' ')
    first = ' '.join(splits[:-1])
    last = splits[-1]
    return '\n'.join([first, last])

def draw_graph(G, year):
    pos = nx.spring_layout(G, seed=1885)  # positions for all nodes

    # nodes
    options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.8}
    nx.draw_networkx_nodes(G, pos, node_color="tab:red", **options)

    # edges
    options = {"edge_color": "tab:gray", "width": 1.0, "alpha": 0.8}
    nx.draw_networkx_edges(G, pos, **options)
    labels = dict(G.nodes(data = 'label'))
    labels = {k: fix_labels(v) for k, v in labels.items()}
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_color="black")
    plt.title(f"Graph of NFL for year {year}")
    plt.tight_layout()
    plt.axis("off")

year = int(input("What year would you like to see for teams:\t"))
nfl = NFL(year)
result = nfl.response['result']
graph = nx.MultiDiGraph(nx.parse_gml(result, label = 'id'))
draw_graph(graph, year)
plt.savefig(f"./example/nfl_example-{year}.png")
