import random

from datetime import datetime, timedelta

from ..reservoir import ReservoirAlgorithm

from graph.simple_graph import SimpleGraph

from subgraph.util import make_subgraph, make_subgraph_edge
from subgraph.pattern import canonical_label

from sampling import skip_rp
from sampling.skip_rs import SkipRS


class DynamicOptimizedReservoirAlgorithm(ReservoirAlgorithm):


    def __init__(self, k=3, M=1000):
        super().__init__(k=k, M=M)

        self.skip_rs = SkipRS(M)

        # number of overflowing subgraphs skipped
        self.skip_sum_rs = 0
        self.skip_sum_rp = 0

        # the count of uncompensated deletions, where
        self.c1 = 0 # i) the deleted element was in the sample, and
        self.c2 = 0 # ii) the deleted element was not in the sample


    @property
    def d(self):
        return self.c1 + self.c2


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

        if not self.reservoir.is_full():
            # the reservoir is not full, which means we either
            # haven't encountered enough subgraphs to fill it, or
            # there are uncompensated deletions from the reservoir

            # in the former case, we simply add subgraphs into
            # the reservoir until it is full

            if self.d == 0:
                I = min(W, self.M - len(self.reservoir))
                self.s = I
                self.N += I

        # RANDOM PAIRING STEP

        sum_rp = 0

        while (self.d > 0) and (sum_rp < W):
            num_picked_subgraphs = 0
            Z_rp = skip_rp.skip_records(self.c1, self.d)

            if sum_rp + Z_rp < W:
                num_picked_subgraphs = int(self.c1 > 0)
            else:
                Z_rp = W - sum_rp

            I += num_picked_subgraphs
            self.c1 -= num_picked_subgraphs
            self.c2 -= Z_rp

            sum_rp += Z_rp + num_picked_subgraphs 

        W -= sum_rp

        # RANDOM SAMPLING STEP

        # determine the number of candidates I to include in the sample
        while self.s < W:
            I += 1
            Z_rs = self.skip_rs.apply(self.N)
            self.N += Z_rs + 1
            self.s += Z_rs + 1

        # sample I subgraphs from among the candidates
        if I < len(subgraph_candidates):
            additions = random.sample(subgraph_candidates, I)
        else:
            additions = subgraph_candidates

        # add all sampled subgraphs
        for nodes in additions:
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges + [edge])
            self.process_new_subgraph(subgraph)

        self.graph.add_edge(edge)
        self.s -= W

        e_add_end = datetime.now()

        ms = timedelta(microseconds=1)
        self.metrics['edge_op'].append('add')
        self.metrics['edge_op_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['num_candidate_subgraphs'].append(len(subgraph_candidates))
        self.metrics['num_processed_subgraphs'].append(I)
        self.metrics['reservoir_full_bool'].append(int(self.reservoir.is_full()))

        return True


    def remove_edge(self, edge):
        if edge not in self.graph:
            return False

        e_del_start = datetime.now()

        self.graph.remove_edge(edge)

        u = edge.get_u()
        v = edge.get_v()

        # find all nodesets representing subgraphs that will
        # no longer be connected after the removal of this edge
        removals = self.get_new_subgraphs(u, v)
        D = len(removals)

        # we start compensating for subgraph deletions with variables c1 and c2
        # after the reservoir has filled up once
        compensate_for_removals = self.reservoir.is_full() or self.d > 0
        removals_from_sample = 0

        # find all subgraphs in the reservoir containing nodes u and v
        for old_subg in self.reservoir.get_common_subgraphs(u, v):

            if frozenset(old_subg.nodes) in removals:
                # subgraph is no longer connected after edge removal, remove it
                removals_from_sample += int(self.process_old_subgraph(old_subg))
            else:
                # subgraph stays connected after edge removal, replace it
                old_edges = old_subg.edges
                edges = [e for e in old_edges if e != make_subgraph_edge(edge)]
                new_subg = make_subgraph(old_subg.nodes, edges)
                self.process_existing_subgraph(old_subg, new_subg)

        if compensate_for_removals:
            # update the counts of uncompensated deletions
            self.c1 += removals_from_sample
            self.c2 += D - removals_from_sample

        self.N -= D

        e_del_end = datetime.now()

        ms = timedelta(microseconds=1)
        self.metrics['edge_op'].append('del')
        self.metrics['edge_op_ms'].append((e_del_end - e_del_start) / ms)
        self.metrics['num_candidate_subgraphs'].append(D)
        self.metrics['num_processed_subgraphs'].append(removals_from_sample)
        self.metrics['reservoir_full_bool'].append(int(self.reservoir.is_full()))

        return True


    def process_new_subgraph(self, subgraph):
        success, old_subgraph = self.reservoir.add(subgraph)

        if success: self.add_subgraph(subgraph)
        if old_subgraph: self.remove_subgraph(old_subgraph)

        return success

    def process_old_subgraph(self, subgraph):
        return self.reservoir.remove(subgraph)
