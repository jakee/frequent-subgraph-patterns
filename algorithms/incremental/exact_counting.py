from collections import Counter

from graph.simple_graph import SimpleGraph

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label

from util.set import flatten

class IncrementalExactCountingAlgorithm:
    k = 0
    graph = None
    patterns = None

    def __init__(self, k=3):
        self.k = k
        self.graph = SimpleGraph()
        self.patterns = Counter()

    def add_edge(self, edge):
        if edge in self.graph:
            return False

        u = edge.get_u()
        v = edge.get_v()

        '''
        u_neighbor_nodes, u_neighborhood_dict = self.graph.neighborhood(u)
        v_neighbor_nodes, v_neighborhood_dict = self.graph.neighborhood(v)

        # following code is specific to k=3
        common_neighbor_nodes = u_neighbor_nodes & v_neighbor_nodes

        for n_u in (u_neighbor_nodes - common_neighbor_nodes):
            # create wedge
            u_nbr = u_neighborhood_dict[n_u]
            nodes = [u, v, n_u]
            edges = [edge, make_edge(u, n_u, u_nbr.e_label)]

            wedge = make_subgraph(nodes, edges)
            self.add_subgraph(wedge)

        for n_v in (v_neighbor_nodes - common_neighbor_nodes):
            # create wedge
            v_nbr = v_neighborhood_dict[n_v]
            nodes = [u, v, n_v]
            edges = [edge, make_edge(v, n_v, v_nbr.e_label)]

            wedge = make_subgraph(nodes, edges)
            self.add_subgraph(wedge)

        for n_b in common_neighbor_nodes:
            u_nbr = u_neighborhood_dict[n_b]
            v_nbr = v_neighborhood_dict[n_b]

            nodes = [u, v, n_b]
            edges = [make_edge(u, n_b, u_nbr.e_label), make_edge(v, n_b, v_nbr.e_label)]

            # remove the pre-existing wedge triplet from subgraphs
            wedge = make_subgraph(nodes, edges)
            self.remove_subgraph(wedge)

            # add the triangles to the subgraph
            triangle = make_subgraph(nodes, edges + [edge])
            self.add_subgraph(triangle)
        '''

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

        return True

    def add_subgraph(self, subgraph):
        self.patterns.update([canonical_label(subgraph)])


    def remove_subgraph(self, subgraph):
        self.patterns.subtract([canonical_label(subgraph)])