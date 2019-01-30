import os
import csv
import time

import numpy as np

from collections import defaultdict
from argparse import ArgumentParser, FileType

from graph.util import make_edge

from algorithms.incremental.exact_counting import IncrementalExactCountingAlgorithm
from algorithms.incremental.naive_reservoir import IncrementalNaiveReservoirAlgorithm
from algorithms.incremental.optimized_reservoir import IncerementalOptimizedReservoirAlgorithm

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

    for i in range(times):
        simulator = Algorithm(k, M)
        duration = run_simulation(simulator, edges)

        durations.append(duration)
        for name, values in simulator.metrics.items():
            run_metrics[name].append(values)


    # calculate avg run duration and means for each metric
    avg_duration = np.mean(durations)

    for name in run_metrics.keys():
        run_metrics[name] = np.mean(np.asarray(run_metrics[name]), axis=0)


    # construct and write the csv file to output the collect metrics
    out_file_path = os.path.join(output_dir, 'out.csv')
    out_headers = sorted(run_metrics.keys())

    with open(out_file_path, 'w', encoding='utf-8') as out_file:
        out_writer = csv.writer(out_file, delimiter=' ')

        out_writer.writerow(out_headers)

        for row_values in zip(*[run_metrics[name] for name in out_headers]):
            out_writer.writerow([float(x) for x in row_values])


if __name__ == '__main__':
    main()
