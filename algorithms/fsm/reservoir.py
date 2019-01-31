from abc import ABCMeta, abstractmethod

from .base import BaseAlgorithm
from sampling.subgraph_reservoir import SubgraphReservoir

class ReservoirAlgorithm(BaseAlgorithm, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, M=None, **kwargs):
        self.M = M # reservoir size
        self.N = 0 # number of subgraphs encountered
        self.reservoir = SubgraphReservoir()

        super().__init__(M=M, **kwargs)


    @abstractmethod
    def process_new_subgraph(self, subgraph):
        pass
