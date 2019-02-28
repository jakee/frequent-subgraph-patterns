from abc import ABCMeta, abstractmethod

from .base import BaseAlgorithm
from sampling.subgraph_reservoir import SubgraphReservoir

class ReservoirAlgorithm(BaseAlgorithm, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, M=None, **kwargs):
        self.M = M # reservoir size
        self.N = 0 # number of subgraphs encountered
        self.reservoir = SubgraphReservoir(size=M)

        super().__init__(M=M, **kwargs)


    @abstractmethod
    def process_new_subgraph(self, subgraph):
        pass


    @abstractmethod
    def process_old_subgraph(self, subgraph):
        pass


    def process_existing_subgraph(self, old_subgraph, new_subgraph):
        self.reservoir.replace(old_subgraph, new_subgraph)
        self.remove_subgraph(old_subgraph)
        self.add_subgraph(new_subgraph)
