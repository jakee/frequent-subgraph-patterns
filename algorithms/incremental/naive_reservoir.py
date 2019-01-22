import numpy as np

from collections import Counter

from graph.simple_graph import SimpleGraph

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label

from sampling.subgraph_reservoir import SubgraphReservoir

from algorithms.exploration.optimized_quadruplet import get_new_subgraphs

from util.set import flatten

class IncrementalNaiveReservoirAlgorithm:
    k = None
    M = None # reservoir size
    N = None # number of subgraphs seen
    graph = None
    patterns = None
    reservoir = None


    def __init__(self, M, k=3):
        self.k = k
        self.M = M
        self.N = 0

        self.graph = SimpleGraph()
        self.patterns = Counter()
        self.reservoir = SubgraphReservoir()


    def add_edge(self, edge):
        if edge in self.graph:
            return False

        u = edge.get_u()
        v = edge.get_v()

        # replace update all existing subgraphs with u and v in the reservoir
        for s in self.reservoir.get_common_subgraphs(u, v):
            self.remove_subgraph_from_reservoir(s)
            self.add_subgraph_to_reservoir(make_subgraph(s.nodes, s.edges+(edge,)))

        # find new subgraph candidates for the reservoir
        additions = get_new_subgraphs(self.graph, u, v, self.k)

        # perform reservoir sampling for each new subgraph candidate
        for nodes in additions:
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges+[edge])
            self.add_subgraph(subgraph)

        self.graph.add_edge(edge)

        return True


    def add_subgraph(self, subgraph):
        self.N += 1

        success = False

        if len(self.reservoir) < self.M:
            success = True
        elif np.random.rand() < (self.M / float(self.N)):
            success = True
            self.remove_subgraph_from_reservoir(self.reservoir.random())

        if success:
            self.add_subgraph_to_reservoir(subgraph)


    def add_subgraph_to_reservoir(self, subgraph):
        self.reservoir.add(subgraph)
        self.patterns.update([canonical_label(subgraph)])


    def remove_subgraph_from_reservoir(self, subgraph):
        self.reservoir.remove(subgraph)
        self.patterns.subtract([canonical_label(subgraph)])
