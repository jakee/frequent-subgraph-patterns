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

        for old_subg in self.reservoir.get_common_subgraphs(u, v):
            new_subg = make_subgraph(old_subg.nodes, old_subg.edges + (edge,))
            self.process_existing_subgraph(old_subg, new_subg)

        s_rep_end = datetime.now()

        # find new subgraph candidates for the reservoir
        s_add_start = datetime.now()
        additions = self.get_new_subgraphs(u, v)

        # perform reservoir sampling for each new subgraph candidate
        I = 0
        for nodes in additions:
            self.N += 1
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
        self.metrics['reservoir_full_bool'].append(int(self.reservoir.is_full()))

        return True


    def process_new_subgraph(self, subgraph):
        success, old_subgraph = self.reservoir.add(subgraph, N=self.N)

        if success: self.add_subgraph(subgraph)
        if old_subgraph: self.remove_subgraph(old_subgraph)

        return success
