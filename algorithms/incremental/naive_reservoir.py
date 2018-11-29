from collections import Counter

from graph.simple_graph import SimpleGraph

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label

from sampling.subgraph_reservoir import SubgraphReservoir

from util.set import flatten

class IncrementalNaiveReservoirAlgorithm:
    k = None
    M = None # reservoir size
    N = None # number of subgraphs seen
    graph = None
    patterns = None
    reservoir = None


    def __init__(self, M, k=3):
        self.k = k
        self.graph = SimpleGraph()
        self.patterns = Counter()
        self.reservoir = SubgraphReservoir()


    def add_edge(self, edge):
        if edge in self.graph:
            return False

        u = edge.get_u()
        v = edge.get_v()

        # each subgraph is either a new addition or replaces an existing subgraph
        additions = set()
        replacements = set()

        for h in range(self.k - 2 + 1):
            j = self.k - 2 - h

            u_neighborhoods = self.graph.n_hop_neighborhood(u, h)
            v_neighborhoods = self.graph.n_hop_neighborhood(v, j)

            # the common nodes in the neighborhoods
            if h < j:
                u_neighborhoods_ext = self.graph.n_hop_neighborhood(u, h + 1)
                common = flatten(u_neighborhoods_ext) & flatten(v_neighborhoods)
            else:
                common = flatten(u_neighborhoods) & flatten(v_neighborhoods)

            common -= set([u, v])

            for u_neighborhood in u_neighborhoods:
                for v_neighborhood in v_neighborhoods:
                    # only consider disjoint neighborhoods
                    # as their union will have size k
                    if u_neighborhood.isdisjoint(v_neighborhood):
                        neighborhood = frozenset(u_neighborhood | v_neighborhood)

                        if (neighborhood not in additions) and \
                           (neighborhood not in replacements):
                            # only consider neighborhoods once

                            if common.isdisjoint(neighborhood):
                                # combined neighborhoods contain no common nodes
                                # add the newly created subgraph
                                additions.add(neighborhood)
                            else:
                                # combined neighborhoods contain common nodes
                                # replace the existing subgraph
                                replacements.add(neighborhood)

        for nodes in additions:
            # collect the induced subgraph after addition of edge
            # add that subgraph
            edges = self.graph.get_induced_edges(nodes)
            subgraph = make_subgraph(nodes, edges+[edge])
            self.add_subgraph(subgraph)

        for nodes in replacements:
            # collect the induced subgraph with nodes
            # remove that subgraph
            # update the subgraph by adding edge
            # add the updated subgraph
            edges = self.graph.get_induced_edges(nodes)
            existing_subgraph = make_subgraph(nodes, edges)

            if existing_subgraph in self.reservoir:
                self.remove_subgraph_from_sample(existing_subgraph)
                self.add_subgraph_to_sample(make_subgraph(nodes, edges+[edge]))

        self.graph.add_edge(edge)

        return True


    def add_subgraph(self, subgraph):
        self.N++

        success = False

        if len(self.reservoir) < self.M:
            success = True
        elif np.random.rand() < (self.M / float(self.N)):
            success = True
            self.remove_subgraph(self.reservoir.random())

        if success:
            self.add_subgraph_to_sample(subgraph)


    def add_subgraph_to_sample(self, subgraph):
        self.reservoir.remove(subgraph)
        self.patterns.subtract([canonical_label(subgraph)])


    def remove_subgraph_from_sample(self, subgraph):
        self.reservoir.remove(subgraph)
        self.patterns.subtract([canonical_label(subgraph)])
