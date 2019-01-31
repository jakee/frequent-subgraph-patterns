import random

from datetime import datetime, timedelta

from ..reservoir import ReservoirAlgorithm

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label


class IncrementalNaiveReservoirAlgorithm(ReservoirAlgorithm):

    def __init__(self, k=3, M=1000):
        super().__init__(k=k, M=M)


    def add_edge(self, edge):
        if edge in self.graph:
            return False

        e_add_start = datetime.now()

        u = edge.get_u()
        v = edge.get_v()

        # replace update all existing subgraphs with u and v in the reservoir
        s_rep_start = datetime.now()
        for subg in self.reservoir.get_common_subgraphs(u, v):
            self.remove_subgraph(subg)
            self.add_subgraph(make_subgraph(subg.nodes, subg.edges+(edge,)))
        s_rep_end = datetime.now()

        # find new subgraph candidates for the reservoir
        s_add_start = datetime.now()
        additions = self.get_new_subgraphs(u, v)

        # perform reservoir sampling for each new subgraph candidate
        I = 0
        for nodes in additions:
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges+[edge])
            I += int(self.process_new_subgraph(subgraph))
        s_add_end = datetime.now()

        self.graph.add_edge(edge)

        e_add_end = datetime.now()

        ms = timedelta(microseconds=1)
        self.metrics['edge_add_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['subgraph_add_ms'].append((s_add_end - s_add_start) / ms)
        self.metrics['subgraph_replace_ms'].append((s_rep_end - s_rep_start) / ms)
        self.metrics['new_subgraph_count'].append(len(additions))
        self.metrics['included_subgraph_count'].append(I)
        self.metrics['reservoir_full_bool'].append(int(len(self.reservoir) >= self.M))

        return True


    def process_new_subgraph(self, subgraph):
        self.N += 1

        success = False

        if len(self.reservoir) < self.M:
            success = True
        elif random.random() < (self.M / float(self.N)):
            success = True
            self.remove_subgraph(self.reservoir.random())

        if success:
            self.add_subgraph(subgraph)

        return success


    def add_subgraph(self, subgraph):
        self.reservoir.add(subgraph)
        self.patterns.update([canonical_label(subgraph)])


    def remove_subgraph(self, subgraph):
        self.reservoir.remove(subgraph)
        self.patterns.subtract([canonical_label(subgraph)])
