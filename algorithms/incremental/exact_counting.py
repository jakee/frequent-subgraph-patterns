from collections import Counter, defaultdict

from datetime import datetime, timedelta

from graph.simple_graph import SimpleGraph

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label

from util.set import flatten

from algorithms.exploration.optimized_quadruplet import addition_explore

class IncrementalExactCountingAlgorithm:
    k = 0
    graph = None
    patterns = None
    metrics = None


    def __init__(self, k, *args):
        # we use *args in order to make this class
        # interchangeable with other Algorithms
        # that take more arguments than just k
        self.k = k
        self.graph = SimpleGraph()
        self.patterns = Counter()
        self.metrics = defaultdict(list)


    def add_edge(self, edge):
        if edge in self.graph:
            return False

        e_add_start = datetime.now()

        u = edge.get_u()
        v = edge.get_v()

        additions, replacements = addition_explore(self.graph, u, v, self.k)

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
        self.metrics['edge_add_ms'].append((e_add_end - e_add_start) / ms)
        self.metrics['new_subgraph_count'].append(len(additions))

        return True


    def add_subgraph(self, subgraph):
        self.patterns.update([canonical_label(subgraph)])


    def remove_subgraph(self, subgraph):
        self.patterns.subtract([canonical_label(subgraph)])
