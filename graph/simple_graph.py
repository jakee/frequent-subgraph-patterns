from itertools import combinations, product
from collections import defaultdict

from graph.util import make_edge

from util.set import flatten

class SimpleGraph:
    adjacency_matrix = None
    edge_labels = None


    def __init__(self):
        self.adjacency_matrix = defaultdict(set)
        self.edge_labels = {}


    def __contains__(self, edge):
        return (edge.u, edge.v) in self.edge_labels


    def add_edge(self, edge):
        """Add an edge to the graph."""
        self._add_neighbor(edge.get_u(), edge.get_v())
        self._add_edge_label(edge)


    def remove_edge(self, edge):
        """Remova an edge from the graph."""
        self._remove_neighbor(edge.get_u(), edge.get_v())
        self._remove_edge_label(edge)


    def _add_neighbor(self, U, V):
        """Add U and V as neighbors to the adjacency matrix."""
        self.adjacency_matrix[U].add(V)
        self.adjacency_matrix[V].add(U)


    def _remove_neighbor(self, U, V):
        """Remove neighbor relationship of U and V from the adjacency matrix."""
        self.adjacency_matrix[U].remove(V)
        self.adjacency_matrix[V].remove(U)


    def _add_edge_label(self, edge):
        """Store the label corresponding to this edge."""
        self.edge_labels[(edge.u, edge.v)] = edge.label


    def _remove_edge_label(self, edge):
        """Forget the label corresponding to this edge."""
        del self.edge_labels[(edge.u, edge.v)]


    def neighbors(self, node):
        """Retrieve all neighbors of a node."""
        if node in self.adjacency_matrix:
            return self.adjacency_matrix[node]

        return set()


    def n_hop_neighborhood(self, source, n):
        """Enumerate all n-hop neighborhoods originating from source node."""

        if n > 0:
            # DFS to enumerate obvious [1...n] -hop neighborhoods
            stack = [(source, set([source]))]
            m_hop_neighborhoods = {k: set() for k in range(1, n + 1)}

            while len(stack) > 0:
                u, hops = stack.pop()

                m = len(hops) - 1

                if m > 0:
                    # mth hop reached, commit the neighborhood
                    m_hop_neighborhoods[m].add(frozenset(hops))

                if n > m:
                    for v in self.neighbors(u):
                        if v not in hops:
                            stack.append((v, hops | set([v])))

            # go through the [1..n] -hop neighborhoods to find all
            # combinations of n hop neighborhoods
            for k in range(1, n):
                k_hop_hoods = m_hop_neighborhoods[k]
                one_hop_hoods = m_hop_neighborhoods[1]

                for N_k, N_1 in product(k_hop_hoods, one_hop_hoods):
                    N_k_plus_1 = N_k | N_1

                    if len(N_k_plus_1) == k + 2:
                        # this combination resulted in a candidate
                        # k + 2 node subgraph neighborhood
                        m_hop_neighborhoods[k+1].add(N_k_plus_1)

            return m_hop_neighborhoods[n]

        else:

            return set([frozenset([source])])


    def two_hop_neighborhood(self, source, through_nodes=None, exclude_nodes=set()):
        """Enumerate all 2-hop neighborhoods originating from source node."""
        one_hop_nodes = self.neighbors(source)
        exclude_nodes = exclude_nodes | one_hop_nodes | set([source])

        if through_nodes != None:
            one_hop_nodes = one_hop_nodes & through_nodes

        two_hop_dict = {}

        for v in one_hop_nodes:
            nbrs = self.neighbors(v)
            for s in nbrs - exclude_nodes:
                if s not in two_hop_dict:
                    two_hop_dict[s] = set()
                two_hop_dict[s].add(v)

        return two_hop_dict


    def get_induced_edges(self, nodes):
        """Retrieve the set of edges induced by a set of nodes."""
        edges = []

        # node pairs come out of combinations in sorted
        # order as the input iterable is in sorted order
        for (u, l_u), (v, l_v) in combinations(sorted(nodes), 2):
            q_uv = self.edge_labels.get((u, v))
            if q_uv != None:
                edges.append(make_edge(u, l_u, v, l_v, q_uv))

        return edges

