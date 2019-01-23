import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

import time
from datetime import datetime, timedelta

from graph.util import make_edge

from algorithms.incremental.exact_counting import IncrementalExactCountingAlgorithm
from algorithms.incremental.naive_reservoir import IncrementalNaiveReservoirAlgorithm
from algorithms.incremental.optimized_reservoir import IncerementalOptimizedReservoirAlgorithm


def generate_labeled_graph(N, p, L, Q):
    G = nx.fast_gnp_random_graph(N, p)

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

def run_simulation(simulator, graph):
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

    addition_durations = []

    start_time = time.time()

    for i, edge in enumerate(data):
        s_dt = datetime.now()
        simulator.add_edge(edge)
        e_dt = datetime.now()

        addition_durations.append((e_dt - s_dt) / timedelta(microseconds=1))

    end_time = time.time()

    return end_time - start_time, addition_durations


def main():
    np.random.seed(42)

    k = 4

    N = 70
    p = 0.25

    L_count = 2 # vertex labels
    Q_count = 2 # edge labels

    #graph = generate_micro_labeled_graph()
    graph = generate_labeled_graph(N, p, L_count, Q_count)

    '''
    print("\nEXACT COUNTING\n")

    ec_sim_durations = []
    ec_edge_add_durations = []

    for i in range(10):
        sim = IncrementalExactCountingAlgorithm(k)
        duration, durations = run_simulation(sim, graph)

        print("The simulation ran for", duration, "seconds.")
        print("Number of different patterns in sample:", len((+sim.patterns).keys()))
        print("Number of different patterns in sample:", len(sim.patterns.keys()), "(incl. < 0 values)")
        print("Total number of subgraphs in sample:", sum((+sim.patterns).values()))
        print("Total number of subgraphs in sample:", sum(sim.patterns.values()), "(incl. < 0 values)")

        ec_sim_durations.append(duration)
        ec_edge_add_durations.append(durations)

    print("The simulations ran for on avg.", np.mean(ec_sim_durations), "seconds.")
    '''

    print("\nNAIVE RESERVOIR SAMPLING\n")

    nrs_sim_durations = []
    nrs_edge_add_durations = []

    for i in range(10):
        sim = IncrementalNaiveReservoirAlgorithm(1529, k) #324938
        duration, durations = run_simulation(sim, graph)

        print("The simulation ran for", duration, "seconds.")
        print("Number of different patterns in sample:", len((+sim.patterns).keys()))
        print("Number of different patterns in sample:", len(sim.patterns.keys()), "(incl. < 0 values)")
        print("Total number of subgraphs in sample:", sum((+sim.patterns).values()))
        print("Total number of subgraphs in sample:", sum(sim.patterns.values()), "(incl. < 0 values)")

        nrs_sim_durations.append(duration)
        nrs_edge_add_durations.append(durations)

    print("The simulations ran for on avg.", np.mean(nrs_sim_durations), "seconds.")

    print("\nOPTIMIZED RESERVOIR SAMPLING\n")

    ors_sim_durations = []
    ors_edge_add_durations = []

    for i in range(10):
        sim = IncerementalOptimizedReservoirAlgorithm(1529, k) #324938
        duration, durations = run_simulation(sim, graph)

        print("The simulation ran for", duration, "seconds.")
        print("Number of different patterns in sample:", len((+sim.patterns).keys()))
        print("Number of different patterns in sample:", len(sim.patterns.keys()), "(incl. < 0 values)")
        print("Total number of subgraphs in sample:", sum((+sim.patterns).values()))
        print("Total number of subgraphs in sample:", sum(sim.patterns.values()), "(incl. < 0 values)")

        ors_sim_durations.append(duration)
        ors_edge_add_durations.append(durations)

    print("\nThe simulations ran for on avg.", np.mean(ors_sim_durations), "seconds.")

    # output should look like this
    # k = 3: Counter({'221120': 2, '211210': 2, '211220': 1, '221121': 1})
    # k = 4: Counter({'2211112200': 2, '2112220100': 1, '2111220100': 1, '2211120020': 0})
    #print(sim.patterns)

    #node_colors = [label for u, label in graph.nodes.data('label')]
    #edge_colors = [label for u, v, label in graph.edges.data('label')]

    #nx.draw_circular(graph, node_color=node_colors, cmap=plt.get_cmap('Dark2'), edge_color=edge_colors, edge_cmap=plt.get_cmap('Set1'), with_labels=True)
    #plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111)

    #ax.plot(np.arange(len(ec_edge_add_durations[0])), np.mean(np.asarray(ec_edge_add_durations), axis=0))
    ax.plot(np.arange(len(nrs_edge_add_durations[0])), np.mean(np.asarray(nrs_edge_add_durations), axis=0))
    ax.plot(np.arange(len(nrs_edge_add_durations[0])), np.mean(np.asarray(ors_edge_add_durations), axis=0))

    plt.show()


if __name__ == '__main__':
    main()
