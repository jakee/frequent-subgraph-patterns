import random

from datetime import datetime, timedelta

from ..reservoir import ReservoirAlgorithm

from graph.simple_graph import SimpleGraph

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label

from sampling.skip_rs import SkipRS

class IncerementalOptimizedReservoirAlgorithm(ReservoirAlgorithm):


    def __init__(self, k=3, M=1000):
        self.s = 0
        self.skip_rs = SkipRS(M)
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
        subgraph_candidates = self.get_new_subgraphs(u, v)

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
            self.process_new_subgraph(subgraph)

        self.graph.add_edge(edge)
        self.s -= W

        e_add_end = datetime.now()

        ms = timedelta(microseconds=1)
        self.metrics['edge_op'].append('add')
        self.metrics['edge_op_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['num_candidate_subgraphs'].append(W)
        self.metrics['num_processed_subgraphs'].append(I)
        self.metrics['reservoir_full_bool'].append(int(self.reservoir.is_full()))
        self.metrics['skiprs_treshold_bool'].append(int(self.skip_rs.is_threshold_reached(self.N)))

        return True


    def process_new_subgraph(self, subgraph):
        success, old_subgraph = self.reservoir.add(subgraph)

        if success: self.add_subgraph(subgraph)
        if old_subgraph: self.remove_subgraph(old_subgraph)

        return success
