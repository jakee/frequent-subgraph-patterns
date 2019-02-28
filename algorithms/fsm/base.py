from functools import partial
from abc import ABCMeta, abstractmethod
from collections import Counter, defaultdict

from graph.simple_graph import SimpleGraph

from subgraph.pattern import canonical_label

from algorithms.exploration.util import (
    new_subgraphs_func,
    all_subgraphs_func)

class BaseAlgorithm(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, k=None, **kwargs):
        self.k = k

        self.graph = SimpleGraph()

        self.metrics = defaultdict(list)
        self.patterns = Counter()

        self.get_new_subgraphs = partial(new_subgraphs_func(k), self.graph, k)
        self.get_all_subgraphs = partial(all_subgraphs_func(k), self.graph, k)


    @abstractmethod
    def add_edge(self, edge):
        pass


    @abstractmethod
    def remove_edge(self, edge):
        pass


    def add_subgraph(self, subgraph):
        self.patterns[canonical_label(subgraph)] += 1


    def remove_subgraph(self, subgraph):
        self.patterns[canonical_label(subgraph)] -= 1
