from datetime import datetime, timedelta

from ..incremental.exact_counting import IncrementalExactCountingAlgorithm

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label


class DynamicExactCountingAlgorithm(IncrementalExactCountingAlgorithm):


    def __init__(self, k=3, **kwargs):
        super().__init__(k=k)


    def remove_edge(self, edge):
        if edge not in self.graph:
            return False

        self.graph.remove_edge(edge)

        e_add_start = datetime.now()

        u = edge.get_u()
        v = edge.get_v()

        removals, replacements = self.get_all_subgraphs(u, v)

        for nodes in removals:
            # collect the induced subgraph after removal of edge
            # remove the subgraph with the removed edge included
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges + [edge])
            self.remove_subgraph(subgraph)

        for nodes in replacements:
            # collect the induced subgraph before removal of edge
            # remove that subgraph
            # update the subgraph by not including the removed edge
            # add the updated subgraph
            edges = self.graph.get_induced_edges(nodes)

            existing_subgraph = make_subgraph(nodes, edges + [edge])
            self.remove_subgraph(existing_subgraph)

            updated_subgraph = make_subgraph(nodes, edges)
            self.add_subgraph(updated_subgraph)

        e_add_end = datetime.now()
        ms = timedelta(microseconds=1)
        self.metrics['edge_remove_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['removed_subgraph_count'].append(len(removals))

        return True
