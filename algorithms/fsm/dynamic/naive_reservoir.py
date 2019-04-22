import random

from datetime import datetime, timedelta

from ..reservoir import ReservoirAlgorithm

from subgraph.util import make_subgraph, make_subgraph_edge
from subgraph.pattern import canonical_label


class DynamicNaiveReservoirAlgorithm(ReservoirAlgorithm):

    def __init__(self, k=3, M=1000):
        super().__init__(k=k, M=M)

        # the count of uncompensated deletions, where
        self.c1 = 0 # i) the deleted element was in the sample, and
        self.c2 = 0 # ii) the deleted element was not in the sample


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
        self.metrics['edge_op'].append('add')
        self.metrics['edge_op_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['num_candidate_subgraphs'].append(len(additions))
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
        compensate_for_removals = self.reservoir.is_full() or (self.c1 + self.c2) > 0
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

        # update the count of uncompensated deletions from outside the sample
        if compensate_for_removals:
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
        success = False
        do_sampling = False

        if self.c1 + self.c2 == 0:
            # there are no uncompensated deletions,
            # so we can do normal reservoir sampling
            do_sampling = True
        else:
            # there are uncompensated deletions,
            # add subgraph to reservoir with probability c1 / (c1 + c2)
            if random.random() < self.c1 / float(self.c1 + self.c2):
                self.c1 -= 1
                do_sampling = True
            else:
                self.c2 -= 1

        if do_sampling:
            success, old_subgraph = self.reservoir.add(subgraph, N=self.N)
            if success: self.add_subgraph(subgraph)
            if old_subgraph: self.remove_subgraph(old_subgraph)

        return success


    def process_old_subgraph(self, subgraph):
        return self.reservoir.remove(subgraph)
