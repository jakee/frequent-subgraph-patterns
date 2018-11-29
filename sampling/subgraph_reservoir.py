import numpy as np

class SubgraphReservoir:
    subgraphs = None

    def __init__(self):
        subgraphs = set()


    def __contains__(self, subgraph):
        return subgraph in self.subgraphs


    def __len__(self):
        return len(subgraphs)


    def add(self, subgraph):
        subgraphs.add(subgraph)


    def remove(self, subgraph):
        subgraphs.remove(subgraph)


    def random(self):
        return np.random.choice(list(subgraphs))
