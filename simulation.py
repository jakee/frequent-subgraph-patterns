import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

import time

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

        data.append(make_edge(u, u_label, v, v_label, edge_label))

    np.random.shuffle(data)

    start_time = time.time()

    for i, edge in enumerate(data):
        simulator.add_edge(edge)

    end_time = time.time()

    return end_time - start_time


def main():
    np.random.seed(42)

    k = 4

    N = 70
    p = 0.25

    L_count = 2 # vertex labels
    Q_count = 2 # edge labels

    #graph = generate_micro_labeled_graph()
    graph = generate_labeled_graph(N, p, L_count, Q_count)

    print("\nEXACT COUNTING\n")

    ec_sim_durations = []
    ec_edge_add_durations = []

    for i in range(10):
        sim = IncrementalExactCountingAlgorithm(k)
        duration = run_simulation(sim, graph)

        print("The simulation ran for", duration, "seconds.")
        print("Number of different patterns in sample:", len((+sim.patterns).keys()))
        print("Total number of subgraphs in sample:", sum((+sim.patterns).values()))

        ec_sim_durations.append(duration)
        ec_edge_add_durations.append(sim.metrics.extract('edge_add_ms'))

    print("The simulations ran for on avg.", np.mean(ec_sim_durations), "seconds.")


    print("\nNAIVE RESERVOIR SAMPLING\n")

    nrs_sim_durations = []
    nrs_edge_add_durations = []
    nrs_a_durations = []
    nrs_r_durations = []
    nrs_n_subgraphs = []
    nrs_i_subgraphs = []
    nrs_reservoir_full = []

    for i in range(10):
        sim = IncrementalNaiveReservoirAlgorithm(k, 1529) #324938
        duration = run_simulation(sim, graph)

        print("The simulation ran for", duration, "seconds.")
        print("Number of different patterns in sample:", len((+sim.patterns).keys()))
        print("Total number of subgraphs in sample:", sum((+sim.patterns).values()))

        nrs_sim_durations.append(duration)
        nrs_edge_add_durations.append(sim.metrics.extract('edge_add_ms'))
        nrs_a_durations.append(sim.metrics.extract('subgraph_add_ms'))
        nrs_r_durations.append(sim.metrics.extract('subgraph_replace_ms'))
        nrs_n_subgraphs.append(sim.metrics.extract('new_subgraph_count'))
        nrs_i_subgraphs.append(sim.metrics.extract('included_subgraph_count'))
        nrs_reservoir_full.append(sim.metrics.extract('reservoir_full_bool'))

    print("The simulations ran for on avg.", np.mean(nrs_sim_durations), "seconds.")


    print("\nOPTIMIZED RESERVOIR SAMPLING\n")

    ors_sim_durations = []
    ors_edge_add_durations = []
    ors_a_durations = []
    ors_r_durations = []
    ors_n_subgraphs = []
    ors_i_subgraphs = []
    ors_reservoir_full = []
    ors_skip_thresh = []

    for i in range(10):
        sim = IncerementalOptimizedReservoirAlgorithm(k, 1529) #324938
        duration = run_simulation(sim, graph)

        print("The simulation ran for", duration, "seconds.")
        print("Number of different patterns in sample:", len((+sim.patterns).keys()))
        print("Total number of subgraphs in sample:", sum((+sim.patterns).values()))

        ors_sim_durations.append(duration)
        ors_edge_add_durations.append(sim.metrics.extract('edge_add_ms'))
        ors_a_durations.append(sim.metrics.extract('subgraph_add_ms'))
        ors_r_durations.append(sim.metrics.extract('subgraph_replace_ms'))
        ors_n_subgraphs.append(sim.metrics.extract('new_subgraph_count'))
        ors_i_subgraphs.append(sim.metrics.extract('included_subgraph_count'))
        ors_reservoir_full.append(sim.metrics.extract('reservoir_full_bool'))
        ors_skip_thresh.append(sim.metrics.extract('skiprs_treshold_bool'))

    print("\nThe simulations ran for on avg.", np.mean(ors_sim_durations), "seconds.")


    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(np.arange(len(ec_edge_add_durations[0])), np.mean(np.asarray(ec_edge_add_durations), axis=0), label="ec")
    ax.plot(np.arange(len(nrs_edge_add_durations[0])), np.mean(np.asarray(nrs_edge_add_durations), axis=0), label="naive rs")
    ax.plot(np.arange(len(ors_edge_add_durations[0])), np.mean(np.asarray(ors_edge_add_durations), axis=0), label="optimized rs")
    plt.title("edge addition durations, k="+str(k))
    plt.show()


    nrs_reservoir_full_at = np.count_nonzero(np.mean(np.asarray(nrs_reservoir_full), axis=0) < 0.2)

    fig = plt.figure()
    ax = fig.add_subplot(311)

    #ax.plot(np.arange(len(ec_edge_add_durations[0])), np.mean(np.asarray(ec_edge_add_durations), axis=0))
    ax.plot(np.arange(len(nrs_edge_add_durations[0])), np.mean(np.asarray(nrs_edge_add_durations), axis=0))
    ax.axvline(nrs_reservoir_full_at, color='r', alpha=0.6)
    plt.title("edge addition duration")
    #ax.plot(np.arange(len(nrs_edge_add_durations[0])), np.mean(np.asarray(ors_edge_add_durations), axis=0))

    ax = fig.add_subplot(312)
    ax.stackplot(np.arange(len(nrs_edge_add_durations[0])), np.mean(np.asarray(nrs_a_durations), axis=0), np.mean(np.asarray(nrs_r_durations), axis=0), labels=['addition', 'replacement'])
    ax.axvline(nrs_reservoir_full_at, color='r', alpha=0.6)
    plt.title("subgraph add and replacement durations")
    plt.legend()

    ax = fig.add_subplot(313)
    ax.plot(np.arange(len(nrs_edge_add_durations[0])), np.mean(np.asarray(nrs_i_subgraphs), axis=0) / np.mean(np.asarray(nrs_n_subgraphs), axis=0))
    ax.axvline(nrs_reservoir_full_at, color='r', alpha=0.6)
    plt.title("ratio of included subgraphs")

    fig.suptitle('Incremental Stream, Naive Reservoir Sampling, k='+str(k), fontsize=16)

    plt.show()


    ors_reservoir_full_at = np.count_nonzero(np.mean(np.asarray(ors_reservoir_full), axis=0) < 0.2)
    ors_threshold_reached_at = np.count_nonzero(np.mean(np.asarray(ors_skip_thresh), axis=0) < 0.2)

    fig = plt.figure()
    ax = fig.add_subplot(311)

    ax.plot(np.arange(len(ors_edge_add_durations[0])), np.mean(np.asarray(ors_edge_add_durations), axis=0))
    ax.axvline(ors_reservoir_full_at, color='r', alpha=0.6)
    ax.axvline(ors_threshold_reached_at, color='g', alpha=0.6)
    plt.title("edge addition duration")

    ax = fig.add_subplot(312)
    ax.stackplot(np.arange(len(ors_edge_add_durations[0])), np.mean(np.asarray(ors_a_durations), axis=0), np.mean(np.asarray(ors_r_durations), axis=0), labels=['addition', 'replacement'])
    ax.axvline(ors_reservoir_full_at, color='r', alpha=0.6)
    ax.axvline(ors_threshold_reached_at, color='g', alpha=0.6)
    plt.title("subgraph add and replacement durations")
    plt.legend()

    ax = fig.add_subplot(313)
    ax.plot(np.arange(len(ors_edge_add_durations[0])), np.mean(np.asarray(ors_i_subgraphs), axis=0) / np.mean(np.asarray(ors_n_subgraphs), axis=0))
    ax.axvline(ors_reservoir_full_at, color='r', alpha=0.6)
    ax.axvline(ors_threshold_reached_at, color='g', alpha=0.6)
    plt.title("ratio of included subgraphs")

    fig.suptitle('Incremental Stream, Optimized Reservoir Sampling, k='+str(k), fontsize=16)

    plt.show()


if __name__ == '__main__':
    main()
