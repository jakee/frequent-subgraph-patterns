import random

from collections import defaultdict

class SubgraphReservoir:
    subgraphs = None
    vertex_subgraphs = None

    def __init__(self):
        self.subgraphs = set()
        self.vertex_subgraphs = defaultdict(set)


    def __contains__(self, subgraph):
        return subgraph in self.subgraphs


    def __len__(self):
        return len(self.subgraphs)


    def add(self, subgraph):
        if subgraph not in self.subgraphs:
            self.subgraphs.add(subgraph)

            for u in subgraph.nodes:
                self.vertex_subgraphs[u].add(subgraph)

            return True
        else:
            return False


    def remove(self, subgraph):
        if subgraph in self.subgraphs:
            self.subgraphs.remove(subgraph)

            for u in subgraph.nodes:
                self.vertex_subgraphs[u].remove(subgraph)

            return True
        else:
            return False


    def get_common_subgraphs(self, u, v):
        return self.vertex_subgraphs[u] & self.vertex_subgraphs[v]


    def random(self):
        return random.choice(list(self.subgraphs))
