import os
import csv

import numpy as np
import networkx as nx

from argparse import ArgumentParser


def generate_labeled_graph(N, p, L, Q):
    G = nx.fast_gnp_random_graph(N, p)

    for node in G:
        G.nodes[node]['label'] = np.random.randint(1, L+1)

    for u, v in G.edges:
        G.edges[u, v]['label'] = np.random.randint(1, Q+1)

    return G


def main():
    parser = ArgumentParser(description="Generate a random labeled ER graph.")

    parser.add_argument('N',
        type=int,
        help="number of nodes N in the graph")

    parser.add_argument('p',
        type=float,
        help="probability p that an edge exists between any two nodes")

    parser.add_argument('-l',
        dest='L',
        type=int,
        default=2,
        help="number of node labels L (default 2)")

    parser.add_argument('-q',
        dest='Q',
        type=int,
        default=2,
        help="number of edge labels Q (default 2)")

    parser.add_argument('-d', '--dest', default=".", help="destination directory")

    args = vars(parser.parse_args())

    N = args['N']
    p = args['p']
    L = args['L']
    Q = args['Q']

    graph = generate_labeled_graph(N, p, L, Q)

    filename = "N%d_p%d_L%d_Q%d_graph.edg" % (N, int(p * 100), L, Q)

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
