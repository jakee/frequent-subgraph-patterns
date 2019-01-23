import random

import numpy as np

from collections import Counter

from graph.simple_graph import SimpleGraph

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label

from sampling.subgraph_reservoir import SubgraphReservoir
from sampling.skip_rs import SkipRS

from algorithms.exploration.optimized_quadruplet import get_new_subgraphs

from util.set import flatten

class IncerementalOptimizedReservoirAlgorithm:
    k = None
    M = None # reservoir size
    N = None # number of subgraphs seen
    s = None # number of surplus subgraps to skip this iteration

    graph = None
    patterns = None
    reservoir = None
    skip_rs = None


    def __init__(self, M, k=3):
        self.k = k
        self.M = M
        self.N = 0
        self.s = 0

        self.graph = SimpleGraph()
        self.patterns = Counter()
        self.reservoir = SubgraphReservoir()
        self.skip_rs = SkipRS(M)


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
        subgraph_candidates = list(get_new_subgraphs(self.graph, u, v, self.k))

        W = len(subgraph_candidates)
        I = 0 # number of subgraph candidates to include in sample

        if len(self.reservoir) < self.M:
            # if the reservoir is not full,
            # we must include the next M - N subgraphs
            I = min(W, self.M - len(self.reservoir))
            self.s = I
            self.N += I

        # determine the number of candidates I to include in the sample
        while self.s < W:
            I += 1
            Z_rs = self.skip_rs.apply(self.N)
            self.N += Z_rs + 1
            self.s += Z_rs + 1

        # sample I subgraphs from the W candidates
        if I < W:
            additions = random.sample(subgraph_candidates, I)
        else:
            additions = subgraph_candidates

        # add all sampled subgraphs
        for nodes in additions:
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges+[edge])
            self.add_subgraph(subgraph)

        self.graph.add_edge(edge)
        self.s -= W

        return True


    def add_subgraph(self, subgraph):
        if len(self.reservoir) >= self.M:
            self.remove_subgraph_from_reservoir(self.reservoir.random())

        self.add_subgraph_to_reservoir(subgraph)


    def add_subgraph_to_reservoir(self, subgraph):
        self.reservoir.add(subgraph)
        self.patterns.update([canonical_label(subgraph)])


    def remove_subgraph_from_reservoir(self, subgraph):
        self.reservoir.remove(subgraph)
        self.patterns.subtract([canonical_label(subgraph)])
