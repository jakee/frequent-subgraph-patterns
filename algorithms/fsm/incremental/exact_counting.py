from datetime import datetime, timedelta

from ..base import BaseAlgorithm

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label


class IncrementalExactCountingAlgorithm(BaseAlgorithm):


    def __init__(self, k=3, **kwargs):
        super().__init__(k=k)


    def add_edge(self, edge):
        if edge in self.graph:
            return False

        e_add_start = datetime.now()

        u = edge.get_u()
        v = edge.get_v()

        additions, replacements = self.get_all_subgraphs(u, v)

        for nodes in additions:
            # collect the induced subgraph after addition of edge
            # add that subgraph
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges + [edge])
            self.add_subgraph(subgraph)

        for nodes in replacements:
            # collect the induced subgraph with nodes
            # remove that subgraph
            # update the subgraph by adding edge
            # add the updated subgraph
            edges = self.graph.get_induced_edges(nodes)

            existing_subgraph = make_subgraph(nodes, edges)
            self.remove_subgraph(existing_subgraph)

            updated_subgraph = make_subgraph(nodes, edges + [edge])
            self.add_subgraph(updated_subgraph)

        self.graph.add_edge(edge)

        e_add_end = datetime.now()
        ms = timedelta(microseconds=1)
        self.metrics['edge_op'].append('add')
        self.metrics['edge_op_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['num_processed_subgraphs'].append(len(additions))

        return True


    def remove_edge(self, edge):
        pass
