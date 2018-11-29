import numpy as np

from itertools import permutations
from collections import Counter


def canonical_label(graphlet):
    nodes, edges = graphlet

    edge_labels = {}
    degrees = Counter()

    for edge in edges:
        u, v, label = edge
        edge_labels[(u, v)] = label
        degrees.update([u, v])

    nodes_by_dl = {}
    vertex_labels = {}

    for node in nodes:
        vertex, label = node
        vertex_labels[vertex] = label

        degree = degrees[vertex]

        if (degree, label) not in nodes_by_dl:
            nodes_by_dl[(degree, label)] = []

        nodes_by_dl[(degree, label)].append(node)

    initial_setup = sorted([(d, len(ns), l) for (d, l), ns in nodes_by_dl.items()], reverse=True)

    # initialize the vertex array and adjacency matrix
    vertices = []
    adj = np.zeros((len(nodes), len(nodes)), dtype=int)

    # populate the vertex array
    for degree, size, label in initial_setup:
        vertices += [ u for u, l in nodes_by_dl[(degree, label)]]

    vertices = np.array(vertices)

    # populate the adjacency matrix
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

    for degree, size, label in initial_setup:
        # if partition size is only one node
        # we can simply ignore it
        if size > 1:
            # if partition contains more than one node,
            # permutate until largest canonical label is found
            end = start + size

            indices = list(range(start, end))

            A_max = None
            V_max = None
            c_max = ''

            for perm in permutations(indices):
                perm = list(perm)

                V = vertices.copy()
                A = adj.copy()

                # swap the vertices around in the copy of the
                # vertex list
                V[indices] = V[perm]

                # swap the rows and columns in the copy of the
                # adjacency matrix
                A[indices, :] = A[perm, :]
                A[:, indices] = A[:, perm]

                candidate_label = _make_canonical_label(V, A, vertex_labels)

                if candidate_label > c_max:
                    c_max = candidate_label
                    V_max = V
                    A_max = A

                adj = A_max
                vertices = V_max

        start += size

    return _make_canonical_label(vertices, adj, vertex_labels)


def _make_canonical_label(vertices, adjacency_matrix, vertex_labels):
    v_labels = [vertex_labels[u] for u in vertices]
    e_labels = list(adjacency_matrix[np.tril_indices(len(vertices), k=-1)])
    return ''.join([str(x) for x in (v_labels + e_labels)])
