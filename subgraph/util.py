from .subgraph import Subgraph, SubgraphEdge

def make_subgraph(nodes, edges):
    nodes = sorted(nodes)
    edges = sorted([make_subgraph_edge(edge) for edge in edges])
    return Subgraph(tuple(nodes), tuple(edges))

def make_subgraph_edge(edge):
    return SubgraphEdge(edge.u, edge.v, edge.label)
