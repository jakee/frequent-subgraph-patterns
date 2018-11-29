from itertools import combinations, product
from collections import deque

from .util import make_edge

class SimpleGraph:
    adjacency_matrix = None
    edge_labels = None


    def __init__(self):
        self.adjacency_matrix = {}
        self.edge_labels = {}


    def __contains__(self, edge):
        return (edge.u, edge.v) in self.edge_labels


    def add_neighbor(self, U, V):
        if U not in self.adjacency_matrix:
            self.adjacency_matrix[U] = set()

        if V not in self.adjacency_matrix:
            self.adjacency_matrix[V] = set()

        self.adjacency_matrix[U].add(V)
        self.adjacency_matrix[V].add(U)


    def add_edge_label(self, edge):
        self.edge_labels[(edge.u, edge.v)] = edge.label


    def add_edge(self, edge):
        U = edge.get_u()
        V = edge.get_v()

        self.add_neighbor(U, V)
        self.add_edge_label(edge)


    def neighbors(self, node):
        if node in self.adjacency_matrix:
            return self.adjacency_matrix[node]

        return set()


    def n_hop_neighborhood(self, source, n):
        if n > 0:
            '''
            # First, BFS to label the neighborhood of the node
            # based on the number of hops it takes to
            # reach the source

            bfs_stack = deque([(source, 0)])
            distances = {}

            while len(bfs_stack) > 0:
                u, dist = bfs_stack.popleft()

                if u not in distances:
                    distances[u] = dist

                if dist < n:
                    for v in self.neighbors(u):
                        if v not in distances:
                            bfs_stack.append((v, dist + 1))

            while len(stack) > 0:
                u, hops = stack.pop()

                if n + 1 > len(hops):
                    for v in self.neighbors(u):
                        if v not in hops:
                            stack.append((v, hops | set([v])))
                else:
                    # nth hop reached, commit the neighborhood
                    neighborhoods.add(frozenset(hops))
            '''

            # Then, DFS to enumerate all [1...n] -hop neighborhoods
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


    def get_induced_edges(self, nodes):
        print(nodes)
        edges = []

        # node pairs come out of combinations in sorted
        # order as the input iterable is in sorted order
        for U, V in combinations(sorted(nodes), 2):
            if (U[0], V[0]) in self.edge_labels:
                edges.append(make_edge(U, V, self.edge_labels[(U[0], V[0])]))

        return edges

