import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from graph.util import make_edge

from algorithms.incremental.exact_counting import IncrementalNaiveReservoirAlgorithm


def generate_labeled_graph(N, p, L, Q):
    G = nx.fast_gnp_random_graph(N, p, seed=42)

    for node in G:
        G.nodes[node]['label'] = np.random.randint(1, L+1)

    for u, v in G.edges:
        G.edges[u, v]['label'] = np.random.randint(1, Q+1)

    return G


def generate_micro_labeled_graph():
    G = nx.Graph()

    G.add_node(1, label=1)
    G.add_node(2, label=1)
    G.add_node(3, label=2)
    G.add_node(4, label=2)
    G.add_node(5, label=1)

    G.add_edge(1, 3, label=2)
    G.add_edge(2, 3, label=2)
    G.add_edge(3, 4, label=1)
    G.add_edge(3, 5, label=1)
    G.add_edge(4, 5, label=2)

    return G

def run_simulation(graph, k):
    # get list of edges
    # permutate list of edges
    # add edges one by one
    # update k-vertex subgraph frequencies after each addition

    data = []

    for u, v, edge_label in graph.edges.data('label'):
        u_label = graph.nodes[u]['label']
        v_label = graph.nodes[v]['label']

        data.append(make_edge((u, u_label), (v, v_label), edge_label))

    np.random.shuffle(data)

    simulator = IncrementalExactCountingAlgorithm(k)

    for edge in data:
        simulator.add_edge(edge)

    return simulator


def main():
    np.random.seed(42)

    N = 10
    p = 0.25

    L_count = 3 # vertex labels
    Q_count = 2 # edge labels

    graph = generate_micro_labeled_graph()
    #graph = generate_labeled_graph(N, p, L_count, Q_count)

    sim = run_simulation(graph, 4)

    # output should look like this
    # k = 3: Counter({'221120': 2, '211210': 2, '211220': 1, '221121': 1})
    # k = 4: Counter({'2211112200': 2, '2112220100': 1, '2111220100': 1, '2211120020': 0})
    print(sim.patterns)

    node_colors = [label for u, label in graph.nodes.data('label')]
    edge_colors = [label for u, v, label in graph.edges.data('label')]

    nx.draw_circular(graph, node_color=node_colors, cmap=plt.get_cmap('Dark2'), edge_color=edge_colors, edge_cmap=plt.get_cmap('Set1'), with_labels=True)
    plt.show()


if __name__ == '__main__':
    main()
