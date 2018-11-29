import numpy as np

from itertools import combinations, product

from subgraph.util import make_subgraph
from subgraph.pattern import canonical_label
from subgraph.subgraph import SubgraphEdge

# determines from edges wether a subgraph is connected based
def _is_connected(edges):
    components = []

    for u, v in edges:
        found = False

        for C in components:
            if u in C or v in C:
                found = True
                C.update([u, v])

        if not found:
            components.append(set([u, v]))

    return len(set.intersection(*components)) > 0


# extremely naive method for calculating T_k values for different
# graphs based on k, L and Q
# k = size of subgraph pattern
# L = number of different vertex labels
# Q = number of different edge labels
def calculate_T_k(k, L, Q):
    min_edges = k - 1
    max_edges = sum(range(1, k))

    potential_edges = list(combinations(range(k), 2))

    possible_patterns = set()

    for vertex_labels in product(range(1, L+1), repeat=k):
        nodes = list(enumerate(vertex_labels))

        for num_edges in range(min_edges, max_edges + 1):

            for edges in combinations(potential_edges, num_edges):
                edges = list(edges)
                if _is_connected(edges):

                    for edge_labels in product(range(1,Q+1), repeat=num_edges):
                        subgraph = make_subgraph(nodes, [SubgraphEdge(u, v, l) for (u, v), l in zip(edges, edge_labels)])
                        possible_patterns.add(canonical_label(subgraph))

    return len(possible_patterns)


# calculate a (ε, δ)-approximation for the size of a reservoir used
# to maintain a uniform sample of k-subgraphs in an evolving graph
def calculate_M(T_k, delta, epsilon):
    return np.ceil(np.log(T_k/delta) * ((4 + epsilon)/np.power(epsilon, 2)))

