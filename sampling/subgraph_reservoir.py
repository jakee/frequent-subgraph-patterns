import random

class SubgraphReservoir:
    subgraphs = None
    vertex_subgraphs = None

    def __init__(self):
        self.subgraphs = set()
        self.vertex_subgraphs = {}


    def __contains__(self, subgraph):
        return subgraph in self.subgraphs


    def __len__(self):
        return len(self.subgraphs)


    def add(self, subgraph):
        if subgraph not in self.subgraphs:
            self.subgraphs.add(subgraph)

            for u in subgraph.nodes:
                self._add_vertex_subgraph(u, subgraph)

            return True
        else:
            return False


    def remove(self, subgraph):
        if subgraph in self.subgraphs:
            self.subgraphs.remove(subgraph)

            for u in subgraph.nodes:
                self._remove_vertex_subgraph(u, subgraph)

            return True
        else:
            return False


    def get_common_subgraphs(self, u, v):
        if (u in self.vertex_subgraphs) and (v in self.vertex_subgraphs):
            return self.vertex_subgraphs[u] & self.vertex_subgraphs[v]
        else:
            return set()


    def random(self):
        return random.choice(list(self.subgraphs))


    def _add_vertex_subgraph(self, vertex, subgraph):
        if vertex in self.vertex_subgraphs:
            self.vertex_subgraphs[vertex].add(subgraph)
        else:
            self.vertex_subgraphs[vertex] = set([subgraph])


    def _remove_vertex_subgraph(self, vertex, subgraph):
        if vertex in self.vertex_subgraphs:
            self.vertex_subgraphs[vertex].remove(subgraph)
