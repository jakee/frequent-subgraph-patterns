import os
import csv
import time
import uuid

import numpy as np

from collections import defaultdict
from argparse import ArgumentParser, FileType

from graph.util import make_edge

from algorithms.fsm.incremental.exact_counting import IncrementalExactCountingAlgorithm
from algorithms.fsm.incremental.naive_reservoir import IncrementalNaiveReservoirAlgorithm
from algorithms.fsm.incremental.optimized_reservoir import IncerementalOptimizedReservoirAlgorithm

ALGORITHMS = {

    'incremental': {
        'exact': IncrementalExactCountingAlgorithm,
        'naive': IncrementalNaiveReservoirAlgorithm,
        'optimal': IncerementalOptimizedReservoirAlgorithm
    },

    'dynamic': {
        'exact': None,
        'naive': None,
        'optimal': None
    }

}

def run_simulation(simulator, edges):
    np.random.shuffle(edges)

    start_time = time.time()

    for edge in edges:
        simulator.add_edge(edge)

    end_time = time.time()

    return end_time - start_time


def main():
    parser = ArgumentParser(description="Run FSM on an evolving graph.")

    parser.add_argument("k",
        type=int,
        help="size of subgraphs (k-nodes) being mined")

    parser.add_argument('stream_setting',
        choices=['incremental', 'dynamic'],
        help="choose between incremental or fully dynamic stream setting")

    parser.add_argument('algorithm',
        choices=['exact', 'naive', 'optimal'],
        help="choose exact counting, or naive or optimised reservoir sampling")

    parser.add_argument('edge_file',
        type=FileType('r'),
        help="path to the input graph edge file")

    parser.add_argument('output_dir',
        help="path to the directory for output files")

    parser.add_argument('-m',
        dest='M',
        type=int,
        help="reservoir size required for naive and optimal algorithms")

    parser.add_argument('-t', '--times',
        type=int,
        default=10,
        help="number of times the simulation is run in this instance")

    args = vars(parser.parse_args())

    k = args['k']
    algo = args['algorithm']
    stream = args['stream_setting']
    M = args['M']
    times = args['times']

    in_file = args['edge_file']
    output_dir = args['output_dir']

    print("Running Frequent Subgraph Mining on an Evolving Graph", "\n")

    print("PARAMETERS")
    print("stream setting:", stream)
    print("algorithm:     ", algo)
    print("k:             ", k)
    print("M:             ", M)
    print("times:         ", times)
    print("input graph:   ", in_file.name, "\n")


    Algorithm = ALGORITHMS[stream][algo]

    if (algo in ['naive', 'optimal']) and (M == None):
        msg = "the reservoir size must be defined for %s algorithm" % (algo)
        raise ValueError(msg)

    if Algorithm == None:
        msg = "%s algorithm is not available for %s stream setting" % (algo, stream)
        raise NotImplementedError(msg)


    # read the input graph from the edge file
    with in_file as edge_file:
        edge_reader = csv.reader(edge_file, delimiter=' ')
        edges = [make_edge(*tuple(int(x) for x in row)) for row in edge_reader]


    # run simulations and collect the duration and metrics from each run
    durations = []
    run_metrics = defaultdict(list)
    run_patterns = []

    print("SIMULATIONS", "\n")

    for i in range(times):
        print("Running simulation", i + 1, "...")

        simulator = Algorithm(k=k, M=M)
        duration = run_simulation(simulator, edges)

        print("Done, run took", duration, "seconds.", "\n")

        durations.append(duration)
        for name, values in simulator.metrics.items():
            run_metrics[name].append(values)

        run_patterns.append(+simulator.patterns)

    avg_duration = np.mean(durations)

    patterns = run_patterns[-1]

    print("Average duration of a run was", avg_duration, "seconds.")
    print("Last run detected", len(patterns.keys()), "different subgraph patterns.")
    print("Last run detected", sum(patterns.values()), "different subgraphs.", "\n")


    # calculate means for each metric
    for name in run_metrics.keys():
        run_metrics[name] = np.mean(np.asarray(run_metrics[name]), axis=0)


    # construct the output files for collected metrics and patterns
    print ("OUTPUT")

    identifier = uuid.uuid4()

    metrics_path = os.path.join(output_dir, "%s_metrics.csv" % (identifier))
    metrics_headers = sorted(run_metrics.keys())

    with open(metrics_path, 'w', encoding='utf-8') as metrics_file:
        metrics_writer = csv.writer(metrics_file, delimiter=' ')

        metrics_writer.writerow(metrics_headers)

        for row_values in zip(*[run_metrics[name] for name in metrics_headers]):
            metrics_writer.writerow([float(x) for x in row_values])

        print("metrics file: ", metrics_file.name)


    patterns_path = os.path.join(output_dir, "%s_patterns.csv" % (identifier))
    patterns_headers = ["canonical_label"] + ["count_%d" % (i + 1) for i in range(times)]

    canonical_labels = set.union(*(set(p) for p in run_patterns))

    with open(patterns_path, 'w', encoding='utf-8') as patterns_file:
        patterns_writer = csv.writer(patterns_file, delimiter=' ')

        patterns_writer.writerow(patterns_headers)

        for c_label in canonical_labels:
            counts = [p[c_label] for p in run_patterns]
            patterns_writer.writerow([c_label, *counts])

        print("patterns file:", patterns_file.name)


if __name__ == '__main__':
    main()
