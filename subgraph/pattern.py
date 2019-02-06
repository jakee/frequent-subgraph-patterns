import numpy as np

from itertools import permutations
from collections import Counter, defaultdict


def canonical_label(graphlet):
    nodes, edges = graphlet

    edge_labels = {}
    degrees = Counter()

    for u, v, label in edges:
        edge_labels[(u, v)] = label
        degrees.update([u, v])

    # group nodes into initial partitions based with same degree and label
    parts = defaultdict(list)
    vertex_labels = {}

    for vertex, label in nodes:
        vertex_labels[vertex] = label
        degree = degrees[vertex]
        parts[(degree, label)].append(vertex)

    # sort partitions by degree, size, label in descending order
    initial = sorted(((p[0], len(parts[p]), p[1]) for p in parts), reverse=True)

    # initialize the vertex array
    vertices = np.array([u for d, _, l in initial for u in parts[(d, l)]])

    # initialize the adjacency matrix based on vertex array
    adj = np.zeros((len(nodes), len(nodes)), dtype=int)

    for i in range(len(vertices)):
        u = vertices[i]

        for j in range(len(vertices)):
            v = vertices[j]

            if (u, v) in edge_labels:
                adj[i][j] = edge_labels[(u, v)]

            if (v, u) in edge_labels:
                adj[i][j] = edge_labels[(v, u)]

    start = 0
    end = 0

    for degree, size, label in initial:

        # if partition size is only one node, we can ignore it

        # if partition contains more than one node,
        # permutate until largest canonical label is found

        if size > 1:
            end = start + size

            indices = list(range(start, end))

            A_max = None
            V_max = None
            c_max = ''

            for perm in permutations(indices):
                perm = list(perm)

                V = vertices.copy()
                A = adj.copy()

                # modify copied vertex list to reflect current permutation
                V[indices] = V[perm]

                # swap the rows and columns in copied adjacency matrix
                # to reflect current permutation
                A[indices, :] = A[perm, :]
                A[:, indices] = A[:, perm]

                candidate_label = _make_canonical_label(V, A, vertex_labels)

                if candidate_label > c_max:
                    c_max = candidate_label
                    V_max = V
                    A_max = A

            # update adjacency matrix and vertex list to represent the
            # permutation of this partition with the largest canonical label
            adj = A_max
            vertices = V_max

        start += size

    return _make_canonical_label(vertices, adj, vertex_labels)


def _make_canonical_label(vertices, adjacency_matrix, vertex_labels):
    v_labels = [vertex_labels[u] for u in vertices]
    e_labels = list(adjacency_matrix[np.tril_indices(len(vertices), k=-1)])
    return ''.join([str(x) for x in (v_labels + e_labels)])
