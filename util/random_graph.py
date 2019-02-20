import os
import csv

import numpy as np
import networkx as nx

from argparse import ArgumentParser


def label_graph(graph, L, Q):
    """
    Returns a copy of G with randomly labeled nodes and edges.

    Copies the networkx.Graph G and assigns each node one of the
    labels [1,...,L] and each edge one of the labels [1,...,Q]
    uniformly at random.
    """
    G = graph.copy()


    for node in G:
        G.nodes[node]['label'] = np.random.randint(1, L+1)

    for u, v in G.edges:
        G.edges[u, v]['label'] = np.random.randint(1, Q+1)

    return G


def main():
    parser = ArgumentParser(description="Generate a random labeled ER graphs.")

    parser.add_argument('N',
        type=int,
        help="number of nodes N in the graph")

    parser.add_argument('p',
        type=float,
        help="probability p that an edge exists between any two nodes")

    parser.add_argument('-l', '--nodelabels',
        dest='L',
        nargs="+",
        type=int,
        default=[2],
        help="list of node label counts L (default [2])")

    parser.add_argument('-q', '--edgelabels',
        dest='Q',
        nargs="+",
        type=int,
        default=[2],
        help="list of edge label counts Q (default [2])")

    parser.add_argument('-d', '--dest', default=".", help="destination directory")

    parser.add_argument('-n', '--name', default="ER", help="name for graph(s)")

    args = vars(parser.parse_args())

    name = args['name']
    N = args['N']
    p = args['p']
    Ls = args['L']
    Qs = args['Q']

    if len(Ls) != len(Qs):
        raise ValueError("the number of node and edge label counts does not match")

    G = nx.fast_gnp_random_graph(N, p)

    for L, Q in zip(Ls, Qs):

        graph = label_graph(G, L, Q)

        filename = "%s_N%d_p%d_L%d_Q%d_graph.edg" % (name, N, int(p * 100), L, Q)

        if args['dest']:
            filename = os.path.join(args['dest'], filename)

        with open(filename, 'w', encoding='utf-8') as f:
            edge_writer = csv.writer(f, delimiter=' ')
            for u, v, q_uv in graph.edges.data('label'):
                l_u = graph.nodes[u]['label']
                l_v = graph.nodes[v]['label']
                edge_writer.writerow([u, l_u, v, l_v, q_uv])


if __name__ == '__main__':
    main()
