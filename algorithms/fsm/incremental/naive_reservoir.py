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
        for old_subg in self.reservoir.get_common_subgraphs(u, v):
            new_subg = make_subgraph(old_subg.nodes, old_subg.edges + (edge,))
            self.process_existing_subgraph(old_subg, new_subg)

        # find new subgraph candidates for the reservoir
        additions = self.get_new_subgraphs(u, v)

        # perform reservoir sampling for each new subgraph candidate
        I = 0
        for nodes in additions:
            self.N += 1
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges+[edge])
            I += int(self.process_new_subgraph(subgraph))

        self.graph.add_edge(edge)

        e_add_end = datetime.now()

        ms = timedelta(microseconds=1)
        self.metrics['edge_op'].append('add')
        self.metrics['edge_op_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['num_candidate_subgraphs'].append(len(additions))
        self.metrics['num_processed_subgraphs'].append(I)
        self.metrics['reservoir_full_bool'].append(int(self.reservoir.is_full()))

        return True


    def process_new_subgraph(self, subgraph):
        success, old_subgraph = self.reservoir.add(subgraph, N=self.N)

        if success: self.add_subgraph(subgraph)
        if old_subgraph: self.remove_subgraph(old_subgraph)

        return success


    def process_old_subgraph(self, subgraph):
        raise NotImplementedError()


    def remove_edge(self, edge):
        raise NotImplementedError()
